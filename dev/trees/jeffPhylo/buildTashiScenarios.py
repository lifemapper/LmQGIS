import os,sys
import commands

import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
sys.path.append(os.path.join(import_path, 'LmShared'))
configPath = os.path.join(import_path, 'config', 'config.ini') 
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
#######################################
from LmClient.lmClientLib import LMClient


tiffDLoc = '/home/jcavner/Philippines_ScenarionLyrs_Downloaded/'

res = commands.getoutput('ls %s*.tif' % (tiffDLoc))  
tiffPaths = res.split('\n')





user = 'TashiTestMay'
pwd = 'TashiTestMay'

client = LMClient()
client.login(user,pwd)

for fullPath in tiffPaths:
   
   try:
      fullName = os.path.basename(fullPath).replace('.tif','')
      typeCodeName = fullName.split('_')[0]
      name = fullName.replace('_AEAC',"")
      
   
      typeCodeTitle = typeCodeName
      description = typeCodeName
      
      newCode = client.sdm.postTypeCode(typeCodeName, title=typeCodeTitle, description=description)
       
      
      epsgCode = 102028
      dataFormat = 'GTiff'
      units = 'meters'
      
   
      description = name
      title = name
      envLayerType = typeCodeName
      
      
      
      obj = client.sdm.postLayer(name, epsgCode, envLayerType, 
                                                  units, dataFormat, title=title,
                                                  description=description,
                                                  fileName=fullPath)
   except Exception, e:
      print str(e)
   
   else:
      print "posted ",name
      