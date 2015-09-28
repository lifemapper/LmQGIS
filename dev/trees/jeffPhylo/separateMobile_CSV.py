import csv
from decimal import *
import os
from shapely.geometry import Point, mapping
import fiona

csvPath = "/home/jcavner/MobileAlabama/Knouft_data_for_KU/locality_data/Mobile_crayfish_csv.csv"
lr = list(csv.reader(open(csvPath,'r')))

ld = [{k:v  for k,v in zip(lr[0],l) } for l in lr[1:]]

pointDict = {}
for d in ld:
   name = d['Species']
   x = float(d['longitude'])
   y = float(d['latitude'])
   if name in pointDict:   
      pointDict[name].append((x,y))
   else:
      pointDict[name] = [(x,y)]

prjInfo = """PROJCS["NAD_1983_UTM_Zone_16N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-87],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]"""
      
    

      
schema = { 'geometry': 'Point', 'properties': { 'name': 'str:24'} }
shpOutBasePath = "/home/jcavner/MobileAlabama/Knouft_data_for_KU/locality_data/Crayfish/shps"      
print len(pointDict.keys())
for key in pointDict:
   # each key will be a shapefile
   shpOut = os.path.join(shpOutBasePath,key+'.shp')
   with fiona.open( shpOut, "w", "ESRI Shapefile", schema) as output:
      for x,y in pointDict[key]:
         point = Point(x, y)
         output.write({'properties': {'name': key},'geometry': mapping(point)})
      
   with open(os.path.join(shpOutBasePath,key+".prj"),'w') as out:
      out.write(prjInfo)      
