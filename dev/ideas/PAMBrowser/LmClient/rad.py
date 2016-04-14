"""
@summary: Client functions for Lifemapper RAD web services
@author: CJ Grady
@version: 3.3.4
@status: release

@license: Copyright (C) 2016, University of Kansas Center for Research

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

@note: Time format - Time should be specified in ISO 8601 format 
          YYYY-mm-ddTHH-MM-SSZ
             Where:
                YYYY is the four-digit year (example 2009)
                mm is the two-digit month (example 06)
                dd is the two-digit day (example 07)
                HH is the two-digit hour (example 09)
                MM is the two-digit minute (example 23)
                SS is the two-digit second (example 15)
            Example for June 7, 2009 9:23:15 AM - 2009-06-07T09:23:15Z
"""
import json
from types import ListType

from LmClient.constants import CONTENT_TYPES
from LmCommon.common.unicode import toUnicode

# .............................................................................
class RADClient(object):
   """
   @summary: Lifemapper RAD web service functions
   """
   # .........................................
   def __init__(self, cl):
      """
      @summary: Constructor
      """
      self.cl = cl
   
   # =========================================================================
   # =                              Experiments                              =
   # =========================================================================
   # .........................................
   def countExperiments(self, afterTime=None, beforeTime=None, epsgCode=None):
      """
      @summary: Counts experiments for a user
      @param afterTime: List experiments with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: List experiments with creation times before this time 
                            (ISO 8601 format)
      @param epsgCode: The epsg code of the experiments to return
      """
      url = "%s/services/rad/experiments/" % self.cl.server
      return self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode)])
      
   # .........................................
   def deleteExperiment(self, expId):
      """
      @summary: Deletes a Lifemapper RAD experiment
      @param expId: The id of the experiment to delete
      """
      url = "%s/services/rad/experiments/%s" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, method="DELETE", objectify=True)
      return obj
   
   # .........................................
   def getExperiment(self, expId):
      """
      @summary: Returns a Lifemapper RAD experiment
      @param expId: The id of the experiment to return
      """
      url = "%s/services/rad/experiments/%s" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, method="GET", objectify=True).experiment
      return obj
   
   # .........................................
   def getExperimentLayerIndices(self, expId, fileName):
      """
      @summary: Returns the layer indices for an experiment as a pickle
      @param expId: The id of the experiment to return the indicies for
      @param fileName: The file to store the pickled data in
      """
      url = "%s/services/rad/experiments/%s/indices" % (self.cl.server, expId)
      resp = self.cl.makeRequest(url, method="GET")
      try:
         open(fileName, 'w').write(resp)
      except Exception, _:
         return False
      return True
      
   # .........................................
   def listExperiments(self, afterTime=None, beforeTime=None, epsgCode=None, 
                                       page=0, perPage=100, fullObjects=False):
      """
      @summary: Lists experiments for a user
      @param afterTime: List experiments with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: List experiments with creation times before this time 
                            (ISO 8601 format)
      @param epsgCode: The epsg code of the experiments to return
      @param page: The page of results
      @param perPage: The number of results per page
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/experiments/" % self.cl.server
      return self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("fullObjects", int(fullObjects))])
   
   # .........................................
   def postExperiment(self, name, epsgCode, email=None, description=None):#, buckets=[], paLayers=[], ancLayers=[]):
      """
      @summary: Posts a new Lifemapper RAD experiment
      @param name: The name of this new experiment
      @param epsgCode: The EPSG code representing the projection used for all
                          spatial data in this experiment
      @param email: (optional) An email address to associate with this 
                       experiment
      """
      postXml = """\
      <lmRad:request xmlns:lmRad="http://lifemapper.org"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xsi:schemaLocation="http://lifemapper.org 
                                               /schemas/radServiceRequest.xsd">
            <lmRad:experiment>
               <lmRad:name>%s</lmRad:name>
               <lmRad:epsgCode>%s</lmRad:epsgCode>
