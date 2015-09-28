import commands
from osgeo import ogr
from qgis.core import *

mammalsDir = '/home/jcavner/terrestrial_mammals/africa_mammals/unzipped/*.shp'

mammalsInDir = commands.getoutput("ls %s" % mammalsDir)

mammalsList = mammalsInDir.split("\n")

count = 0
invalid  = 0
for shp in mammalsList:
   handle = ogr.Open(shp)
   layerObj = handle.GetLayer(0)
   layerDef = layerObj.GetLayerDefn()
   featureCnt = layerObj.GetFeatureCount()
   if featureCnt < 1:
      print shp.split('/')[6]
   fieldCount = layerDef.GetFieldCount()
   choices  = []
   for fieldIdx in range(0,fieldCount):
      fieldDef = layerDef.GetFieldDefn(fieldIdx)
      choices.append(fieldDef.GetName())
   if 'PRESENCE' in choices:
      
      count += 1
   else:
      print shp.split('/')[6], str(choices)
   handle.Destroy()  
   
   
   #myLayer = QgsVectorLayer(str(shp),'testCRS','ogr')
   #if myLayer.isValid():
   #   print "valid"
   #else:
   #   invalid += 1
      #print "not valid ",shp.split('/')[6]
   #del myLayer
   
print "DONE"
print count
