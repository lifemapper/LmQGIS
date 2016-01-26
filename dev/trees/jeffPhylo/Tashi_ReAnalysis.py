import commands
import os, sys
import csv
from osgeo import ogr


import_path = "/home/jcavner/ghWorkspace/LmQGIS.git/lifemapperTools/"
sys.path.append(os.path.join(import_path, 'LmShared'))
configPath = os.path.join(import_path, 'config', 'config.ini') 
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
#######################################
from LmClient.lmClientLib import LMClient

def buildClient(user = 'Dermot' ,pwd = 'Dermot'):
   
   client =  LMClient()
   client.login(user,pwd)
   return client

def getPreviousMask(cl,maskId,fN):
   try:
      cl.sdm.getLayerTiff(maskId,filename=fN)
   except:
      return False
   else:
      if not os.path.exists(fN):
         return False
      else:
         return True

def setMaxentParams(algObj, paramNames):
   
   for name,value in paramNames:  
      [p for p in algObj.parameters if p.name == name][0].value = value
   

def postOcc(displayName,occFilePath):
   
   try:
      print "posting occurrence set"
      occ = client.sdm.postOccurrenceSet(displayName,'shapefile',occFilePath,epsgCode=epsg)
   except Exception, e:
      print "failed to post Occ"
      print str(e)
      return False
   else:
      return occ

def postExperiment(occSetId, algoCode, mdlScen, mdlMask, prjMask, prjScen = [], algoParams = []):
   try:
      
      algObj = client.sdm.getAlgorithmFromCode(algoCode)
      setMaxentParams(algObj,algoParams)

      #for p in algObj.parameters:
      #     print p.name," ",p.value   
      exp = client.sdm.postExperiment(algObj, mdlScen, occSetId, 
                                      prjScns = prjScen, 
                                      mdlMask =  mdlMask, prjMask = prjMask)
   except Exception, e:
      print str(e)
      return False
   else:
      return exp 


def postMaskLayer(name, dloc, typeCode ,epsg):
   try:
      mask = client.sdm.postLayer(name, epsg, typeCode, 'meters', 'GTiff', fileName=dloc)
   except Exception, e:
      print str(e)
      return False
   else:
      return mask

def getFeatureCount(daShapefile):
   
   driver = ogr.GetDriverByName('ESRI Shapefile')
   dataSource = driver.Open(daShapefile, 0)
   if dataSource is None:
      print 'Could not open %s' % (daShapefile)
      return False
   else:
      layer = dataSource.GetLayer()
      featureCount = layer.GetFeatureCount()
      return featureCount

epsg = 102028
maskTypeCode = 'MASK'
climateScen = 1586

JulyMaskBasePath = "/home/jcavner/Tash_Masks_July10_2015/Tiffs" 
#### occurrences ####
occDirectory = "/home/jcavner/Tashi_2016_Reanalysis/FinalOcc/FinalOcc1_13_16/shps/reprojected/"
res = commands.getoutput('ls %s*.shp' % (occDirectory))  
occs = res.split('\n')
#######################

AllSpsRenamed = "/home/jcavner/subsettedPAIC_Masks/CSVforSpeciesThatNeedMasks/Final.csv"
MasterList = list(csv.reader(open(AllSpsRenamed,'r')))
MasksByName = {l[0]:l[2]  for l in MasterList[1:]}  # all sps with or without masks


# open all 4 model csvs, combine and add user name as a key

csvBase = "/home/jcavner/TashiCSV/"
users = [('tashitso','anamza348','tashitsoMask'), ('TashiNew_March','TashiNew_March','TashiNew_March_Mask'),
            ('TashiFourSpecies','TashiFourSpecies','TashiFourSpecies_Mask'),('TashiTestMay','TashiTestMay','TashiTestMay_Mask')]

previousMasks = {}
for user in users:
   fN = os.path.join(csvBase,user[0]+".csv")
   modelList = list(csv.reader(open(fN,'r')))
   d = {sps[0]:{'user':user,'maskId':sps[4]} for sps in modelList[1:]}
   previousMasks.update(d)
   
saveDownLoadedMask = "/home/jcavner/DownLoadedMasks_Jan2016/"

client = buildClient("Tashi_Jan2016","Tashi_Jan2016")   #main client, new user

params = [( "replicates", 5),  #5 is what we want but tested with 6,7 to make it different
          ("replicatetype", 1),
          ("extrapolate", 1),
          ("doclamp", 1),
          ("outputgrids", 1),
          ("plots", 1),
          ("maximumiterations", 500),
          ("convergencethreshold", 0.00001),
          ("adjustsampleradius", 0),
          ("defaultprevalence", .5),
          ("randomseed", 1),
          ("removeduplicates", 1),
          ("writeclampgrid", 1),
          ("writemess", 1),
          ("randomtestpoints", 0),
          ("maximumbackground", 10000),
          ("betamultiplier", 1),
          ("applythresholdrule", 4),
          ("addsamplestobackground",1),
          ("outputformat",0)]
# 
for occP in occs:
   fc = getFeatureCount(occP)
   if fc:
      if fc >= 5:
         spsName =  os.path.splitext(os.path.basename(occP))[0].replace("_AEAC","")
         #if spsName not in MasksByName:
         if MasksByName[spsName] != '':
            # means we made a new mask, so get locally and post
            #print "checking"
            mfN = os.path.join(JulyMaskBasePath,MasksByName[spsName]+'.tif')
            if not os.path.exists(os.path.join(JulyMaskBasePath,MasksByName[spsName]+'.tif')):
               print "path for mask doesn't exist ",MasksByName[spsName]
         else:
            # not local, use id from dict, retrieve, save locally and repost  
            # now just get from  saveDownLoadedMask
            mfN = os.path.join(saveDownLoadedMask,spsName+"_MASK.tif")
            if not os.path.exists(mfN):
               print "old ",spsName
               
         occ = postOcc(spsName, occP)
         if occ:
            occId = occ.id
            mask = postMaskLayer(spsName+"_MASK", mfN, "MASK", epsg)
            if mask:
               mdlMask = prjMask = mask.id
               mdlScen = climateScen
               prjScen = [] #[model["scenarioid"]]         
               exp     = postExperiment(occId, "ATT_MAXENT", 
                                        mdlScen, mdlMask, 
                                        prjMask, prjScen = prjScen, 
                                        algoParams = params)
               if not exp:
                  print "could not post exp for ",spsName
               else:
                  print "SUCCESSFULLY POSTED ",spsName
            else:
               print "could not post mask for ",spsName
            ###############################
            #  used this download masks first
            #if spsName not in previousMasks:
            #  print "not in previous ",spsName
            #else:
            #  user = previousMasks[spsName]['user'][0]
            #  pwd = previousMasks[spsName]['user'][1]
            #  maskId = int(previousMasks[spsName]['maskId'])
            #  fN = os.path.join(saveDownLoadedMask,spsName+'_MASK.tif')
            #  print user, pwd
            #  oldCl = buildClient(user, pwd)
            #  if not getPreviousMask(oldCl, maskId, fN):
            #     print "could not download ",spsName
            #  del oldCl  
         else:
            print "could not post occ for ",spsName     
   else:
      print "could not get feature count for ",occP            
               