%s
%s
            </lmRad:experiment>
         </lmRad:request>""" % (name, epsgCode,
               "               <lmRad:description>%s</lmRad:description>" % \
                           description if description is not None else "", 
               "               <lmRad:email>%s</lmRad:email>" % \
                           email if email is not None else "")
      url = "%s/services/rad/experiments/" % self.cl.server
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                body=postXml, 
                                headers={"Content-Type": "application/xml"},
                                objectify=True)
      return obj.experiment
   
     
   # Buckets
   # --------
   # .........................................
   def countBuckets(self, expId, afterTime=None, beforeTime=None):
      """
      @summary: Counts buckets for a user
      @param expId: The id of the experiment to count buckets for
      @param afterTime: Count buckets with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: Count buckets with creation times before this time 
                            (ISO 8601 format)
      """
      url = "%s/services/rad/experiments/%s/buckets" % (self.cl.server, expId)
      return self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime)])
   
   # .........................................
   def deleteBucket(self, experimentId, bucketId):
      """
      @summary: Delete a bucket from the Lifemapper system
      @param experimentId: The experiment containing the bucket
      @param bucket: The bucket to delete
      """
      url = "%s/services/rad/experiments/%s/buckets/%s" % (self.cl.server, 
                                                        experimentId, bucketId)
      obj = self.cl.makeRequest(url, method="DELETE", objectify=True)
      return obj
      
   # .........................................
   def getBucket(self, experimentId, bucketId):
      """
      @summary: Get one of an experiment's buckets
      @param experimentId: The experiment containing buckets
      @param bucketId: The bucket to return
      """
      url = "%s/services/rad/experiments/%s/buckets/%s" % (self.cl.server, 
                                                        experimentId, bucketId)
      obj = self.cl.makeRequest(url, method="GET", objectify=True).bucket
      return obj
   
   # .........................................
   def getBucketShapegridData(self, filePath, expId, bucketId, intersected=False):
      """
      @summary: Gets a bucket's shapegrid as a shapefile
      @param filePath: The path of the location to save this file
      @param expId: The experiment containing the bucket
      @param bucketId: The id of the bucket to get the shapegrid for
      @param intersected: (optional) If True, returns intersected layers in the
                             shapefile, else returns the shapgrid itself
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/%sshapefile" % \
               (self.cl.server, expId, bucketId, 
                "" if intersected else "shapegrid/")
      sf = self.cl.makeRequest(url, method="GET")
      try:
         open(filePath, 'wb').write(sf)
      except Exception, _:
         return False
      return True
   
   # .........................................
   def getBucketSitesPresent(self, filePath, expId, bucketId):
      """
      @summary: Gets the sites present for a bucket (original pamsum) as a 
                   pickle
      @param filePath: The path of the location to save this file
      @param expId: The experiment containing the bucket
      @param bucketId: The id of the bucket to get the shapegrid for
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/presence" % \
               (self.cl.server, expId, bucketId)
      resp = self.cl.makeRequest(url, method="GET")
      try:
         open(filePath, 'w').write(resp)
      except Exception, _:
         return False
      return True
   
   # .........................................
   def listBuckets(self, expId, afterTime=None, beforeTime=None, page=0, 
                                               perPage=100, fullObjects=False):
      """
      @summary: Lists buckets for a user
      @param expId: The id of the experiment to list buckets for
      @param afterTime: List buckets with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: List buckets with creation times before this time 
                            (ISO 8601 format)
      @param page: The page of results
      @param perPage: The number of results per page
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/experiments/%s/buckets" % (self.cl.server, expId)
      bkts = self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("fullObjects", int(fullObjects))])
      return bkts
   
   # .........................................
   def addBucket(self, expId, shpName, cellShape, cellSize, mapUnits, epsgCode, bbox, cutout=None):
      """
      @summary: Adds a bucket to an experiment
      @param expId: The id of the experiment to add a bucket to
      @param shpName: The name of this new bucket's shapegrid
      @param cellShape: The shape of the cells for the shapegrid
      @param cellSize: The size of the cells in mapUnits
      @param mapUnits: The units of the cell size (ie: dd for decimal degrees)
      @param epsgCode: The EPSG code representing the projection of the bucket
      @param bbox: The bounding box for the new bucket
      @param cutout: (optional) WKT representing the area to cut out
      """
      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>addbucket</ows:Identifier>
  <wps:DataInputs>
      <wps:Input>
         <ows:Identifier>bucket</ows:Identifier>
         <wps:Data>
            <wps:ComplexData>
               <lmRad:shapegrid>
                  <lmRad:name>%s</lmRad:name>
                  <lmRad:cellShape>%s</lmRad:cellShape>
                  <lmRad:cellSize>%s</lmRad:cellSize>
                  <lmRad:mapUnits>%s</lmRad:mapUnits>
                  <lmRad:epsgCode>%s</lmRad:epsgCode>
                  <lmRad:bounds>%s</lmRad:bounds>
