import numpy as np
import csv
from operator import itemgetter
import cPickle
import os,sys
import ntpath
import operator
from osgeo import ogr,gdal
from __builtin__ import False


ogr.UseExceptions()

class BioGeo():
   
   def __init__(self, contrastsdLoc, intersectionLyrDLoc, EventField=False):
      """
      @summary: contructor for all biogeo encoding
      @note: EventField only for non-collections
      """
      self.contrastColl = False  # list of ogr data sources
      self.eventField = EventField
      fieldName = sPSet = commonSet = True 
      try: 
         if os.path.exists(contrastsdLoc) and os.path.exists(intersectionLyrDLoc) and EventField:
            self.contrastsDs = self.openShapefile(contrastsdLoc) 
            fieldName = self._checkEventFieldName()
            if not fieldName:
               raise Exception, "incorrect event field"
            sPSet = self._setSinglePathValues(EventField, contrastsdLoc)
            commonSet = self._setCommon(intersectionLyrDLoc)
         else:
            raise ValueError('shapefile or EventField missing')
      except Exception, e:
         if fieldName and sPSet and commonSet:
            try:
               # this branch for multiples (collection)
               if len(contrastsdLoc) == 1 and os.path.exists(contrastsdLoc[0]):
                  raise Exception, "list_one"
               ####
               self.contrastColl = []
               for fn in contrastsdLoc:
                  if os.path.exists(fn):
                     ds = self.openShapefile(fn)
                     self.contrastColl.append(ds)
               ###      
               if not self._eachTwo():
                  self.contrastColl = False
                  raise Exception, "more then two features in .."
               if not self._checkEventFieldName():  # does a contrast collection need an EventField?
                  self.contrastColl = False
                  raise Exception, "incorrect event field"
               if os.path.exists(intersectionLyrDLoc):
                  self._setCommon(intersectionLyrDLoc)
               else:
                  self.contrastColl = False
                  raise ValueError('shapefile missing')
               
            except Exception, e: 
               try:
                  if str(e) == 'list_one':
                     if os.path.exists(intersectionLyrDLoc):  
                        self.contrastsDs = self.openShapefile(contrastsdLoc[0])
                        if not self._checkEventFieldName():
                           raise Exception, "incorrect event field"
                        self._setSinglePathValues(EventField, contrastsdLoc[0])
                        self._setCommon(intersectionLyrDLoc)
                     else:
                        raise ValueError('shapefile missing')
                  else:
                     raise Exception, str(e)  # was ValueError('unable to build collection')
               except Exception, e:
                  print str(e)
         else:
            print str(e)

# ........................................................................
   def _setMutuallyExclusive(self,ds):
      """
      @summary: determine if mutually exclusive
      @note: this might not work under certain circumstances
      """
      lyr = ds.GetLayer(0)
      fc = lyr.GetFeatureCount()
      # now call get distinct
           
# ........................................................................      
   def _setCommon(self, intersectionLyrDLoc):
      set = True
      try:
         self.intersectionDs = self.openShapefile(intersectionLyrDLoc)
         self.sortedSites = self.sortShpGridFeaturesBySiteID(self.intersectionDs.GetLayer(0))
      except:
         set = False
      return set      
# ........................................................................
   def _setSinglePathValues(self, EventField, contrastsdLoc):
      set = True
      try:
         self.contrastShpName = ntpath.basename(contrastsdLoc)
         if '.shp' in self.contrastShpName:
            self.contrastShpName = self.contrastShpName.replace('.shp','')
         
         self.distinctEvents = self.getDistinctEvents(self.contrastsDs, EventField, self.contrastShpName) 
         self._positions = self.buildContrastPostions(self.distinctEvents)
      except Exception, e:
         print "error in setSinglePath ",str(e)
         set = False
      return set
