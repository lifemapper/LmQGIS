"""
@summary: This is the Agoodle module from Brent Pedersen at 
             https://github.com/brentp/agoodle modified by Jeff Cavner on 
             6/17/11.  Agoodle intersects polygons against rasters.  
             Raster/Polygon intersects are made very efficient by treating the 
             intersection as a point in polygon exercise (using matplotlib's 
             point in poly) by finding the bbox in pixel coords of a the 
             polygon, and then building an array of points that represent 
             pixels within that local pixel space, and then finds the number of 
             points from that array that fall within the vertices of the 
             polygon in pixel coords.  
@contact: Jeff Cavner - jcavner [at] ku [dot] edu
@note: I modified it to take into account the use case for when the ratio of 
          pixel size to polygon size is close to the same, or if the pixel size 
          is larger than the polygon size.  I added raster_as_poly to the 
          Agoodle class, and mask_with_raster to the goodlearray class.  These 
          methods allow you to treat pixels as polygons and then do an 
          intersection against those polygons and the polygon of interest.

@license: gpl2
@copyright: Copyright (C) 2015, University of Kansas Center for Research

          Lifemapper Project, lifemapper [at] ku [dot] edu, 
          Biodiversity Institute,
          1345 Jayhawk Boulevard, Lawrence, Kansas, 66045, USA
   
          This program is free software; you can redistribute it and/or modify 
          it under the terms of the GNU General Public License as published by 
          the Free Software Foundation; either version 2 of the License, or (at 
          your option) any later version.
  
          This program is distributed in the hope that it will be useful, but 
          WITHOUT ANY WARRANTY; without even the implied warranty of 
          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
          General Public License for more details.
  
          You should have received a copy of the GNU General Public License 
          along with this program; if not, write to the Free Software 
          Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
          02110-1301, USA.
"""

import numpy as np
try: # Version 1.3
   import matplotlib.nxutils as nx
except: # Version 1.1
   from matplotlib.path import Path
from osgeo import gdal
from osgeo import ogr, osr
import os.path as op

# .............................................................................
class _RasterInfo(object):

   # ...................................
   def __init__(self, raster):
      t = raster.GetGeoTransform()
      self.left  = t[0]
      self.xsize = t[1]
      self.top   = t[3]
      self.ysize = t[5]
      
      self.nx = raster.RasterXSize
      self.ny = raster.RasterYSize
      
      self.bottom = self.top  + self.ysize * self.ny
      self.right  = self.left + self.xsize * self.nx
      
      assert self.right > self.left, "bounds are messed up"
      if self.bottom > self.top:
         self.bottom, self.top = self.top, self.bottom
         self.ysize *= -1
      #assert self.bottom < self.top

   # ...................................
   def __repr__(self):
      fmt = "_RasterInfo(extent=(%.2f, %.2f, %.2f, %.2f)"
      fmt += ", pixel=(%i, %i), gridsize=(%i, %i))"
      return fmt % (self.left, self.bottom, self.right, self.top,\
                           self.xsize, self.ysize, self.nx, self.ny)

   # ...................................
   @property
   def extent(self):
      return (self.left, self.bottom, self.right, self.top)