%s
               </lmRad:shapegrid>
            </wps:ComplexData>
         </wps:Data>
      </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" % (shpName, cellShape, cellSize, mapUnits, epsgCode, bbox, "                 <lmRad:cutout>%s</lmRad:cutout>" % cutout if cutout is not None else "")
      
      url = "%s/services/rad/experiments/%s/addbucket" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"},
                                objectify=True)
      if obj.Status.ProcessSucceeded is not None:
         return obj.Status.ProcessOutputs.Output.Data.LiteralData.value
      else:
         return False

   # .........................................
   def addBucketByShapegridId(self, expId, shpId):
      """
      @summary: Adds a bucket to an experiment
      @param expId: The id of the experiment to add a bucket to
      @param shpId: The id of the shapegrid to use for this bucket
      """
      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>addbucket</ows:Identifier>
  <wps:DataInputs>
      <wps:Input>
         <ows:Identifier>bucket</ows:Identifier>
         <wps:Data>
            <wps:ComplexData>
               <lmRad:shapegridId>%s</lmRad:shapegridId>
            </wps:ComplexData>
         </wps:Data>
      </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" % shpId
      
      url = "%s/services/rad/experiments/%s/addbucket" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"},
                                objectify=True)
      if obj.Status.ProcessSucceeded is not None:
         return obj.Status.ProcessOutputs.Output.Data.LiteralData.value
      else:
         return False

   # .........................................
   def intersectBucket(self, expId, bucketId):
      """
      @summary: Requests that an intersection is performed against a bucket or
                   all of the buckets in an experiment
      @param expId: The id of the experiment to perform intersections for
      @param bucketId: The id of the bucket to intersect.
      """
      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>intersect</ows:Identifier>
  <wps:DataInputs>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" 
      
      url = "%s/services/rad/experiments/%s/%sintersect" % (self.cl.server, expId, 
               "buckets/%s/" % bucketId if bucketId is not None else "")
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"},
                                objectify=True)
      if obj.Status.ProcessAccepted is not None:
            return lambda : self.getStatusStage(self.getBucket(expId, bucketId))
      else:
         return False

   # .........................................
   def randomizeBucket(self, expId, bucketId, method='swap', numSwaps=10000):
      """
      @summary: Requests that a bucket be randomized
      @param expId: The id of the experiment containing the bucket to randomize
      @param bucketId: The id of the bucket to randomize
      @param method: (optional) The randomization method to use (swap | splotch)
      @param numSwaps: (optional) The number of successful swaps to perform
      """
      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>randomize</ows:Identifier>
  <wps:DataInputs>
      <wps:Input>
         <ows:Identifier>randomizeMethod</ows:Identifier>
         <wps:Data>
            <wps:LiteralData>%s</wps:LiteralData>
         </wps:Data>
      </wps:Input>
      <wps:Input>
         <ows:Identifier>numSwaps</ows:Identifier>
         <wps:Data>
            <wps:LiteralData>%s</wps:LiteralData>
         </wps:Data>
      </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" % (method, numSwaps)
   
      url = "%s/services/rad/experiments/%s/buckets/%s/randomize" % (
                                                                  self.cl.server, 
                                                                  expId, 
                                                                  bucketId)
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"},
                                objectify=True)
      if obj.Status.ProcessAccepted is not None:
         return lambda : self.getStatusStage(self.getBucket(expId, bucketId))
      else:
         return False
   
   # .........................................
   def getOriginalPamCsv(self, experimentId, bucketId, headers=False, filePath=None):
      """
      @summary: Get the experiment's bucket's orginal pam in CSV format
      @param experimentId: The experiment containing buckets
      @param bucketId: The bucket to return
      @param headers: (optional) Add column headers and centroids to response
      @note: Will probably change in release
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/csv%s" % (self.cl.server, 
                                                        experimentId, bucketId,
                                                        "?addHeaders=1" if headers else "")
      cnt = self.cl.makeRequest(url, method="GET")
      if filePath is not None:
         try:
            open(filePath, 'w').write(cnt)
         except Exception, _:
            return False
      return cnt
   
   # Ancillary Layers
   # -----------------
   # .........................................
   def addAncLayer(self, expId, lyrId, attrValue=None, 
                   calculateMethod="weightedMean", minPercent=None):
      """
      @summary: Adds an ancillary layer to a RAD experiment
      @param expId: The id of the experiment to add the ancillary layer to
      @param lyrId: The id of the layer to add
      @param attrValue: (optional) The attribute value
      @param calculateMethod: (optional) The method used for calculation
      @param minPercent: (optional) The minimum percentage for presence
      @note: This service is still experimental and may not work as expected
      """
      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>addanclayer</ows:Identifier>
  <wps:DataInputs>
      <wps:Input>
         <ows:Identifier>ancLayer</ows:Identifier>
         <wps:Data>
            <wps:ComplexData>
               <lmRad:layerId>%s</lmRad:layerId>
               <lmRad:parameters>
%s%s%s
               </lmRad:parameters>
            </wps:ComplexData>
         </wps:Data>
      </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" % (lyrId,
       "                  <lmRad:attrValue>%s</lmRad:attrValue>\n" 
          % attrValue if attrValue is not None else "",
       "                  <lmRad:calculateMethod>%s</lmRad:calculateMethod>\n" 
          % calculateMethod if calculateMethod is not None else "",
       "                  <lmRad:minPercent>%s</lmRad:minPercent>\n" 
          % minPercent if minPercent is not None else "",
      )
      
      url = "%s/services/rad/experiments/%s/addanclayer" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"}, 
                                objectify=True)
      if obj.Status.ProcessSucceeded is not None:
         return True
      else:
         return False
   
   # .........................................
   def getAncillaryLayer(self, expId, ancLyrId):
      """
      @summary: Get a specific ancillary layer
      @param expId: The experiment that the ancillary layer belongs to
      @param ancLyrId: The id of the ancillary layer
      """
      url = "%s/services/rad/experiments/%s/anclayers/%s/xml"
      obj = self.cl.makeRequest(url, method="GET", objectify=True).layer
      return obj
   
   # .........................................
   def listAncillaryLayers(self, expId, afterTime=None, beforeTime=None, 
                                 epsgCode=None, layerId=None, layerName=None, 
                                 page=0, perPage=100, ancillaryValueId=None, 
                                 fullObjects=False):
      """
      @summary: Lists Ancillary layers for a user
      @param expId: The id of the experiment to list ancillary layers for
      @param afterTime: List ancillary layers with creation times after this 
                           time (ISO 8601 format)
      @param beforeTime: List ancillary layers with creation times before this 
                            time (ISO 8601 format)
      @param epsgCode: List ancillary layers with this EPSG code
      @param layerId: List ancillary layers that use the layer with this id
      @param layerName: List ancillary layers with layers that have this name
      @param page: The page of results
      @param perPage: The number of results per page
      @param ancillaryValueId: List ancillary layers that have the ancillary 
                                  values specified by this id
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/experiments/%s/anclayers" % (self.cl.server, expId)
      ancLyrs = self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("layerId", layerId),
                                              ("layerName", layerName),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("ancillaryValueId", ancillaryValueId),
                                              ("fullObjects", int(fullObjects))])
      return ancLyrs
   
   def countAncillaryLayers(self, expId, afterTime=None, beforeTime=None, 
                                 epsgCode=None, layerId=None, layerName=None, 
                                 ancillaryValueId=None):
      """
      @summary: Counts Ancillary layers for a user
      @param expId: The id of the experiment to count ancillary layers for
      @param afterTime: Count ancillary layers with creation times after this 
                           time (ISO 8601 format)
      @param beforeTime: Count ancillary layers with creation times before this 
                            time (ISO 8601 format)
      @param epsgCode: Count ancillary layers with this EPSG code
      @param layerId: Count ancillary layers that use the layer with this id
      @param layerName: Count ancillary layers with layers that have this name
      @param ancillaryValueId: Count ancillary layers that have the ancillary 
                                  values specified by this id
      """
      url = "%s/services/rad/experiments/%s/anclayers" % (self.cl.server, expId)
      return self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("layerId", layerId),
                                              ("layerName", layerName),
                                              ("ancillaryValueId", ancillaryValueId)
                                              ])

   # .........................................
   def getAncLayers(self, expId):
      """
      @summary: Get ancillary layers associated with an experiment
      @param expId: The id of the experiment to return layers for
      @note: This service is still experimental and the results may not be as 
                expected
      """
      url = "%s/services/rad/experiments/%s/anc" % (self.cl.server, expId)
      try:
         respObj = self.cl.makeRequest(url, method="GET", objectify=True)
         lyrs = respObj.layerset.layers
         if lyrs is not None:
            if not isinstance(lyrs, ListType):
               lyrs = [lyrs]
            return lyrs
         else:
            return []
      except Exception, _:
         return []
         
   # Presence / Absence Layers
   # --------------------------
   # .........................................
   def addPALayer(self, expId, lyrId, attrPresence, minPresence, 
                  maxPresence, percentPresence, attrAbsence=None, 
                  minAbsence=None, maxAbsence=None, percentAbsence=None):
      """
      @summary: Adds a presence / absence layer to an experiment
      @param expId: The id of the experiment to add this layer for
      @param lyrId: The id of the layer to add
      @param attrPresence: The attribute indicating presence
      @param minPresence: The minimum value indicating presence
      @param maxPresence: The maximum value indicating presence
      @param percentPresence: The proportion required to indicate presence
      @param attrAbsence: (optional) The attribute indicating absence
      @param minAbsence: (optional) The minimum value indicating absence
      @param maxAbsence: (optional) The maximum value indicating absence
      @param percentAbsence: (optional) The portion required to indicate absence
      """
      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>addpalayer</ows:Identifier>
  <wps:DataInputs>
      <wps:Input>
         <ows:Identifier>paLayer</ows:Identifier>
         <wps:Data>
            <wps:ComplexData>
               <lmRad:layerId>%s</lmRad:layerId>
               <lmRad:parameters>
