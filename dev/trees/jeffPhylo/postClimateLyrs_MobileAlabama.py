import os,sys
import commands

import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
sys.path.append(os.path.join(import_path, 'LmShared'))
configPath = os.path.join(import_path, 'config', 'config.ini') 
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
#######################################

from LmClient.lmClientLib import LMClient

client = LMClient()
client.login('MobileAlabama2','MobileAlabama2')

tifs = ['/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current training layers/GeoTiffProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current training layers/GeoTiffProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current training layers/GeoTiffProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current training layers/GeoTiffProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current training layers/GeoTiffProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 low/GeoTiffProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 low/GeoTiffProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 low/GeoTiffProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 low/GeoTiffProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 low/GeoTiffProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 high/GeoTiffProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 high/GeoTiffProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 high/GeoTiffProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 high/GeoTiffProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 high/GeoTiffProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 med/GeoTiffProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 med/GeoTiffProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 med/GeoTiffProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 med/GeoTiffProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 med/GeoTiffProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 high/GeoTiffsProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 high/GeoTiffsProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 high/GeoTiffsProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 high/GeoTiffsProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 high/GeoTiffsProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 low/GeoTiffsProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 low/GeoTiffsProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 low/GeoTiffsProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 low/GeoTiffsProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2086 low/GeoTiffsProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 med/GeoTiffProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 med/GeoTiffProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 med/GeoTiffProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 med/GeoTiffProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/future projection layers/2051 med/GeoTiffProjected/max_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current projection layers/GeoTiffProjected/slope_deg.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current projection layers/GeoTiffProjected/mean_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current projection layers/GeoTiffProjected/min_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current projection layers/GeoTiffProjected/cv_flow.tif'
,'/home/jcavner/MobileAlabama/Knouft_data_for_KU/flow_rasters/current projection layers/GeoTiffProjected/max_flow.tif']

occDirectory = "/home/jcavner/MobileAlabama/Knouft_data_for_KU/locality_data/AllPointShps/"
epsg = 26916
res = commands.getoutput('ls %s*.shp' % (occDirectory))  
occs = res.split('\n')

for occFilePath in occs:
   displayName = os.path.splitext(os.path.basename(occFilePath))[0]
   #print displayName,"   -   ",occFilePath
   try:
      occ = client.sdm.postOccurrenceSet(displayName,'shapefile',occFilePath,epsgCode=epsg)   
   except Exception, e:
      print "could not post ",displayName," ",str(e)
   else:
      print "posted ",occ.id

#for path in tifs:
#   typecode = os.path.basename(path).replace('.tif','')
#   epsgCode = 26916
#   dataFormat = 'GTiff'
#   units = 'meters'
#   projType = path.split("/")[6]
#   if "training" in projType:
#      name = path.split("/")[8].replace('.tif','_model')
#      #print name
#   if "future" in projType:
#      name = "%s_%s" % (path.split("/")[9].replace('.tif',''),path.split("/")[7].replace(" ","_"))
#      #print name
#   if "current projection layers" in projType:
#      name = path.split("/")[8].replace('.tif','_current')
#      #print name
#   description = name
#   title = name
#   
#   try:
#      obj = client.sdm.postLayer(name, epsgCode, typecode, 
#                                                  units, dataFormat, title=title,
#                                                  description=description,
#                                                  fileName=path)
#   except Exception, e:
#      print "could not post ",path," ",str(e)
#   
#   else:
#      print "posted ",obj.id
      
      