# .............................................................................
class AGoodle(object):
   """
   @summary: Class used to access raster data sets through GDAL as numpy arrays
                and allows polygon queries on raster data sets.
   """
   # ...................................
   def __init__(self, filename):
      assert op.exists(filename), "%s does not exist" % filename
      self.filename = filename
      self.raster   = gdal.Open(filename)
      self.ri = self.raster_info = _RasterInfo(self.raster)

   # ...................................
   def __repr__(self):
      return "%s(\"%s\")" % (self.__class__.__name__, self.filename)

   # ...................................
   def bbox_to_grid_coords(self, bbox):
      """
      @summary: given a bbox OF THE ENVELOPE OF THE POLYGON in real-world 
                   coordinates return the indexes into the .tif that will 
                   extract the data -- though note that ReadArray requires 
                   offset for the 3rd, 4th params, not xmax, ymax.  Also return 
                   the modified bbox, that exactly matches the grid coords.
      """
      bbox = list(bbox) # incase it's a tuple
      gt = self.ri
      if bbox[0] < gt.left: bbox[0] = gt.left
      if bbox[3] > gt.top:  bbox[3] = gt.top
      # TODO: trim to the other edges as well.
      
      tminx = (bbox[0] - gt.left)/ gt.xsize
      tmaxx = (bbox[2] - gt.left)/ gt.xsize
      tminy = (bbox[3] - gt.top) / gt.ysize
      tmaxy = (bbox[1] - gt.top) / gt.ysize
      #assert tminx < tmaxx, ("min should be < max!", tminx, tmaxx)
      if tminy > tmaxy:
         (tminy, tmaxy) = (tmaxy, tminy)
      if tminx > tmaxx:
         (tminx, tmaxx) = (tmaxx, tminx)
      # round down for mins, and up for maxs to make sure the
      # requested extent is in the area requested.
      tminx, tminy = [max(int(round(t - 0.5)), 0) for t in (tminx, tminy)]
      tmaxx, tmaxy = [int(round(t + 0.5)) for t in (tmaxx, tmaxy)]
      if tmaxx > self.ri.nx and self.ri.nx > tminx : tmaxx = self.ri.nx
      if tmaxy > self.ri.ny and self.ri.ny > tminy: tmaxy = self.ri.ny
      cbbox = [tminx, tminy, tmaxx, tmaxy]
      assert cbbox[2] > cbbox[0] and cbbox[3] > cbbox[1], ("box out of order", cbbox)

      new_bbox = [None, None, None, None]
      new_bbox[0] = gt.left + cbbox[0] * gt.xsize
      new_bbox[2] = gt.left + cbbox[2] * gt.xsize
      new_bbox[1] = gt.top + cbbox[3] * gt.ysize
      new_bbox[3] = gt.top + cbbox[1] * gt.ysize
      assert new_bbox[3] > new_bbox[1], (new_bbox, "out of order")
      
      return cbbox, new_bbox

   # ...................................
   def read_array_bbox(self, bbox=None):
      """
      @summary: given a bbox : (xmin, ymin, xmax, ymax) return a numpy array of 
                   that extent
      """
      if bbox is None:
         bbox = self.ri.extent
      idxs, new_bbox = self.bbox_to_grid_coords(bbox)
      # new_bbox is the bbox for the polygon in real coords to the nearest pixel,
      # idxs is a bounding box in pixel coords of the extent of the polygon
      if bbox[0] > self.ri.right or bbox[3] < self.ri.bottom or \
      bbox[2] < self.ri.left or bbox[1] > self.ri.top:
         ll = [[-999 for x in range(0,idxs[2]-idxs[0])] for y in range(0,idxs[3]-idxs[1])]
         a = np.array(ll)
      else:
         try:
            a = self.raster.ReadAsArray(idxs[0], idxs[1],\
                 idxs[2] - idxs[0], idxs[3] - idxs[1])
         except Exception, e:
            print(str(e))
            print((idxs[0], idxs[1], idxs[2] - idxs[0], idxs[3] - idxs[1]))
      
      # ReadAsArray is a gdal method that returns an array of the pixel values 
      # found within a bbox of pixel coords.  The values are laid out in the 
      # array in the position they are found in the bbox
      
      return goodlearray(a, self, new_bbox)
   
   # ...................................
   def raster_as_poly(self, wkt, wkt_epsg=None, this_epsg=None ):
      """
      @summary: Masks a raster with a polygon specified by wkt
      @param wkt: The well-known text representation of a polygon to use for a 
                     mask
      @param wkt_epsg: (optional) The EPSG Spatial Reference of the WKT.  If 
                          this is None, the Spatial Reference of the raster 
                          will be used.
      @param this_epsg: (optional) The EPSG Spatial Reference of the raster.  
                           If this is None, it will be determined from the
                           raster data.
      """
      
      this_sr = osr.SpatialReference()
      wkt_sr = osr.SpatialReference()
      if this_epsg is None:
         pr = self.raster.GetProjection()
         this_sr.ImportFromWkt(pr)
      else:
         this_sr.ImportFromEPSG(this_epsg)
      if wkt_epsg is None:
         pr = self.raster.GetProjection()
         wkt_sr.ImportFromWkt(pr)
      else:
         wkt_sr.ImportFromEPSG(wkt_epsg)

      pts, bbox = points_from_wkt(wkt, wkt_epsg, this_sr)
      # bbox is a tuple in real world coords
      a = self.read_array_bbox(bbox)
      results = a.mask_with_raster(pts)
      return results
      
      
   # ...................................
   def summarize_wkt(self, wkt, wkt_epsg=None, this_epsg=None):
      """
      @summary: encapsulate the common task of querying a raster with a wkt polygon
      returns a dictionary of class : area.
      where class is the integer value in the raster data store and area is
      the area in units of the raster.
      Likely, one will convert the integer classes into their human-readable names before
      presenting.
      @return:  a dictionary of intersect summary values
      """
      this_sr = osr.SpatialReference()
      wkt_sr = osr.SpatialReference()
      if this_epsg is None:
         pr = self.raster.GetProjection()
         this_sr.ImportFromWkt(pr)
      else:
         this_sr.ImportFromEPSG(this_epsg)
      if wkt_epsg is None:
         pr = self.raster.GetProjection()
         wkt_sr.ImportFromWkt(pr)
      else:
         wkt_sr.ImportFromEPSG(wkt_epsg)

      pts, bbox = points_from_wkt(wkt, wkt_epsg, this_sr)
      # bbox is a tuple in real world coords
      # pts is a numpy array of vertix pairs of the wkt polygon in real world
      # coords
      a = self.read_array_bbox(bbox)
      # a is a goodlearray
      if len(a.shape) == 2:
         a.mask_with_poly(pts, copy=False)
         return a.do_stats()
      else:
         return {-999:0}

   # ...................................
   def circle_mask(self, cradius, mask):
      xs, ys = np.mgrid[-cradius:cradius + 1
                         , -cradius:cradius + 1]

      d = np.sqrt(xs **2 + ys ** 2)
      d = (d  <= cradius).astype(np.int)
      return d

   # ...................................
   def read_array_pt_radius(self, x, y, radius=50000, mask=0, do_mask=True):
      ri = self.ri
      cell_x = (x - ri.left)/ ri.xsize - (radius / ri.xsize)
      cell_y = (ri.top - y)/ abs(ri.ysize) + (radius / ri.ysize)

      cell_x, cell_y = int(round(cell_x)), int(round(cell_y))
      xsize = int(round(2 * radius / ri.xsize + 0.5))
      ysize = abs(int(round(2 * radius / ri.ysize + 0.5)))
      # it has to be an odd number for the masking.
      if not xsize % 2: xsize += 1
      if not ysize % 2: ysize += 1
      a = self.raster.ReadAsArray(cell_x, cell_y, xsize, ysize)
      if do_mask:
         m = self.circle_mask(xsize / 2, mask=mask)
         #assert False, (cell_x, cell_y, ri.xsize, ri.ysize)
         return goodlearray(m * a, self, [x - radius, y - radius, x + radius, y + radius])
      else:
         return goodlearray(a, self, [x - radius, y - radius, x + radius, y + radius])