# ........................................................................

   def _checkEventFieldName(self):
      """
      @summary: check that in self.eventField exists in contrast shapes
      """
      if not self.contrastColl:
         dataSrcs = [self.contrastsDs]
      else:
         dataSrcs = self.contrastColl
      fieldExists = True
      for cShpDs in dataSrcs:
         lyr = cShpDs.GetLayer(0)
         lyrDef = lyr.GetLayerDefn()
         if lyrDef.GetFieldIndex(self.eventField) == -1:
            fieldExists = False
            break
      return fieldExists   
# ........................................................................
   
   def _eachTwo(self):
      """
      @summary: check to see if each shp file in contrast collection only has two features
      """
      eachTwo = True
      try:
         for cShpDs in self.contrastColl:
            lyr = cShpDs.GetLayer(0)
            fc = lyr.GetFeatureCount()
            if fc != 2:
               fn = cShpDs.name
               name = ntpath.basename(fn)
               raise Exception, "More than 2 features in lyr %s" % (name)
      except Exception,e:
         eachTwo = False
         print str(e)
      return eachTwo
# ........................................................................
   @property
   def positions(self):
      return self._positions
      
# ........................................................................       
   def openShapefile(self,dlocation):
   
      ogr.RegisterAll()
      drv = ogr.GetDriverByName('ESRI Shapefile')
      try:
         ds = drv.Open(dlocation)
      except Exception, e:
         raise Exception, 'Invalid datasource, %s: %s' % (dlocation, str(e))
      return ds
# ........................................................................    
   def sortShpGridFeaturesBySiteID(self,lyr):
      """
      @param lyr: osgeo lyr object
      @return: 2-D list of site features sorted by siteids [siteid,feature],[..]..
      """
      sites = []
      for feature in lyr:
         idIdx = feature.GetFieldIndex('siteid')
         siteId = feature.GetFieldAsInteger(idIdx)
         sites.append([siteId,feature])
      sortedSites = sorted(sites, key=itemgetter(0))
      return sortedSites
# ........................................................................    
   def getDistinctEvents(self,contrastLyrDS,eventFieldName,constrastShpName):
      """
      @summary: returns list of distinct event string values
      """
      distinctEvents = []
      sql = 'SELECT DISTINCT %s FROM %s' % (eventFieldName,constrastShpName)
      layer = contrastLyrDS.ExecuteSQL(sql)
      for feature in layer:
         distinctEvents.append(feature.GetField(0))
      
      return distinctEvents
# ........................................................................    
   def getContrastsData(self):
      """
      @summary: collects the (two) features for each distinct event in a merged shp 
      """
      
      distinctEvents = self.distinctEvents   
      contrastLyr = self.contrastsDs.GetLayer(0)
      contrasts = []
      for event in distinctEvents:
         filter = "%s = '%s'" % (self.eventField,event)
         contrastLyr.SetAttributeFilter(filter)
         innerList = [event]
         fc = contrastLyr.GetFeatureCount()  # if this is more than 2 throw exception and bail
         if fc != 2:
            contrasts = False
            break
         for feature in contrastLyr:
            innerList.append(feature) #.GetGeometryRef())   
         contrasts.append(innerList)
      
      return contrasts
# ........................................................................      
   def buildContrastPostions(self, distinctEvents, fromCollection=False):
      """
      @summary: build look up for contrast methods and visualization of outputs
      @todo: needs to get build for contrast collection too, which means not using distinct
      events, which makes sense since shouldn't need EventField in collection.
      """
      refD = {k:v for v,k in enumerate(distinctEvents)}
      return refD
