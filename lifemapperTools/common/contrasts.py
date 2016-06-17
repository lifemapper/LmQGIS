import numpy as np
import csv
from operator import itemgetter
import cPickle
import os,sys
import ntpath
from osgeo import ogr,gdal


ogr.UseExceptions()

### this came from sandbox/dev/dev/trees/buildEventContrasts, another method exists
### in sandbox/dev/dev/trees/buildBioGeographyMtx for mutually exclusive events 
class BioGeo():
   
   def __init__(self, contrasts):
      
      self.contrasts = contrasts   
   
   def openShapefile(self,dlocation):
   
      ogr.RegisterAll()
      drv = ogr.GetDriverByName('ESRI Shapefile')
      try:
         ds = drv.Open(dlocation)
      except Exception, e:
         raise Exception, 'Invalid datasource, %s: %s' % (dlocation, str(e))
      return ds
   
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
   
   def getDistinctEvents(self,contrastLyrDS,eventFieldName,constrastShpName):
      
      distinctEvents = []
      sql = 'SELECT DISTINCT %s FROM %s' % (eventFieldName,constrastShpName)
      layer = contrastLyrDS.ExecuteSQL(sql)
      for feature in layer:
         distinctEvents.append(feature.GetField(0))
      return distinctEvents
   
   def getContrastsData(self,contrastLyrDS,eventFieldName,constrastShpName):
      """
      @param contrastLyrDs: data source for contrast lyr
      """
      
      #distinctEvents = []
      #sql = 'SELECT DISTINCT %s FROM %s' % (eventFieldName,constrastShpName)
      #layer = contrastLyrDS.ExecuteSQL(sql)
      #for feature in layer:
      #   distinctEvents.append(feature.GetField(0))
      
      distinctEvents = self.getDistinctEvents(contrastLyrDS,eventFieldName,constrastShpName)
         
      contrastLyr = contrastLyrDS.GetLayer(0)
      
      # build event idx dict
      refD = {k:v for v,k in enumerate(distinctEvents) }
      
      contrasts = []
      for event in distinctEvents:
         filter = "%s = '%s'" % (eventFieldName,event)
         contrastLyr.SetAttributeFilter(filter)
         innerList = [event]
         fc = contrastLyr.GetFeatureCount()  # if this is more than 2 throw exception and bail
         for feature in contrastLyr:
            innerList.append(feature) #.GetGeometryRef())   
         contrasts.append(innerList)
      
      return contrasts,refD
      
   def buildContrastPostions(self,contrastLyrDS,eventFieldName,constrastShpName):
      
      distinctEvents = self.getDistinctEvents(contrastLyrDS,eventFieldName,constrastShpName)
      refD = {k:v for v,k in enumerate(distinctEvents)}
      return refD
   
   def buildFromExclusive(self,ContDloc,GridDloc,EventField,expDir = None,expId = None):
      """
      @param ContDLoc: file location of contrasts shapefile
      @param GridDloc: file location of shapegrid
      @param EventField: field name of contrast code in contrasts shapefile
      """
      
      mds = self.openShapefile(ContDloc)
      meConstrastLyr = mds.GetLayer(0) #PAIC_lyr
      
      gds = self.openShapefile(GridDloc)
      gLyr = gds.GetLayer(0)
      siteCount = gLyr.GetFeatureCount()
      sortedSites = self.sortShpGridFeaturesBySiteID(gLyr)
      
      PAIC_positions = self.buildContrastPostions(mds,EventField,GridDloc)
      
      contrasts = np.zeros((siteCount,len(PAIC_positions)), dtype=np.int)
      
      
      for i,site in enumerate(sortedSites):
      #while siteFeature is not None:   
         siteGeom = site[1].GetGeometryRef()
         #siteGeom = siteFeature.GetGeometryRef()
         
         meConstrastLyr.ResetReading()
         PAIC = meConstrastLyr.GetNextFeature()
         while PAIC is not None:        
            eventGeom = PAIC.GetGeometryRef()
            
            eventNameIdx = PAIC.GetFieldIndex(EventField)
            eventName = PAIC.GetFieldAsString(eventNameIdx)
            
            if eventName in PAIC_positions:
               colPos = PAIC_positions[eventName] # columns are contrasts
               if siteGeom.Intersect(eventGeom):
                  contrasts[i][colPos] = 1  
               else:
                  contrasts[i][colPos] = -1      
            PAIC = meConstrastLyr.GetNextFeature()
            
         negOnes = np.where(contrasts[i] == -1)[0]
         if len(negOnes) == len(PAIC_positions):
            contrasts[i] = np.zeros(len(PAIC_positions), dtype=np.int)
            
      if expId is not None and expDir is not None:      
         dLoc = os.path.join(expDir,"biogeog_%s.npy" % (str(expId)))   
         wrote = self.writeBioGeoMtx(contrasts, dLoc)   
         #np.save(os.path.join(base,'test.npy'),contrasts) 
         
   def buildFromMergedShp(self,ContDloc,GridDloc,EventField):
      
      mds = self.openShapefile(ContDloc)
      mergedLyr = mds.GetLayer(0)
      
      contrastShpName = ntpath.basename(ContDloc)
      if '.shp' in contrastShpName:
         contrastShpName = contrastShpName.replace('.shp','')
      else:
         # throw an exception
         pass
      
      contrastData, eventPos = self.getContrastsData(mds,EventField,contrastShpName)
      
      
      gds = self.openShapefile(GridDloc)
      gLyr = gds.GetLayer(0)
      #
      numRow = gLyr.GetFeatureCount()
      numCol = len(contrastData)
      # init Contrasts mtx
      contrastsMtx = np.zeros((numRow,numCol),dtype=np.int)
      sortedSites = self.sortShpGridFeaturesBySiteID(gLyr)
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
      
      return contrastsMtx, eventPos
   
   def writeBioGeoMtx(self,mtx,dLoc):
      
      wrote = True
      try:
         np.save(dLoc,mtx)
      except Exception,e:
         wrote = False
      return wrote
      
   

if __name__ == "__main__":
   
   # Contrasts shape and info
   base = "/home/jcavner/TASHI_PAM/GoodContrasts"
   shp = "MergedContrasts_Florida.shp"
   
   Mergeddloc = os.path.join(base,shp)
   EventField = "Event"
   ContrastField = "Contrast"
   
   ########################
   # Grid shape
   
   GridDloc = "/home/jcavner/BiogeographyMtx_Inputs/Florida/TenthDegree_Grid_FL-2462.shp"
   
   mtx, refD = buildFromMergedShp(Mergeddloc, GridDloc, EventField, ContrastField)  
   
   #cPickle.dump(refD, open("/home/jcavner/BiogeographyMtx_Inputs/Florida/pos.pkl",'w'))
   cPickle.dump(refD, open("/home/jcavner/pos.pkl",'w'))
   
   sP = "/home/jcavner/BiogeographyMtx_Inputs/Florida/output.npy"
   sP = "/home/jcavner/output.npy"
   
   if writeBioGeoMtx(mtx, sP ):
      print "saved mtx"
   else:
      print "did not write"
    