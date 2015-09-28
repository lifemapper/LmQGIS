from osgeo import gdal,ogr
import numpy as np
import struct





def getThreshold(tifPath,shpPath,percentile):
   """
   @summary: given a given a GeoTiff and a shapefile return min and max thresholds
   as a percentile for lower threshold, and max for upper
   @param tifPath: full path to tiff
   @param shpPath: full path to shp
   @param percentile: percentile to return (integer)
   """
   
   tiffDs=gdal.Open(tifPath) 
   tO=tiffDs.GetGeoTransform()
   rb=tiffDs.GetRasterBand(1)
   
   RXSize = tiffDs.RasterXSize
   RYSize = tiffDs.RasterYSize
   
   sphDs=ogr.Open(shpPath)
   lyr=sphDs.GetLayer()
   
   pxValues = []
   for feat in lyr:
      geom = feat.GetGeometryRef()
      
      x,y = geom.GetX(), geom.GetY()  #coord in map units
      
      #Convert from map to pixel coordinates.
      px = int((x - tO[0]) / tO[1]) #x pixel
      py = int((y - tO[3]) / tO[5]) #y pixel
      
      if px >= 0 and px <= RXSize and py >= 0 and py <= RYSize:
         structval=rb.ReadRaster(px,py,1,1,buf_type=rb.DataType) 
         val = struct.unpack('f',structval)[0] 
         if val != rb.GetNoDataValue(): 
            pxValues.append(val) 
      
    
   return np.percentile(pxValues,percentile),max(pxValues)



if __name__ == "__main__":
   
   tiff_filename = '/home/jcavner/TashiGeoTiffsJuly20_2015/Occidozyga_laevis.tif'
   shp_filename = '/home/jcavner/TashiShpDownloadedFromTree/Occidozyga_laevis.shp'
   
   print getThreshold(tiff_filename,shp_filename,10)