# ........................................................................   
   def buildFromExclusive(self):
      """
      @summary: builds from one shapefile where feature is exclusive (no overlap)
      this doesn't use area, could be a problem if site intersects more then one event
      @note: TEST THIS WITH /home/jcavner/TASHI_PAM/Test!!
      @note: have to disallow this method for merged data.
      """
      
      mds = self.contrastsDs
      meConstrastLyr = mds.GetLayer(0) 
      
      gds = self.intersectionDs
      gLyr = gds.GetLayer(0)
      siteCount = gLyr.GetFeatureCount()
      sortedSites = self.sortedSites
      
      positions = self.positions
      contrastMtx = np.zeros((siteCount,len(positions)), dtype=np.int)
      
      
      for i,site in enumerate(sortedSites):
      #while siteFeature is not None:   
         siteGeom = site[1].GetGeometryRef()
         #siteGeom = siteFeature.GetGeometryRef()
         
         meConstrastLyr.ResetReading()
         contrastFeature = meConstrastLyr.GetNextFeature()
         while contrastFeature is not None:        
            eventGeom = contrastFeature.GetGeometryRef()
            
            eventNameIdx = contrastFeature.GetFieldIndex(self.eventField)
            eventName = contrastFeature.GetFieldAsString(eventNameIdx)
            
            if eventName in positions:
               colPos = positions[eventName] # columns are contrasts
               if siteGeom.Intersect(eventGeom):
                  contrastMtx[i][colPos] = 1  
               else:
                  contrastMtx[i][colPos] = -1      
            contrastFeature = meConstrastLyr.GetNextFeature()
            
         negOnes = np.where(contrastMtx[i] == -1)[0]  #site not in any event
         if len(negOnes) == len(positions):
            contrastMtx[i] = np.zeros(len(positions), dtype=np.int)
         # What if site intersects all events!! might neeed area
         # but then wouldn't work with centroids
      # TEST THIS WITH /home/jcavner/TASHI_PAM/Test!!
      return contrastMtx
           
# ........................................................................         
   def buildFromMergedShp(self):
      """
      @summary: builds from shapefile that inclues all the contrasts.
      This uses area so will only work with a shapegrid (cells)
      @todo: make so it can also centroid (X,Y)
      """
      
      contrastData = self.getContrastsData()
      if contrastData:
         eventPos =  self.positions
         
         gds = self.intersectionDs
         gLyr = gds.GetLayer(0)
         #
         numRow = gLyr.GetFeatureCount()
         numCol = len(contrastData)
         # init Contrasts mtx
         contrastsMtx = np.zeros((numRow,numCol),dtype=np.int)
         sortedSites = self.sortedSites
         #
         for contrast in contrastData:  
            event = contrast[0]
            if event in eventPos:
               colPos = eventPos[event]
               for i, site in enumerate(sortedSites):   
                  siteGeom = site[1].GetGeometryRef()
                  A1 = 0.0
                  A2 = 0.0
                  if siteGeom.Intersect(contrast[1].GetGeometryRef()):
                     intersection = siteGeom.Intersection(contrast[1].GetGeometryRef())
                     A1 = intersection.GetArea()
                     contrastsMtx[i][colPos] = -1
                  if siteGeom.Intersect(contrast[2].GetGeometryRef()):
                     if A1 > 0.0:
                        intersection = siteGeom.Intersection(contrast[2].GetGeometryRef())
                        A2 = intersection.GetArea()
                        if A2 > A1:
                           contrastsMtx[i][colPos] = 1     
                     else:
                        contrastsMtx[i][colPos] = 1
            else:
               break
      else:
         #raise Exception, "method not available for this data type"
         contrastsMtx = False
      return contrastsMtx
# ........................................................................   
   def writeBioGeoMtx(self,mtx,dLoc):
      
      wrote = True
      try:
         np.save(dLoc,mtx)
      except Exception,e:
         wrote = False
      return wrote
# ........................................................................      