%s%s%s%s%s%s%s%s
               </lmRad:parameters>
            </wps:ComplexData>
         </wps:Data>
      </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" % (lyrId,
       "                  <lmRad:attrPresence>%s</lmRad:attrPresence>\n" 
          % attrPresence if attrPresence is not None else "",
       "                  <lmRad:minPresence>%s</lmRad:minPresence>\n" 
          % minPresence if minPresence is not None else "",
       "                  <lmRad:maxPresence>%s</lmRad:maxPresence>\n" 
          % maxPresence if maxPresence is not None else "",
       "                  <lmRad:percentPresence>%s</lmRad:percentPresence>\n" 
          % percentPresence if percentPresence is not None else "",
       "                  <lmRad:attrAbsence>%s</lmRad:attrAbsence>\n" 
          % attrAbsence if attrAbsence is not None else "",
       "                  <lmRad:minAbsence>%s</lmRad:minAbsence>\n" 
          % minAbsence if minAbsence is not None else "",
       "                  <lmRad:maxAbsence>%s</lmRad:maxAbsence>\n" 
          % maxAbsence if maxAbsence is not None else "",
       "                  <lmRad:percentAbsence>%s</lmRad:percentAbsence>\n" 
          % percentAbsence if percentAbsence is not None else "",
      )
      
      url = "%s/services/rad/experiments/%s/addpalayer" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"},
                                objectify=True)
      if obj.Status.ProcessSucceeded is not None:
         return True
      else:
         return False
   
   # .........................................
   def getPresenceAbsenceLayer(self, expId, paLyrId):
      """
      @summary: Get a specific presence absence layer
      @param expId: The experiment that the presence absence layer belongs to
      @param ancLyrId: The id of the presence absence layer
      """
      url = "%s/services/rad/experiments/%s/palayers/%s/xml"
      obj = self.cl.makeRequest(url, method="GET", objectify=True).layer
      return obj
   
   # .........................................
   def listPresenceAbsenceLayers(self, expId, afterTime=None, beforeTime=None, 
                                 epsgCode=None, layerId=None, layerName=None, 
                                 page=0, perPage=100, presenceAbsenceId=None, 
                                 fullObjects=False):
      """
      @summary: Lists Presence Absence layers for a user
      @param expId: The id of the experiment to list PA layers for
      @param afterTime: List presence absence layers with creation times after 
                           this time (ISO 8601 format)
      @param beforeTime: List presence absence layers with creation times 
                            before this time (ISO 8601 format)
      @param epsgCode: List presence absence layers with this EPSG code
      @param layerId: List presence absence layers that use the layer with this 
                         id
      @param layerName: List presence absence layers with layers that have this 
                           name
      @param page: The page of results
      @param perPage: The number of results per page
      @param presenceAbsenceId: List presence absence layers that have the set 
                                   of presence absence values specified by this 
                                   id
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/experiments/%s/palayers" % (self.cl.server, expId)
      paLyrs = self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("layerId", layerId),
                                              ("layerName", layerName),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("presenceAbsenceId", presenceAbsenceId),
                                              ("fullObjects", int(fullObjects))])
      return paLyrs
   
   # .........................................
   def countPresenceAbsenceLayers(self, expId, afterTime=None, beforeTime=None, 
                                 epsgCode=None, layerId=None, layerName=None, 
                                 presenceAbsenceId=None):
      """
      @summary: Counts Presence Absence layers for a user
      @param expId: The id of the experiment to count PA layers for
      @param afterTime: Count presence absence layers with creation times after 
                           this time (ISO 8601 format)
      @param beforeTime: Count presence absence layers with creation times 
                            before this time (ISO 8601 format)
      @param epsgCode: Count presence absence layers with this EPSG code
      @param layerId: Count presence absence layers that use the layer with this 
                         id
      @param layerName: Count presence absence layers with layers that have this 
                           name
      @param presenceAbsenceId: Count presence absence layers that have the set 
                                   of presence absence values specified by this 
                                   id
      """
      url = "%s/services/rad/experiments/%s/palayers" % (self.cl.server, expId)
      return self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("layerId", layerId),
                                              ("layerName", layerName),
                                              ("presenceAbsenceId", presenceAbsenceId)])
   # .........................................
   def removePALayerFromExperiment(self, expId, paLyrId):
      """
      @summary: Removes a presence / absence layer from an experiment
      @param expId: The id of the experiment to remove the PA layer from
      @param paLyrId: The presence / absence layer id in the experiment to 
                         remove
      """
      url = "%s/services/rad/experiments/%s/palayers/%s" % (self.cl.server, 
                                                            expId, paLyrId)
      obj = self.cl.makeRequest(url, method="DELETE", objectify=True)
      return obj
   
   # .........................................
   def getPALayers(self, expId):
      """
      @summary: Get presence / absence layers associated with an experiment
      @param expId: The id of the experiment to return layers for
      """
      url = "%s/services/rad/experiments/%s/pa" % (self.cl.server, expId)
      try:
         respObj = self.cl.makeRequest(url, method="GET", objectify=True)
         lyrs = respObj.layerset.layers
         if lyrs is not None:
            if not isinstance(lyrs, ListType):
               lyrs = [lyrs]
            return lyrs
         else:
            return []
      except Exception, _:
         return []
         
   # Experiment Tree
   # --------------------------
   # .........................................
   def addTreeForExperiment(self, expId, filename=None, jTree=None):
      """
      @summary: Adds a json tree to an experiment
      @param expId: The id of the experiment to add this layer for
      @param filename: (optional) The file path where the tree can be found
      @param jTree: (optional) The tree data as a string
      @note: One of filename or jTree must be supplied
      """
      if filename is not None:
         jTree = open(filename).read() # Should throw error if file doesn't exist
      elif jTree is not None:
         if isinstance(jTree, dict):
            jTree = json.dumps(jTree)
         else:
            jTree = toUnicode(jTree)
      else:
         raise Exception, "Must specify either filename or jTree to add a tree to an experiment"

      postXml = """\
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
             xmlns="http://www.opengis.net/wps/1.0.0" 
             xmlns:wfs="http://www.opengis.net/wfs" 
             xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:lmRad="http://lifemapper.org"
             xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd">
  <ows:Identifier>addtree</ows:Identifier>
  <wps:DataInputs>
      <wps:Input>
         <ows:Identifier>jsonTree</ows:Identifier>
         <wps:Data>
            <wps:LiteralData>
               %s
            </wps:LiteralData>
         </wps:Data>
      </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/gml-3.1.1">
      <ows:Identifier>result</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
