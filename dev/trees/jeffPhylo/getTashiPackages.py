
import csv
import os
import sys





import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
sys.path.append(os.path.join(import_path, 'LmShared'))
configPath = os.path.join(import_path, 'config', 'config.ini') 
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
#######################################
from LmClient.lmClientLib import LMClient





def buildClient(user = 'Dermot' ,pwd = 'Dermot'):
   
   client =  LMClient()
   client.login(user,pwd)
   return client


user = 'TashiTestMay'
pwd = 'TashiTestMay'

client = buildClient(user,pwd)

csvBase = "/home/jcavner/TashiCSV/"

outZipsBase = "/home/jcavner/TashiJuly16_2015Package_Zips"
   
# csv's from model table
csvList = ["tashitso.csv","TashiNew_March.csv","TashiFourSpecies.csv","TashiTestMay.csv"]
csvList = ["TashiTestMay.csv"]
for fcsv in csvList:
   csvPath = os.path.join(csvBase,fcsv)
   lr = list(csv.reader(open(csvPath,'r')))
   modelInfo = {l[2]:{k:v  for k,v in zip(lr[0],l) } for l in lr[1:]}
   noComplete = 0
   for key in modelInfo:
      # build path
      try:
         filename = os.path.join(outZipsBase,modelInfo[key]['name']+'.zip')
      #print filename
         lexp = client.sdm.listExperiments(afterTime='2015-07-09',status=300,
                                           occurrenceSetId=key)
         if len(lexp) <> 1:
            raise Exception, "could not list package for occset "+key
         else:
            modelid = lexp[0].id
            client.sdm.getExperimentPackage(modelid,filename)
      except Exception, e:
         print str(e)
      else:
         noComplete = noComplete + 1
         
   print
   print
   print "No COMPLETE ",noComplete
   