class PhyloEncoding():
   
   ##############  tree  ###################
   
   def __init__(self, treeDict, PAM):
      
      self.treeDict = treeDict
      self.PAM = PAM
   
   
   # ........................................
   def makeP(self,branchLengths):
      """
      @summary: encodes phylogeny into matrix P and checks
      for sps in tree but not in PAM (I), if not in PAM, returns
      new PAM (I) in addition to P
      """
      ######### make P ###########
      tips, internal, tipsNotInMtx, lengths,tipPaths = self.buildTips()
      negsDict = self.processInternalNodes(internal)
      tipIds,internalIds = self.getIds(tips,internalDict=internal)
      #matrix = initMatrix(len(tipIds),len(internalIds))
      if branchLengths:
         sides = self.getSides(internal,lengths)
         matrix = np.zeros((len(tipIds),len(internalIds)),dtype=np.float)  # consider it's own init func
         P = self.buildP_WithBranch(matrix,sides,tips,internalIds,lengths,tipPaths)
      else:
         matrix = self.initMatrix(len(tipIds),len(internalIds))
         P = self.buildPMatrix(matrix,internalIds,tips, negsDict)
      
      if len(tipsNotInMtx) > 0:
         I = self.processTipNotInMatrix(tipsNotInMtx, internal, self.PAM)
      else:
         I = self.PAM  
      return P, I, internal
   # ........................................
      
   def buildTips(self): 
      """
      @summary: flattens to tips and return list of tip clades(dicts)
      unsure how calculations would reflect/change if more tips in tree
      than in PAM.  If it does it needs to check for matrix key
      @param noColPam: at what point does this arg get set/sent
      """ 
      clade = self.treeDict
      noColPam = self.PAM.shape[1]   
      noMx = {'c':noColPam}  # needs to start with last sps in pam
      tips = []
      tipsNotInMatrix = []
      internal = {}
      lengths = {}
      tipPaths = {}
      def buildLeaves(clade):
      
         if "children" in clade: 
            #### just a check, probably take out 
            if "length" in clade:
               lengths[int(clade["pathId"])] = float(clade["length"])
            if len(clade["children"]) > 2:
               print "polytomy ",clade["pathId"]
            ############    
            internal[clade["pathId"]] = clade["children"] # both sides
            for child in clade["children"]:  
               buildLeaves(child)
         else: 
            if "mx" in clade: 
               castClade = clade.copy()
               castClade["mx"] = int(castClade["mx"])
               tips.append(castClade)
               
            else:
               castClade = clade.copy()
               castClade['mx'] = noMx['c']  # assigns a mx starting at end of pam
               tips.append(castClade)
               tipsNotInMatrix.append(castClade)
               noMx['c'] = noMx['c'] + 1
            if "length" in clade:
               lengths[int(clade["pathId"])] = float(clade["length"]) 
            tipPaths[clade['pathId']] = clade['path']  
      buildLeaves(clade)  
      tips.sort(key=operator.itemgetter('mx'))   
      tipsNotInMatrix.sort(key=operator.itemgetter('mx'))
      return tips, internal, tipsNotInMatrix, lengths, tipPaths
   
   
   # ..........................
   def getSiblingsMx(self, clade):
      """
      @summary: gets all tips that are siblings that are in PAM, (have 'mx')
      """
      
      mx = []
      def getMtxIds(clade):
         if "children" in clade:
            for child in clade['children']:
               getMtxIds(child)
         else:
            if "mx" in clade:
               mx.append(int(clade["mx"]))
      getMtxIds(clade)
      return mx
   # ..........................
   def processTipNotInMatrix(self, tipsNotInMtx,internal,pam):
      """
      @param tipsNotInMtx: list of tip dictionaries
      @param internal: list of internal nodes made in buildTips
      """  
      
      mxMapping = {} 
      for tip in tipsNotInMtx:
         parentId = [x for x in tip["path"].split(",")][1]  
         parentsChildren = internal[parentId]#['children']  
         for sibling in parentsChildren:
            if tip['pathId'] != sibling['pathId']:
               # not itself
               if 'children' in sibling:
                  # recurse unitl it get to tips with 'mx'
                  mxs = self.getSiblingsMx(sibling)
                  mxMapping[int(tip['mx'])] = mxs
               else:
                  if "mx" in sibling:
                     mxMapping[int(tip['mx'])] = [int(sibling['mx'])]
                  else:
                     mxMapping[int(tip['mx'])] = 0
      la = [] # list of arrays              
      for k in sorted(mxMapping.keys()):
         if isinstance(mxMapping[k],list):
            
            t = np.take(pam,np.array(mxMapping[k]),axis = 1)
            b = np.any(t,axis = 1)  #returns bool logical or
         else:
            b = np.ones(pam.shape[0],dtype=np.int)
         la.append(b)
      newPam = np.append(pam,np.array(la).T,axis=1)
      return newPam
   # ...............................
   def processInternalNodes(self, internal):
      """
      @summary: takes dict of interal nodes from one side of the phylogeny
      returns dict of lists of ids that descend from parent on that branch,
      key is parent pathId
      """
      negDict = {}
      for k in internal:
         #l = negs(internal[k])  #for when one side is captured in buildTips
         l = self.negs(internal[k][0]) # for when all children are attached to internal
         negDict[str(k)] = l  # cast key to string, Dec. 10, 2015
         # since looked like conversion to json at one point wasn't converting
         # pathId 0 at root of tree to string
      return negDict
   
   # ..........................      
   def negs(self, clade):
      sL = []
      def getNegIds(clade):    
         if "children" in clade:
            sL.append(int(clade["pathId"]))
            for child in clade["children"]:
               getNegIds(child)
         else:
            sL.append(int(clade["pathId"]))
      getNegIds(clade)
      return sL
   
   # ..........................................   
   def initMatrix(self, rowCnt,colCnt):
      return np.empty((rowCnt,colCnt))
   # ..........................................
   def getIds(self, tipsDictList,internalDict=None):
      """
      @summary: get tip ids and internal ids
      """
      
      tipIds = [int(tp["pathId"]) for tp in tipsDictList ]
      if internalDict is None:
         
         total = (len(tipIds) * 2) - 1 # assumes binary tree
         allIds = [x for x in range(0,total)]
         internalIds = list(set(allIds).difference(set(tipIds)))
      else:
         internalIds = [int(k) for k in internalDict.keys()]
         internalIds.sort()
      #print "from getIDs ",len(tipIds)," ",len(internalIds)  # this is correct
      return tipIds,internalIds
      
   
   def buildPMatrix(self, emptyMtx, internalIds, tipsDictList, whichSide):
      #negs = {'0': [1,2,3,4,5,6,7], '2': [3, 4, 5], '1':[2,3,4,5,6],
      #        '3':[4],'8':[9]}
      negs = whichSide
      for ri,tip in enumerate(tipsDictList):
         newRow = np.zeros(len(internalIds),dtype=np.float)  # need these as zeros since init mtx is autofil
         pathList = [int(x) for x in tip["path"].split(",")][1:]
         tipId = tip["pathId"]
         for i,n in enumerate(pathList):
            m = 1
            #print n
            if int(tipId) in negs[str(n)]:
               m = -1
            idx = internalIds.index(n)
            newRow[idx] = (.5**i) * m
         emptyMtx[ri] = newRow  
      
      return emptyMtx  
   
   
   def getSides_0(self, internal,lengths):
      """
      has to have complete lengths
      """
      def goToTip(clade):
         
         if "children" in clade:
            lengthsfromSide[int(clade["pathId"])] = float(clade["length"])
            for child in clade["children"]:
               goToTip(child)
         else:
            # tips
            lengthsfromSide[int(clade["pathId"])] = float(clade["length"])
            #pass
      # for each key (pathId) in internal recurse each side
      sides = {}
      for pi in internal:
         sides[int(pi)] = []
         
         lengthsfromSide = {}
         goToTip(internal[pi][0])
         sides[int(pi)].append(lengthsfromSide)
         
         lengthsfromSide = {}
         goToTip(internal[pi][1])
         sides[int(pi)].append(lengthsfromSide)
      print sides
      print
      return sides
   
   def getSides(self, internal,lengths):
      """
      has to have complete lengths
      """
      def goToTip(clade):
         
         if "children" in clade:
            lengthsfromSide[int(clade["pathId"])] = float(clade["length"])
            for child in clade["children"]:
               goToTip(child)
         else:
            # tips
            lengthsfromSide[int(clade["pathId"])] = float(clade["length"])
            #pass
      # for each key (pathId) in internal recurse each side
      sides = {}
      ik = [int(k) for k in internal.keys()]  # int version of internal keys
      all_keys = list(set(lengths.keys() + ik))
      for pi in all_keys:  # 0 doesn't have a lengh so isn't in lengths
         sides[int(pi)] = []
         if str(pi) in internal:
            lengthsfromSide = {}
            goToTip(internal[str(pi)][0])
            sides[pi].append(lengthsfromSide)
         else:
            sides[pi].append({pi:lengths[pi]})
         if str(pi) in internal:
            lengthsfromSide = {}
            goToTip(internal[str(pi)][1])
            sides[pi].append(lengthsfromSide)
         else:
            sides[pi].append({pi:lengths[pi]})
      print sides
      print
      return sides
   
   
   def buildP_WithBranch(self, emptyMtx, sides, tipsDictList, internalIds, lengths, tipPaths):
      """
      @param tipsDictList: list of tip dict clades orders by key 'mx'
      @param internalIds: ordered by appearance in P
      @param tipPaths: dict by tip pathId with path for each tip
      """
      tipIds = [int(tp["pathId"]) for tp in tipsDictList] #.sort() # sorted by mx in buildTips
      # will need to order sides by using sorted(keys())
      for pi in sorted(sides.keys()):
         # one side
         if pi not in tipIds:
            posSide = sides[pi][0] # dictionary
            den = sum(posSide.values())  # some for each tip on one side
            
            tipsInSide = [k for k in posSide.keys() if k in tipIds]
            for tip in tipsInSide:
               tipPath = [int(x) for x in tipPaths[str(tip)].split(",")] # unsure of this
               idx = tipPath.index(pi)
               pathsToWorkWith = tipPath[:idx]  # this really means minus one
               
               #r = sum([ posSide[t]/len(sides[t][0]) for i,t in enumerate(pathsToWorkWith)])/den
               toSum = []
               for t in pathsToWorkWith:
                  if t not in tipIds:
                     len_tips = len([k for k in sides[t][0].keys()+sides[t][1].keys() if k in tipIds])
                  else:
                     len_tips = 1
                  #print t," & ",len_tips
                  toSum.append(posSide[t]/len_tips)
               r = sum(toSum)/den * -1
               
               emptyMtx[tipIds.index(tip)][internalIds.index(pi)] = r
               
               #print pi," ",tip," ",den," ",r
               
            ##############
            
            negSide = sides[pi][1] # dictionary
            den = sum(negSide.values())  # some for each tip on one side
            
            tipsInSide = [k for k in negSide.keys() if k in tipIds]
            for tip in tipsInSide:
               tipPath = [int(x) for x in tipPaths[str(tip)].split(",")] # unsure of this
               idx = tipPath.index(pi)
               pathsToWorkWith = tipPath[:idx]  # this really means minus one
               
               #r = sum([ negSide[t]/len(sides[t][0]) for i,t in enumerate(pathsToWorkWith)])/den
               toSum = []
               for t in pathsToWorkWith:
                  if t not in tipIds:
                     len_tips = len([k for k in sides[t][0].keys()+sides[t][1].keys() if k in tipIds])
                  else:
                     len_tips = 1
                  #print t," & ",len_tips
                  toSum.append(negSide[t]/len_tips)
               r = sum(toSum)/den 
               #print pi," ",tip," ",den," ",r
               emptyMtx[tipIds.index(tip)][internalIds.index(pi)] = r
      
      return emptyMtx

   

