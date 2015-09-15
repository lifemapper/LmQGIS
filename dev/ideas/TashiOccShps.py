import csv as c
import os
import commands
from shapely.geometry import Point, mapping
import fiona
 
schema = { 'geometry': 'Point', 'properties': { 'name': 'str:24'} }

# Tashi change here
#############
csvPath = '/home/jcavner/TashiTestOcc/'
shpOutBasePath = '/home/jcavner/'
lonField = 'dec_long'
latField = 'dec_lat'
nameField = 'sciname'
################

csvs = commands.getoutput('ls %s*.csv' % (csvPath))
csvPathList = csvs.split('\n')


for csv in csvPathList:
   spsName = os.path.basename(csv)   
   shpOut = os.path.join(shpOutBasePath,spsName.replace('.csv','.shp'))
   try:
      with fiona.open( shpOut, "w", "ESRI Shapefile", schema) as output:
         with open(csv, 'rb') as f:
            reader = c.DictReader(f)
            for row in reader:
               point = Point(float(row[lonField]), float(row[latField]))
               output.write({
               'properties': {
               'name': row[nameField]
               },
               'geometry': mapping(point)
               })
   except Exception, e:
      print "failed to write %s because %s" % (spsName,str(e))
   else:
      print "success!"
print; print; print "finsihed"