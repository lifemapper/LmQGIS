import os, sys
import csv
import commands


#############################################
import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
sys.path.append(os.path.join(import_path, 'LmShared'))
configPath = os.path.join(import_path, 'config', 'config.ini') 
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
#######################################
from LmClient.lmClientLib import LMClient



#NewMasksPath = "/home/jcavner/subsettedPAIC_Masks/CSVforSpeciesThatNeedMasks/SpeciesList.csv"
NewMasksPath = "/home/jcavner/subsettedPAIC_Masks/CSVforSpeciesThatNeedMasks/Final.csv"

spsNeedNewMasksList = list(csv.reader(open(NewMasksPath,'r')))
# [0] -- name, [1] -- Code
NewMaskSps = {l[0]:l[2]  for l in spsNeedNewMasksList[1:] if l[2] != ''}

NotNewMasks = {l[0]:l[2]  for l in spsNeedNewMasksList[1:] if l[2] == ''}  # but should be good names?

# looks like {spsName:MaskCode,...}
# Code dictionary
NewMaskCodes = {"A":'Mindano',"B":"Luzon","C": "west_Visayan","D":"Ronblon",
                "E":"Babayans","F":"Palawan","G":"Sulu"}



#modelInfo = [{k:v  for k,v in zip(lr[0],l) } for l in lr[1:]]

# {'maskid': '6473', 'scenarioid': '1045', 'occurrencesetid': '5665122', 'name': 'Platymantis.n.sp_3', 'modelid': '1399855'}

###########################################################
def setMaxentParams(algObj, paramNames):
   
   for name,value in paramNames:  
      [p for p in algObj.parameters if p.name == name][0].value = value
   

   
def buildClient(user = 'Dermot' ,pwd = 'Dermot'):
   
   client =  LMClient()
   client.login(user,pwd)
   return client

def getOccCount(experiment = None, occSet = None):
   
   if experiment is not None:
      count = experiment.model.occurrenceSet.featureCount
   if occSet is not None:
      count = occSet.featureCount
   return count

def getOccSet(occSetId):
   
   occSet = False
   try:
      occSet = client.sdm.getOccurrenceSet(occSetId)
   except Exception, e:
      print "Exception in get Occurrence Set ",str(e)
   return occSet
      
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
      exp = None
      return exp      

def buildMask(shpPath, tifMaskPath, maskName):
   
   mask_tiff_out = os.path.join(tifMaskPath,'%s.tif' % (maskName))
   tiff_command = """gdal_rasterize -a_nodata -9999 -a code -tr 904.721138268655 904.721138268655 -l %s %s %s"""  % (maskName, shpPath, mask_tiff_out)   
   res = commands.getoutput(tiff_command)  
   
   return mask_tiff_out

def postMaskLayer(name, dloc, typeCode ,epsg):
   try:
      mask = client.sdm.postLayer(name, epsg, typeCode, 'meters', 'GTiff', fileName=dloc)
   except Exception, e:
      print str(e)
      return False
   else:
      return mask