if __name__ == "__main__":
   
   
   #### Test BioGeo ####
   ## Contrasts shape and info
   base = "/home/jcavner/TASHI_PAM/GoodContrasts"
   shpName = "MergedContrasts_Florida.shp"
   #
   Mergeddloc = os.path.join(base,shpName)
   
   Mergeddloc = '/home/jcavner/TASHI_PAM/Test/PAIC.shp'
   
   EventField = "PAIC"
   #
   #########################
   ## Grid shape
   #
   GridDloc = "/home/jcavner/BiogeographyMtx_Inputs/Florida/TenthDegree_Grid_FL-2462.shp"
   #
   
   GridDloc = '/home/jcavner/TASHI_PAM/Test/Grid_5km.shp'
   
   myObj = BioGeo(Mergeddloc,GridDloc,EventField)
   #mtx = myObj.buildFromMergedShp()  
   #print "MTX ",mtx
   mtx = myObj.buildFromExclusive()
   print myObj.positions  # does exist for mutually exclusive
   
   #cPickle.dump(refD, open("/home/jcavner/BiogeographyMtx_Inputs/Florida/pos.pkl",'w'))
   #cPickle.dump(refD, open("/home/jcavner/pos.pkl",'w'))
   
   sP = "/home/jcavner/BiogeographyMtx_Inputs/Florida/output.npy"
   sP = "/home/jcavner/testy.npy"
   
   #if myObj.writeBioGeoMtx(mtx, sP ):
   #   print "saved mtx"
   #else:
   #   print "did not write"
   
   #   Test Multiple Shp Files
   
   #base = "/home/jcavner/BiogeographyMtx_Inputs/Florida/GoodContrasts"
   #shpList = ["GulfAtlantic.shp","MergedContrasts_Florida.shp","Pliocene.shp","ApalachicolaRiver.shp"]
   #shpList = ["/"]
   #pathList = []
   #for shp in shpList:
   #   fn = os.path.join(base,shp)
   #   pathList.append(fn)
   #   
   #testInst = BioGeo(pathList,GridDloc,"Event")
   #testInst.eachTwo()
   
   
   #################  end BioGeo  ######################## 
   #
   #
   #tree = {"name": "0",
   #     "path": "0",
   #     "pathId": "0",
   #     "children":[
   #                 {"pathId":"1","length":".4","path":"1,0",
   #                 "children":[
   #                             {"pathId":"2","length":".15","path":"9,5,0",
   #                              "children":[
   #                                          {"pathId":"3","length":".65","path":"3,2,1,0",
   #                                           
   #                                           "children":[
   #                                                       {"pathId":"4","length":".2","path":"4,3,2,1,0","mx":"0"},
   #                                                       {"pathId":"5","length":".2","path":"5,3,2,1,0","mx":"1"}
   #                                                       ]
   #                                           
   #                                           },
   #                                          
   #                                          {"pathId":"6","length":".85","path":"6,2,1,0","mx":"2"}
   #                                          
   #                                          ]
   #                              
   #                              },
   #                              {"pathId":"7","length":"1.0","path":"7,1,0","mx":"3"}
   #                             
   #                             ] },
   #                 
   #
   #                 {"pathId":"8","length":".9","path":"8,0",
   #                  "children":[{"pathId":"9","length":".5","path":"9,8,0","mx":"4"},{"pathId":"10","length":".5","path":"10,8,0","mx":"5"}] } 
   #                 ]
   #     
   #     }
   #
   #I = np.random.choice(2,24).reshape(4,6)
   #
   #treeEncodeObj = PhyloEncoding(tree,I)
   #
   #P, I, internal = treeEncodeObj.makeP(True)
   #print P
   
   