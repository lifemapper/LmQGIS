import commands
import os


cutPath = "/home/jcavner/TashiTestOcc/prepForMasks/philippines.shp"

#for scen in scens:
   #for yr in yrs:
#listtifs = commands.getoutput('ls /home/jcavner/worldclim_lwr48/future/NIES/%s/%s/*.tif' % (scen,yr))
listtifs = commands.getoutput('ls /home/jcavner/TashiTestOcc/climate/bboxCut/*.tif')
tifpaths = listtifs.split('\n')

#outpath = "/home/jcavner/Bison_WorldClim/Future/%s/%s/" % (scen,yr)
outpath = "/home/jcavner/TashiTestOcc/climate/PHCut/" 
#print "DOING SCEN ",scen," YEARS ",yr

for path in tifpaths:
   
   # get just tiff names
   fN = os.path.split(path)[1]
   fullout = os.path.join(outpath,fN)   
   #extent = "-125 50 -66 24"
   #gdalwarp -q -cutline /home/jcavner/USAdminBoundaries/US_Bison_Lwr48_singleParts.shp -crop_to_cutline -of GTiff /share/data/ClimateData/Present/worldclim/bio_9.tif /home/jcavner/worldclim_lwr48/test.tif
   # gdal_translate -projwin -90.0 90.0 180.0 -36.0 -of GTiff /share/data/ClimateData/Present/worldclim/bio_1.tif /home/jcavner/out.tif
   #gdalStr = "gdal_translate -projwin %s -of GTiff %s %s" % (extent,path,fullout)
   gdalStr = "gdalwarp -dstnodata -9999 -q -cutline %s -crop_to_cutline -of GTiff %s %s" % (cutPath,path,fullout)
   #print gdalStr
   resp = commands.getoutput(gdalStr)
   print resp
print "done"
