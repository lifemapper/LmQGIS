import json
import os
import urllib2
import cPickle
from osgeo import ogr,gdal
import ntpath


def openShapefile(dlocation):

   ogr.RegisterAll()
   drv = ogr.GetDriverByName('ESRI Shapefile')
   try:
      ds = drv.Open(dlocation)
   except Exception, e:
      raise Exception, 'Invalid datasource, %s: %s' % (dlocation, str(e))
   return ds

def getDistinctSpecies(BdS,shpName,spsField):
   """
   @param BdS: Boom shapefile datasource   
   """
   distinctSps = []
   sql = 'SELECT DISTINCT %s FROM %s' % (spsField,shpName)
   res = BdS.ExecuteSQL(sql)
   for feature in res:
      distinctSps.append(feature.GetField(0))
      
   return distinctSps
   
def buildLookupIdx(distinctSps):
   
   # http://api.gbif.org/v1/species/match?verbose=true&rank=species&&class=aves&name=Xenicus%20gilviventris
   look = {}
   notIn = []
   for spsName in distinctSps:
      url = "http://api.gbif.org/v1/species/match?verbose=true&rank=species&class=aves&name=%s" % (spsName)
      try:
         r = urllib2.urlopen(url)
         res = r.read()
         j = json.loads(res)
         if "family" in j:
            if j["family"] not in look:
               look[j["family"]] = [spsName]
            else:
               look[j["family"]].append(spsName)
         if "order" in j:
            if j["order"] not in look:
               look[j["order"]] = [spsName]
            else:
               look[j["order"]].append(spsName)
         if "genus" in j:
            if j["genus"] not in look:
               look[j["genus"]] = [spsName]
            else:
               look[j["genus"]].append(spsName)
               
         
      except:
         print spsName, 'not in'
         notIn.append(spsName)
   cPickle.dump(look,open(os.path.join("/home/jcavner","taxaLookup.pkl"),"wb"))

if __name__ == "__main__":
   
   natureShp = "/home/jcavner/BiodiversityAfrica/Birds/GTBs_2011.shp"
   fieldName = 'SCINAME'
   shpName = ntpath.basename(natureShp)
   shpName = shpName.replace('.shp','')
   
   ds = openShapefile(natureShp)
   distinctSps = getDistinctSpecies(ds, shpName, fieldName)
   buildLookupIdx(distinctSps)
   
   