""" % (jTree)
      
      url = "%s/services/rad/experiments/%s/addtree" % (self.cl.server, expId)
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=[("request", "Execute")], 
                                body=postXml, 
                                headers={"Content-Type" : "application/xml"},
                                objectify=True)
      if obj.Status.ProcessSucceeded is not None:
         return True
      else:
         return False
   
   # .........................................
   def getTreeForExperiment(self, expId, filename=None):
      """
      @summary: Get the json tree for an experiment
      @param expId: The id of the experiment to return the tree for
      @param filename: (optional) If the file name is specified, save the file
      """
      url = "%s/services/rad/experiments/%s/tree" % (self.cl.server, expId)
      jTree = self.cl.makeRequest(url, method="GET", objectify=False)
         
      if filename is not None:
         with open(filename, 'w') as outF:
            outF.write(jTree)
      return json.loads(jTree)
         
   # PAM / Sums
   # -----------
   # .........................................
   def countPamSums(self, expId, bucketId, afterTime=None, beforeTime=None, 
                         randomized=1, randomMethod=None):
      """
      @summary: Counts pamsums for a user
      @param expId: The id of the experiment
      @param bucketId: The id of the bucket
      @param afterTime: Count pamsums with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: Count pamsums with creation times before this time 
                            (ISO 8601 format)
      @param randomized: 1 for random pamsums, 0 for original
      @param randomMethod: Return pamsums that were randomized with this method.
                              0-not random, 1-swap, 2-splotch
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/" % \
               (self.cl.server, expId, bucketId)
      return self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("randomized", randomized),
                                              ("randomMethod", randomMethod)])

   # .........................................
   def deletePamSum(self, expId, bucketId, pamSumId):
      """
      @summary: Deletes a Lifemapper RAD PAM Sum
      @param expId: The id of the experiment container
      @param bucketId: The id of the bucket containing the pamsum
      @param pamSumId: The id of the pamsum to delete
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/%s" % \
               (self.cl.server, expId, bucketId, pamSumId)
      obj = self.cl.makeRequest(url, method="DELETE", objectify=True)
      return obj
    
   # .........................................
   def getPamSum(self, expId, bucketId, pamSumId):
      """
      @summary: Returns a pamsum
      @param expId: The id of the experiment container
      @param bucketId: The id of the bucket containing the pamsum
      @param pamSumId: The id of the pamsum to return
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/%s" % \
               (self.cl.server, expId, bucketId, pamSumId)
      obj = self.cl.makeRequest(url, method="GET", objectify=True).pamsum
      return obj
   
   # .........................................
   def getPamSumCsv(self, expId, bucketId, pamSumId, headers=False, filePath=None):
      """
      @summary: Returns a pamsum in CSV format
      @note: Jeff, this function will be something different in the release
      @param expId: The id of the experiment container
      @param bucketId: The id of the bucket containing the pamsum
      @param pamSumId: The id of the pamsum to return
      @param headers: (optional) Add column headers and centroids to response
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/%s/csv%s" % \
               (self.cl.server, expId, bucketId, pamSumId, 
                "?addHeaders=1" if headers else "")
      cnt = self.cl.makeRequest(url, method="GET")
      if filePath is not None:
         try:
            open(filePath, 'w').write(cnt)
         except Exception, _:
            return False
      return cnt

   # .........................................
   def getPamSumShapegrid(self, filePath, experimentId, bucketId, pamsumId):
      """
      @summary: Gets the shapegrid containing pamsum data
      @param filePath: The local location to store the file
      @param experimentId: The id of the experiment container
      @param bucketId: The id of the bucket containing the pamsum
      @param pamsumId: The id of the pamsum to return intersected with the 
                         shapegrid
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/%s/shapefile" %\
               (self.cl.server, experimentId, bucketId, pamsumId)
      sf = self.cl.makeRequest(url, method="GET")
      try:
         open(filePath, 'wb').write(sf)
      except Exception, _:
         return False
      return True
   
   # .........................................
   def getPamSumStatistic(self, expId, bucketId, pamSumId, stat):
      """
      @summary: Gets the available statistics for a pamsum
      @param expId: The id of the RAD experiment
      @param bucketId: The id of the RAD bucket
      @param pamSumId: The id of the pamsum to get statistics for
      @param stat: The key of the statistic to return
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/%s/statistics" %\
                        (self.cl.server, expId, bucketId, pamSumId)
      statResp = self.cl.makeRequest(url, 
                                     method="GET", 
                                     parameters=[("statistic", stat)]).strip()
      ret = []
      if len(statResp.split('\n')) > 1:
         for line in statResp.split('\n'):
            if len(line.split(' ')) > 1:
               ret.append([i for i in line.split(' ')])
            else:
               ret.append(line)
      else:
         if len(statResp.split(' ')) > 1:
            ret = [i for i in statResp.split(' ')]
         else:
            ret = statResp.strip()
      return ret

   # .........................................
   def getPamSumStatisticsKeys(self, expId, bucketId, pamSumId, keys="keys"):
      """
      @summary: Gets the available statistics for a pamsum
      @param expId: The id of the RAD experiment
      @param bucketId: The id of the RAD bucket
      @param pamSumId: The id of the pamsum to get statistics for
      @param keys: (optional) The type of keys to return
                               (keys | specieskeys | siteskeys | diversitykeys)
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/%s/statistics" %\
                  (self.cl.server, expId, bucketId, pamSumId)
      keyResp = self.cl.makeRequest(url, 
                                    method="GET", 
                                    parameters=[("statistic", keys)]).strip()
      keys = keyResp.split(' ')
      return keys

   # .........................................
   def listPamSums(self, expId, bucketId, afterTime=None, beforeTime=None, 
                         page=0, perPage=100, randomized=1, randomMethod=None, 
                         fullObjects=False):
      """
      @summary: Lists pamsums for a user
      @param expId: The id of the experiment
      @param bucketId: The id of the bucket
      @param afterTime: List pamsums with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: List pamsums with creation times before this time 
                            (ISO 8601 format)
      @param page: The page of results
      @param perPage: The number of results per page
      @param randomized: 1 for random pamsums, 0 for original
      @param randomMethod: Return pamsums that were randomized with this method.
                              0-not random, 1-swap, 2-splotch
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/experiments/%s/buckets/%s/pamsums/" % \
               (self.cl.server, expId, bucketId)
      return self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("randomized", randomized),
                                              ("randomMethod", randomMethod),
                                              ("fullObjects", int(fullObjects))])

   # -------------------------------------------------------------------------
   
   # =========================================================================
   # =                                Layers                                 =
   # =========================================================================
   # .........................................
   def countLayers(self, afterTime=None, beforeTime=None, epsgCode=None, 
                         layerName=None):
      """
      @summary: Counts layers for a user
      @param afterTime: Count layers with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: Count layers with creation times before this time 
                            (ISO 8601 format)
      @param epsgCode: Count layers with this EPSG code
      @param layerName: Count layers that match this name
      """
      url = "%s/services/rad/layers" % self.cl.server
      lyrs = self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("layerName", layerName)])
      return lyrs
   
   # .........................................
   def deleteLayer(self, layerId):
      """
      @summary: Deletes a layer from Lifemapper
      @param layerId: The id of the layer to delete
      """
      url = "%s/services/rad/layers/%s" % (self.cl.server, layerId)
      obj = self.cl.makeRequest(url, method="DELETE", objectify=True)
      return obj
   
   # .........................................
   def getLayer(self, layerId):
      """
      @summary: Gets a layer metadata object
      @param layerId: The id of the layer to return
      """
      url = "%s/services/rad/layers/%s" % (self.cl.server, layerId)
      obj = self.cl.makeRequest(url, method="GET", objectify=True).layer
      return obj
   
   # .........................................
   def listLayers(self, afterTime=None, beforeTime=None, epsgCode=None,
                        layerName=None, page=0, perPage=100, fullObjects=False):
      """
      @summary: Lists layers for a user
      @param afterTime: List layers with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: List layers with creation times before this time 
                            (ISO 8601 format)
      @param epsgCode: List layers with this EPSG code
      @param layerName: Return layers that match this name
      @param page: The page of results
      @param perPage: The number of results per page
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/layers" % self.cl.server
      # @todo: Does this need userId in params?
      lyrs = self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("layerName", layerName),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("fullObjects", int(fullObjects))])
      return lyrs
   
   # .........................................
   def postRaster(self, name, filename=None, layerUrl=None, layerContent=None,
                  epsgCode=4326, title=None, bbox=None, startDate=None, 
                  endDate=None, mapUnits="dd", resolution=None, valUnits=None, 
                  dataFormat="GTiff", valAttribute=None, description=None, 
                  keywords=[]):
      """
      @summary: Uploads a raster layer to Lifemapper to be used in experiments
      @param name: The name of this layer
      @param filename: (optional) The local location of the raster file to 
                          upload (note that this, layerUrl, or layerContent
                          must be specified)
      @param layerUrl: (optional) The remote location (URL) of the raster file
                          to add to Lifemapper (note that this, filename, or
                          layerContent must be specified)
      @param layerContent: (optional) The string representation of the raster
                              layer to be uploaded.  Note that filename, 
                              layerUrl, or layerContent must be supplied.
      @param epsgCode: (optional) The EPSG code representing the projection
                          of this layer
      @param title: (optional) The title of this uploaded layer
      @param bbox: (optional) The bounding box for this layer
      @param startDate: (optional) The start date associated with the 
                           measurements of this layer
      @param endDate: (optional) The end date associated with the measurements
                         of this layer
      @param mapUnits: (optional) The units associated with the size of the 
                          cells in the raster
      @param resolution: (optional) The resolution of the cells in this raster
      @param valUnits: (optional) The units associated with the values in this
                          raster
      @param dataFormat: (optional) The format of this raster
      @param valAttribute: (optional) The attribute associated with value
      @param description: (optional) A description of this raster layer
      @param keywords: (optional) A list of keywords associated with this raster
      """
      p = [
           ("name" , name),
           ("title", title),
           ("bbox", bbox),
           ("startDate", startDate),
           ("endDate", endDate),
           ("mapUnits", mapUnits),
           ("resolution", resolution),
           ("epsgCode", epsgCode),
           ("valUnits", valUnits),
           ('raster', 1),
           #("gdalType", gdalType),
           ("dataFormat", dataFormat),
           ("valAttribute", valAttribute),
           ("description", description),
          ]
      for kw in keywords:
         p.append(("keyword", kw))
      url = "%s/services/rad/layers" % self.cl.server
      if filename is not None:
         body = open(filename, 'rb').read()
         headers = {"Content-Type" : CONTENT_TYPES[dataFormat]}
      elif layerContent is not None:
         body = layerContent
         headers = {"Content-Type" : CONTENT_TYPES[dataFormat]}
      elif layerUrl is not None:
         p.append(("layerUrl", layerUrl))
         headers = {}
         body = None
      else:
         raise Exception, "Either layerUrl, filename, or layerContent must be specified when posting a raster layer"
         
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=p, 
                                body=body,
                                headers=headers,
                                objectify=True)
      return obj.layer

   # .........................................
   def postVector(self, name, filename=None, layerUrl=None, layerContent=None,
                  epsgCode=4326, title=None, bbox=None, startDate=None, 
                  endDate=None, mapUnits="dd", resolution=None, valUnits=None, 
                  dataFormat="ESRI Shapefile", valAttribute=None, 
                  description=None, keywords=[]):
      """
      @summary: Uploads a vector layer to Lifemapper to be used in experiments
      @param name: The name of this layer
      @param filename: (optional) The local location of the vector file to 
                          upload (note that this, layerUrl, or layerContent 
                          must be specified)
      @param layerUrl: (optional) The remote location (URL) of the vector file
                          to add to Lifemapper (note that this, filename, or
                          layerContent must be specified)
      @param layerContent: (optional) The content of the vector layer to be 
                              posted.  Please note that filename, layerUrl, or
                              layerContent must be suppplied.
      @param epsgCode: (optional) The EPSG code representing the projection
                          of this layer
      @param title: (optional) The title of this uploaded layer
      @param bbox: (optional) The bounding box for this layer
      @param startDate: (optional) The start date associated with the 
                           measurements of this layer
      @param endDate: (optional) The end date associated with the measurements
                         of this layer
      @param mapUnits: (optional) The units associated with the distances of 
                          the vector layer
      @param resolution: (optional) The resolution of this vector layer
      @param valUnits: (optional) The units associated with the values in this
                          vector
      @param dataFormat: (optional) The format of this vector
      @param valAttribute: (optional) The attribute associated with value
      @param description: (optional) A description of this vector layer
      @param keywords: (optional) A list of keywords associated with this vector
      """
      p = [
           ("name" , name),
           ("title", title),
           ("bbox", bbox),
           ("startDate", startDate),
           ("endDate", endDate),
           ("mapUnits", mapUnits),
           ("resolution", resolution),
           ("epsgCode", epsgCode),
           ("valUnits", valUnits),
           ('vector', 1),
           #("ogrType", ogrType),
           ("dataFormat", dataFormat),
           ("valAttribute", valAttribute),
           ("description", description),
          ]
      for kw in keywords:
         p.append(("keyword", kw))
      url = "%s/services/rad/layers" % self.cl.server

      if filename is not None:
         if filename.endswith('.zip'):
            body = open(filename, 'rb').read()
         else:
            body = self.cl.getAutozipShapefileStream(filename)
         headers = {"Content-Type" : "application/x-gzip"}
      elif layerContent is not None:
         body = layerContent
         headers = {"Content-Type" : "application/x-gzip"}
      elif layerUrl is not None:
         p.append(("layerUrl", layerUrl))
         headers = {}
         body = None
      else:
         raise Exception, "Either layerUrl, filename, or layerContent must be specified when posting a vector layer"
         
      obj = self.cl.makeRequest(url, 
                                method="POST", 
                                parameters=p, 
                                body=body,
                                headers=headers,
                                objectify=True)
      
      return obj.layer
   
   
   # -------------------------------------------------------------------------
   
   # =========================================================================
   # =                              Shape Grids                              =
   # =========================================================================
   
   # .........................................
   def countShapegrids(self, afterTime=None, beforeTime=None, epsgCode=None, 
                            cellSides=None, layerId=None, layerName=None):
      """
      @summary: Counts shapegrids for a user
      @param afterTime: Count shapegrids with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: Count shapegrids with creation times before this time 
                            (ISO 8601 format)
      @param epsgCode: The epsg code of the shapegrids to count
      @param cellSides: The number of sides for each cell of the shapegrids.
                           Use 4 for square grids and 6 for hexagonal.
      @param layerId: Count shapegrids with this layer id
      @param layerName: Count shapegrids with this layer name
      """
      url = "%s/services/rad/shapegrids/" % self.cl.server
      return self.cl.getCount(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("cellSides", cellSides),
                                              ("layerId", layerId),
                                              ("layerName", layerName)])
      
   # .........................................
   def deleteShapegrid(self, shpId):
      """
      @summary: Deletes a shapegrid from the Lifemapper system
      @param shpId: The id of the shapegrid to delete
      """
      url = "%s/services/rad/shapegrids/%s" % (self.cl.server, shpId)
      obj = self.cl.makeRequest(url, method="DELETE", objectify=True)
      return obj

   # .........................................
   def getShapegrid(self, shpId):
      """
      @summary: Returns a shapegrid's metadata
      @param shpId: The id of the shapegrid to return
      """
      url = "%s/services/rad/shapegrids/%s" % (self.cl.server, shpId)
      obj = self.cl.makeRequest(url, method="GET", objectify=True).layer
      return obj

   # .........................................
   def listShapegrids(self, afterTime=None, beforeTime=None, epsgCode=None, 
                            cellSides=None, layerId=None, layerName=None, 
                            page=0, perPage=100, fullObjects=False):
      """
      @summary: Lists shapegrids for a user
      @param afterTime: List shapegrids with creation times after this time 
                           (ISO 8601 format)
      @param beforeTime: List shapegrids with creation times before this time 
                            (ISO 8601 format)
      @param epsgCode: The epsg code of the shapegrids to return
      @param cellSides: The number of sides for each cell of the shapegrids.
                           Use 4 for square grids and 6 for hexagonal.
      @param layerId: Return shapegrids with this layer id
      @param layerName: Return shapegrids with this layer name
      @param page: The page of results
      @param perPage: The number of results per page
      @param fullObjects: (optional) If True, return the full objects instead
                             of the list objects
      """
      url = "%s/services/rad/shapegrids/" % self.cl.server
      return self.cl.getList(url, parameters=[("afterTime", afterTime), 
                                              ("beforeTime", beforeTime),
                                              ("epsgCode", epsgCode),
                                              ("cellSides", cellSides),
                                              ("layerId", layerId),
                                              ("layerName", layerName),
                                              ("page", page),
                                              ("perPage", perPage),
                                              ("fullObjects", int(fullObjects))])
      
   # -------------------------------------------------------------------------
   
   # =========================================================================
   # =                           Helper Functions                            =
   # =========================================================================
   # .........................................
   def getStatusStage(self, obj):
      """
      @summary: Gets that status and stage of an object
      @param obj: The object to get the status and stage of
      @return: status, stage 
      """
      try:
         status = obj.status
      except:
         status = None
      try:
         stage = obj.stage
      except:
         stage = None
      return status, stage
      
   # -------------------------------------------------------------------------