if __name__ == "__main__":
   
   #####################################################################
   
   #typeCode = 'TashiNew_March_Mask'  #  march was made for this user, but new ones need to be
   # made for other users and taken into account in list
   epsg = 102028
   
   csvBase = "/home/jcavner/TashiCSV/"
   
   # csv's from model table
   csvList = ["tashitso.csv","TashiNew_March.csv","TashiFourSpecies.csv","TashiTestMay.csv"]
   #csvList = ["Test.csv"]
   # each of these will be used to build a list of dictionaries, like the following
   # {'maskid': '6665', 'scenarioid': '1045', 'occurrencesetid': '5683841', 'name': 'Limnonectes_cf_magnus', 'modelid': '1493091'}
   ###########################
   
   users = [('tashitso','anamza348','tashitsoMask'), ('TashiNew_March','TashiNew_March','TashiNew_March_Mask'),
            ('TashiFourSpecies','TashiFourSpecies','TashiFourSpecies_Mask'),('TashiTestMay','TashiTestMay','TashiTestMay_Mask')]
   #users = [('TashiNew_March','TashiNew_March')]  # tested with this user
   
   # dictionary of dictionaries with user name as key, {'user':{'pwd':####, 'csv':/.../.../###.csv}
   usersPaths = {l[0][0]:{'pwd':l[0][1],'maskCode':l[0][2],'csv':os.path.join(csvBase,l[1])} for l in zip(users,csvList)}
   
   ####################################################################
   
   maskShpBase = "/home/jcavner/Tash_Masks_July10_2015/FiNAL_MUlTI"
   
   tifMaskBasePath = "/home/jcavner/Tash_Masks_July10_2015/Tiffs"
   
   #####################################################################
   
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
   
   # applythresholdrule, 4 : 'Minimum training presence' 
   
   modelNames  = []  # for testing for duplicates
   NoNewMasks = 0
   for item in usersPaths.items():
      try:   
         user = item[0]
         valueDict = item[1]
         pwd = valueDict['pwd']
         csvPath = os.path.join(csvBase,valueDict['csv'])
         
         client = buildClient(user,pwd)
         
         lr = list(csv.reader(open(csvPath,'r')))
         modelInfo = [{k:v  for k,v in zip(lr[0],l) } for l in lr[1:]]  #list of dictionaries
         # {'maskid': '6665', 'scenarioid': '1045', 'occurrencesetid': '5683841', 
         # 'name': 'Limnonectes_cf_magnus', 'modelid': '1493091'}
         #
         #modelNames.append([d['name'] for d in modelInfo ])  # just for testing
         typeCode = valueDict['maskCode']
         for model in modelInfo:
            try:
               name = model["name"] # just for test
               #occId   =  model['occurrencesetid']
               #occObj  = getOccSet(occId)
               #count   = getOccCount(occSet=occObj)
               #if count >= 5:
               if True:
                  if name in NewMaskSps:
                     NoNewMasks += 1
                     ## if name in NewMasksSps build new mask and post, use id from returned post for mask
                     #shpPath = os.path.join(maskShpBase,"%s%s" % (NewMaskSps[name],".shp"))
                     #if not os.path.exists(shpPath):
                     #   raise Exception, "missing shpPath %s" % (shpPath)
                     #   
                     #tiffoutPath = buildMask(shpPath, tifMaskBasePath, NewMaskSps[name])
                     #if not os.path.exists(tiffoutPath):
                     #   raise Exception, "missing tiffPath, failed to make mask %s" % (tiffoutPath)
                     #
                     #   
                     #dloc = tiffoutPath
                     #postedMask = postMaskLayer(name+"_MASK_July10_FirstTry", dloc, typeCode ,epsg)
                     #mdlMask = prjMask = postedMask.id
                     
                  else:
                     mdlMask = prjMask = model["maskid"] 
                  
                  #mdlScen = model['scenarioid']
                  #prjScen = [] #[model["scenarioid"]]         
                  #exp     = postExperiment(occId, "ATT_MAXENT", 
                  #                        mdlScen, mdlMask, 
                  #                        prjMask, prjScen = prjScen, 
                  #                        algoParams = params)
            except Exception,e:
               print "SPECIES EXCEPTION ",name," for user",user,"  ",str(e)
            else:
               print "successfully posted ",name
                 
         del client  # instead of logout
      except Exception, e:
         print "Other EXCEPTION ",str(e),"for user ",user
   print "No NEW MASKS ",NoNewMasks  
####################  diagnostic bloc ###################
   #searchDict = {}
   #searchDict.update(NewMaskSps)
   #searchDict.update(NotNewMasks)
   #
   #dbNames = []
   #for x in modelNames:
   #   for y in x:
   #      dbNames.append(y)
   #print 
   #print "Lengths"     
   #print "What lifemapper has from edited csv of db queries ",len(dbNames)
   #print "Tahsi's spread sheet ",len(searchDict) 
   #print
   #print "names in Tashi's spreadsheet but not in db query csv"
   #for k in searchDict.keys():
   #   if k not in dbNames:
   #      print k
   #print
   #print "names in db query csv but not in Tashi's spreadsheet"
   #for n in dbNames:
   #   if n not in searchDict.keys():
   #      print n
   #      
   #      
   #import collections
   #counter = collections.Counter(dbNames)
   #print
   #print "Repeats in Lifemapper edited csv's of db queries"
   #print counter.most_common(5)
   ######################## end diagonistics #############################   