# .............................................................................
class goodlearray(np.ndarray):
   """
   @summary: an enhanced numpy array class that keeps geographic information
   allowing simple querying of an array with real world coordinates
   """
   
   # ...................................
   def __new__(cls, data, agoodle, extent, dtype=None, copy=False):
      try:
         arr = np.array(data, dtype=dtype, copy=copy).view(cls)
      except Exception,e:
         print(str(e))
         
      arr.agoodle = agoodle
      arr.extent = extent # in real world coords, Jeff, Dec 6. 2012
      return arr

   # ...................................
   def rw2index(self, rx, ry):
      """
      @summary: this used for every real world coord vertice in the polygon.  
      @return: integer coord pairs in pixel coordsIt returns.
      """
      bbox = self.extent
      #assert bbox[0] <= rx <= bbox[2] \
      #   and bbox[1] <= ry <= bbox[3],\
      #       ('point out of grid', bbox, (rx, ry))
   
      xrng = float(bbox[2] - bbox[0])
      yrng = float(bbox[3] - bbox[1])
      # xrng and yrng are the dimensions bbox
      x = (rx - bbox[0]) / xrng * self.shape[1]
      y = (bbox[3] - ry) / yrng * self.shape[0]
      #y = (ry - bbox[1]) / yrng * self.shape[0]
                     
      ix, iy = int(x), int(y) 
         
      if ix == self.shape[1]: ix -= 1
      if iy == self.shape[0]: iy -= 1
     
      #assert ix < self.shape[1], (ix, self.shape[1],rx,ry,"first assert")
      #assert iy < self.shape[0], (iy, self.shape[0],rx,ry, "second assert")

      return ix, iy

   # ...................................
   def rw(self, rx, ry):
      """@summary: take real world coordinate and read the value at
      that coord"""
      ix, iy = self.rw2index(rx, ry)
      return self[iy, ix]
   
   # ...................................
   def mask_with_raster(self,verts):
      """
      @summary: this is the reverse of mask_with_poly.  It is used when the 
      resolution of the shapegrid cell is smaller than the resolution of the
      pixel in a raster palayer.  Therefore it finds how many shapegrid cells
      fall inside of a raster pixel, by treating the dimensions of the pixel
      as a polygon
      @param: verts is a numpy array of coordinate pairs in real-world
      coordinates of the shapegrid cell
      """
      
      coords = [str(v[0])+ ' ' + str(v[1]) for v in verts]
      vertsStr = ','.join(coords)
      shapepoly = ogr.CreateGeometryFromWkt('Polygon(('+vertsStr+'))')
      sumDict = {}
      xres = abs(self.agoodle.ri.xsize)
      yres = abs(self.agoodle.ri.ysize)
      for y in range(0,self.shape[0]):
         for x in range(0,self.shape[1]):
            minx = (x * xres) + self.extent[0]
            miny = self.extent[3] - ((y + 1) * yres)
            maxx = minx + xres
            maxy = miny + yres
            pixelwkt = 'Polygon (('+str(minx)+' '+str(miny)+','+str(maxx)+\
                        ' '+str(miny)+','+str(maxx)+' '+str(maxy)+','+str(minx)+\
                        ' '+str(maxy)+','+str(minx)+' '+str(miny)+'))'
            pixelpoly = ogr.CreateGeometryFromWkt(pixelwkt)
            if pixelpoly.Intersect(shapepoly):
               intersection = pixelpoly.Intersection(shapepoly)
               area = intersection.GetArea()
               if self[y][x] in sumDict.keys():
                  
                  sumDict[self[y][x]] = sumDict[self[y][x]] + area
               else:
                  sumDict[self[y][x]] = area
                  
      return sumDict
      
      
   # ...................................
   def mask_with_poly(self, verts, mask_value=0, copy=True):
      """@summary: verts is in real-world coordinates in same
      projection as this array.
      if copy is false, a new array is not created.
      """
      
      #TODO: sample if the array is too big.
      assert self.shape[0] * self.shape[1] < 4000000
            
      iverts = np.array([self.rw2index(v[0], v[1]) for v in verts])
      # iverts is the polygon vertices in pixel coordinates
      ys, xs = np.indices(self.shape)
      xys = np.column_stack((xs.flat, ys.flat))
      try: # version 1.1
         insiders  = nx.points_inside_poly(xys, iverts)
      except Exception, e:
         try: # version 1.3
            path = Path(iverts)
            insiders = path.contains_points(xys)
         except Exception, e2:
            print(str(e))
            print(str(e2))
      outsiders = xys[(insiders == 0)]
   
      if copy:
         b = self.copy()
         b[(outsiders[:, 1], outsiders[:, 0])] = mask_value
         return b
      self[(outsiders[:, 1], outsiders[:, 0])] = mask_value
      

   # ...................................
   def do_stats(self, exclude=(0, )):
      """@summary: do some stats on the integer types in the array.
      returns the area of cells for each type found in the array.
      you can use this after masking to only calc inside the polygon.
      """
      raster_info = self.agoodle.raster_info
      classes = np.unique(self)
      cell_area = abs(raster_info.xsize * raster_info.ysize)
      stats = {}
      for cls in (c for c in classes if c not in exclude):
         stats[cls] = len(self[self == cls]) * cell_area
      return stats

   # ...................................
   def to_raster(self, filename, driver='GTiff'):
      """
      @summary converts a goodle numpy array into a tiff, this may be useful
      in the future for returning stats as rasters
      """
      from osgeo import gdal_array
      # convert from numpy type to gdal type.
      gdal_type = dict((v, k) for (k, v) \
              in gdal_array.codes.items())[self.dtype.type]
   
      # make it so we can loop over 3rd axis.
      if len(self.shape) == 2:
         a = self[:, :, np.newaxis]
      else:
         a = self
      bbox = self.extent
      ri = self.agoodle.ri
      d = gdal.GetDriverByName(driver)
   
      # NOTE: switch of shape[0] and [1] !!!!
      tif = d.Create(filename, a.shape[1], a.shape[0], a.shape[2], gdal_type)
      xsize = (bbox[2] - bbox[0]) / (self.shape[1])
      ysize = (bbox[1] - bbox[3]) / (self.shape[0])
      # could be a bit off since we had to round to pixel.
      assert abs(xsize - ri.xsize) < 1
      assert abs(ysize - ri.ysize) < 1, (ysize, ri.ysize, xsize, ri.xsize)
      tif.SetGeoTransform([bbox[0], xsize, 0, bbox[3], 0, ysize])
      for i in range(a.shape[2]):
         b = tif.GetRasterBand(i + 1)
         ct = self.agoodle.raster.GetRasterBand(i + 1).GetRasterColorTable()
         if ct:
            b.SetRasterColorTable(ct)
         gdal_array.BandWriteArray(b, a[:, :, i])
      tif.SetProjection(self.agoodle.raster.GetProjection())
      return tif

