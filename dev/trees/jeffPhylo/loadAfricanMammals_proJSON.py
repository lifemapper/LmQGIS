import commands
#from lifemapperTools.common.lmClientLib import LMClient as client
import simplejson


epsgCode = 3410


############ JSON and Dictionary ####################################

mammalJSONPath = '/home/jcavner/PhyloXM_Examples/prunedMatchedAfricanMammals.json'

mammalsDict = simplejson.loads(open(mammalJSONPath,'r').read())

##########  list ###############################

mammalsDir = '/home/jcavner/terrestrial_mammals/africa_mammals/unzipped/renamedEASE/*.shp'

mammalsInDir = commands.getoutput("ls %s" % mammalsDir)

mammalsList = mammalsInDir.split("\n")

#mammalsListSL = mammalsList[0:6]

countDict = {'c':0}

def recMammals(clade,mxDict):
   
  
   if "children" in clade:
      for child in clade["children"]:
         recMammals(child,mxDict)
      
   else:
      # this means it is a leaf
      fullPath = '/home/jcavner/terrestrial_mammals/africa_mammals/unzipped/renamedEASE/%s.shp' % (clade["name"])
      if fullPath in mammalsList:
         try:
            postresponse = client.rad.postVector(**{'filename':fullPath,
                                                                 'name':clade["name"],
                                                                 'epsgCode':epsgCode,
                                                                 'mapUnits':'meters'})
         except:
            print "failed to upload "+fullPath
         else:
            # succeeded in uploading 
            try:
                
               layerId = postresponse.id
               inputs = {'lyrId':layerId,'expId':expId,'attrPresence':'PRESENCE','minPresence':1,
                            'maxPresence':2, 'percentPresence':25}
               ddresponse = client.rad.addPALayer(**inputs)
            except:
               print "failed to add PALayer "+fullPath
            else:
               # add dictionary key "mx" here
               print "uploaded and added ",clade["name"]
               clade["mx"] = mxDict['c']
               #print "succeeded "+clade["name"]+" with mx "+str(mxDict['c'])
               mxDict['c'] += 1
      #else:
      #   pass
         #print "did not find "+clade["name"]+" in directory"      

ids = [1074]               
users = ['Workshop5']               

import sys
import os
import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
sys.path.append(os.path.join(import_path, 'LmShared'))
configPath = os.path.join(import_path, 'config', 'config.ini')
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
from LmClient.lmClientLib import LMClient

               
for expId,user in zip(ids,users):   
   
   client = LMClient(user,user)            
   recMammals(mammalsDict,countDict)    
   # post the json
   try:
      resp = client.rad.addTreeForExperiment(expId, jTree=mammalsDict)
   except:
      post = False
   else:
      post = resp
   print "POST ",post 
   
   client = None    

#with open('/home/jcavner/PhyloXM_Examples/african_mammal_realDealMX.json','w') as outfile:               
#   simplejson.dump(mammalsDict,outfile,indent=4)    