# .............................................................................
def points_from_wkt(wkt, from_epsg, to_epsg):
   """
   @summary: Send in the wkt for a polygon and get back the points and the bbox 
                that contains those points.  'from_epsg' and 'to_epsg' 
                determine how to reproject the points. This can be used if the 
                wkt is in a projection different from the raster to be queried.
   """
   g = ogr.CreateGeometryFromWkt(wkt)
   if isinstance(from_epsg, (long, int)):
      ifrom = osr.SpatialReference(); ifrom.ImportFromEPSG(from_epsg)
   else:
      ifrom = from_epsg
   if isinstance(to_epsg, (long, int)):
      ito = osr.SpatialReference(); ito.ImportFromEPSG(to_epsg)
   else:
      ito = to_epsg
   g.AssignSpatialReference(ifrom)
   g.TransformTo(ito)
   
   # assume it's a polygon, get the outer ring.
   ring = g.GetGeometryRef(0)
   pts = []
   for i in range(ring.GetPointCount()):
      x, y, z = ring.GetPoint(i)
      pts.append((x, y))
   pts = np.array(pts)
   bbox = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
   return pts, bbox


def _openVectorLayer(dlocation):
   ogr.RegisterAll()
   drv = ogr.GetDriverByName('ESRI Shapefile')
   try:
      ds = drv.Open(dlocation)
   except Exception, e:
      raise Exception, 'Invalid datasource, %s: %s' % (dlocation, str(e))
   return ds



def _openShapefile(dlocation, localIdIdx):
   """
   """
   ds = _openVectorLayer(dlocation)
   lyr = ds.GetLayer(0)
   # Read featureId and geometry
   siteGeomDict = {}
   featCount = lyr.GetFeatureCount()
   minx, maxx, miny, maxy = lyr.GetExtent()
   for j in range(featCount):
      currFeat = lyr.GetFeature(j)
      if localIdIdx is not None:
         siteidx = currFeat.GetField(localIdIdx)      
      else:
         siteidx = currFeat.GetFID()
      # same as Shapegrid.siteIndices
      siteGeomDict[siteidx] = currFeat.geometry().ExportToWkt()
   
   return lyr, siteGeomDict, (minx, maxx, miny, maxy)


def rasterIntersect(sgDLocation, sgLocalIdIdx, lyrDLocation):
   """
   @summary: Intersects a Raster dataset by reading as a AGoodle raster 
             object.  Compares the shapegrid cell resolution against the 
             raster resolution.  
             If the shapegrid cell is 5X the resolution of the raster
               * then a regular AGoodle intersection is used, which 
                 treats the raster pixels within the polygon as a numpy matrix 
                 in pixel coords and uses matplotlib to find points, in the 
                 form of an array, that fall within the polygon vertices in 
                 integer pixel coords.  
               * otherwise, each raster pixel is treated as a polygon in real 
                 coords and is intersected with the shapegrid cell polygons.  
             Returns an array of presence (1), and absence(0) for each site
   @param layer: the PresenceAbsenceRaster object
   """     
   sgLyr, sgSiteGeomDict, sgExtent = _openShapefile(sgDLocation, sgLocalIdIdx)
   raster =  AGoodle(lyrDLocation)
          
   areaDict = {}
   for siteIdx, geom in sgSiteGeomDict.iteritems():
      cellgeom = ogr.CreateGeometryFromWkt(geom)
      cellarea = cellgeom.GetArea() 
      #if cellarea > (lyrResolution**2) * 25:                  
      summary = raster.summarize_wkt(geom)
      #else:        
      #   summary = raster.raster_as_poly(geom)
      areaDict[siteIdx] = (summary, cellarea)
   return areaDict 

def calcRasterWeightedMeanColumn(areaDict):
   """
   @summary: calculates weighted mean for pixels within each cell
   of the shapegrid and returns a column (1-dimensional array) of floating 
   point numbers for the GRIM
   """
   layerArray = np.zeros(len(areaDict), dtype=float)
   for siteidx, (summary, cellarea) in areaDict.iteritems():
      numerator = 0
      denominator = 0
      for pixelvalue in summary.keys():
         numerator += float(summary[pixelvalue]) * pixelvalue
         denominator += float(summary[pixelvalue])
      weightedMean = numerator / denominator
      layerArray[siteidx] = weightedMean
   return layerArray

def Avg(areaDict):
   layerArray = np.zeros(len(areaDict), dtype=float)
   for siteidx, (summary, cellarea) in areaDict.iteritems():
      numerator = 0
      denominator = 0
      for pixelvalue in summary.keys():
         numerator += float(pixelvalue)# * pixelvalue
      denominator = len(summary)
      weightedMean = numerator / denominator
      layerArray[siteidx] = weightedMean
   return layerArray

def calcRasterLargestClassColumn(areaDict, minPercent):
   layerArray = np.zeros(len(areaDict), dtype=float)
   minPercent = minPercent / 100.0
   for siteidx, (summary, cellarea) in areaDict.iteritems():
      maxArea = max(summary.values())
      if maxArea / cellarea >= minPercent:
         layerArray[siteidx] = summary.keys()[summary.values().index(maxArea)]
      else:
         layerArray[siteidx] = np.nan
   return layerArray   

if __name__ == "__main__":
   
   pass # TestAgoodle.shp

   raster = "/home/jcavner/Philippines_ScenarionLyrs_Downloaded/bio17_PH_AEAC.tif"
   shp = "/home/jcavner/TestAgoodle.shp"
   
   aD = rasterIntersect(shp,None,raster)
   for x,y in aD[0][0].iteritems():
      print x," ",y
   print calcRasterWeightedMeanColumn(aD)
   print Avg(aD)
   print calcRasterLargestClassColumn(aD, 5)
      