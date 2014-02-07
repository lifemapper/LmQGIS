# -*- coding: utf-8 -*-
"""
@author: Jeff Cavner
@contact: jcavner@ku.edu

@license: gpl2
@copyright: Copyright (C) 2014, University of Kansas Center for Research

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


SIGNUPURL = "http://Lifemapper.org/signup"
DEFAULT_POST_USER = "anon"
DEFAULT_USER = "lm2"
#WEBSITE_ROOT = "http://sporks.nhm.ku.edu"
WEBSITE_ROOT = "http://lifemapper.org"
LM_CLIENT_VERSION_URL = "http://lifemapper.org/clients/versions.xml"
#
SHAPEFILE_EXTENSIONS = ["shp", "shx", "dbf", "prj", "sbn", 
                        "sbx", "fbn", "fbx", "ain", "aih", 
                        "ixs", "mxs", "atx", "cpg"]
CONTENT_TYPES = {
                 "AAIGrid" : "text/plain",
                 "GTiff" : "image/tiff"
                }

#LMRADTYPE = 'rad'
#LMSDMTYPE = 'sdm'

class QGISProject:
   NOEXPID = -999
   NOPROJECT = 'noproject'
   NOUSER = '3166256m.,?K}_)Ir'
   NOWS = 'noWS'
   NOOCC = 'noOcc'

class GridConstructor:
   BASE_URL = ""
   STATUS_URL = None
   REST_URL = ""
   #comment
   
class listPALayers:
   pass
   
   
class ListExperiments:
   BASE_URL = ""
   STATUS_URL = None
   REST_URL = ""
   X_VECTOR = ''
   Y_VECTOR = ''  
     
class RetrievEML:
   EML_PATH = ''
   
class PopulateGrid:
  
   BASE_URL = ""
   STATUS_URL = None
   REST_URL = ""
      
class NewUser:
   
   BASE_URL = None
   STATUS_URL = None
   REST_URL = None
   
class SignIn:
   pass


class RADStatTypes:
   
   STATTYPES = {"speciesrichness":'sites',
                        "meanproportionalrangesize":'sites',
                        "proportionalspeciesdiversity":'sites',
                        "localityrangesize":'sites',
                        "speciesrangesize":'species',
                        "meanproportionalspeciesdiversity":'species',
                        "proportionalrangesize":'species',
                        "rangerichness":'species',
                        "whittakersbeta":'diversity',
                        "ladditivebeta":'diversity',
                        "legendrebeta":'diversity',
                        "sigmaspecies":'matrix',
                        "sigmasites":'marix',
                        "compositioncovariance":'Schluter',
                        "rangecovariance":'Schluter'}


class RandomizeMethods:
# ............................................................................
   NOT_RANDOM = 0
   SWAP = 1
   SPLOTCH = 2
   # these are not used in the client, specifically because I think
   # the post is using the words 'swap','splotch'

RASTER_EXTENSION = '.tif'
ZIP_EXTENSION = '.zip'
SHAPEFILE_EXTENSION = '.shp'
STAGELOOKUP =    {0:'initial',10:'intersect',20:'compressed',30:'randomized',40:'calculate',500:'notify'}
STAGEREVLOOKUP = {'initial':0,'intersect':10,'compressed':20,'randomized':30,'calculate':40,'notify':500}


PER_PAGE = 100

STATUSLOOKUP = {0:'general',1:'initialized',10:'in queue',11:'accepted by cluster',\
                15:'dispatch complete',20:'in waiter queue',21:'dispatched to node',\
                22: 'cluster wrote file',25:'done waiting',30:'in retriever queue',\
                90:'pull requested',100:'pull complete',\
                110:'compute init',120:'running',130:'computed',140:'push requested',\
                150:'pushed',200:'push complete',210:"ready to notify",300:'completed',1000:'error'}

STATUSREVLOOKUP = {'general':0,'initialized':1,'in queue':10,'accepted by cluster':11,\
                  'dispatch complete':15,'in waiter queue':20,'dispatched to node':21,\
                  'cluster wrote file':22,'done waiting':25,'in retriever queue':30,\
                  'pull requested':90,'pull complete':100,\
                  'compute init':110,'running':120,'computed':130,'push requested':140,\
                  'pushed':150,'push complete':200,'ready to notify':210,'completed':300,'error':1000}
# ............................................................................
class JobStage:
# ............................................................................
   """ 
   Constants to define the stages of an RADJob (Experiment, Bucket, or PamSum).
   """
   # ==========================================================================   
   #                               Valid Stage for RAD Experiment                          
   # ==========================================================================
   # This RAD object has not yet been processed
   GENERAL = 0
   # _RadIntersectJob contains RADExperiment 
   INTERSECT = 10
   # _RadCompressJob contains RADBucket or PamSum 
   COMPRESS = 20
   # _RadRandomizeJob contains PamSum
   RANDOMIZE = 30
   
   #SWAP = 31
   #SPLOTCH = 32
   # _RadCalculateJob contains PamSum
   CALCULATE = 40
   
   #           Valid Stage for SDM Jobs and Objects                     
   # ==========================================================================
   # SDMModelJob contains SDMModel 
   MODEL = 110
   # SDMProjectionJob contains SDMProjection 
   PROJECT = 120
   # ==========================================================================   
   #           Valid Stage for Notification Jobs and Objects                     
   # ==========================================================================
   # This Job object is complete, and the user must be notified
   NOTIFY = 500

class JobFamily:
# ............................................................................
   SDM = 1
   RAD = 2
   
# ............................................................................
class ReferenceType:
# ............................................................................
   SDMModel = 101
   SDMProjection = 102
   RADExperiment = 201
   Bucket = 202
   OriginalPamSum = 203
   RandomPamSum = 203

   
# ............................................................................
class JobStatus:
# ............................................................................
   """ 
   Constants to define the steps of a discrete Job within a pipeline.
   """
   # ==========================================================================
   # Pull / Push job statuses.  Replaces old older statuses
   GENERAL = 0
   INITIALIZE = 1
   PULL_REQUESTED = 90
   PULL_COMPLETE = 100
   COMPUTE_INITIALIZED = 110
   RUNNING = 120
   COMPUTED = 130
   PUSH_REQUESTED = 140
   PUSHED = 150
   PUSH_COMPLETE = 200
#    NOTIFY_READY = 210
   RETRIEVE_COMPLETE = 300
   
   GENERAL_ERROR = 1000 # repeated below
   PUSH_FAILED = 1100

   # ==========================================================================

   
   # ==========================================================================   
   #                               Valid status                              =
   # ==========================================================================
   # Created
   #GENERAL = 0
   # Ready to Dispatch (Pre-conditions met)
   #INITIALIZE = 1
   # In Pipeline Dispatcher Queue (Status.QUEUED/2)
   DISPATCH_QUEUE = 10
   # Queued on frontend (OMJobStatus.QUEUED/10)
   CLUSTER_ACCEPTED = 11
   # Pipeline Dispatcher completed (Status.JOB_DISPATCHED/3)
   DISPATCH_COMPLETE = 15
   # In Waiter Queue (Status.JOB_BEGIN/4)
   WAIT_QUEUE = 20 
   # Frontend successfully dispatched to Node (OMJobStatus,DISPATCHED/11)
   CLUSTER_DISPATCHED = 21
   # model or projection file successfully written to the node (OMJobStatus,COMPLETED/12)
   CLUSTER_COMPLETED = 22
   # Waiter completed (Status.JOB_COMPLETE/5)
   WAIT_COMPLETE = 25
   # In Retriever Queue (Status.JOB_RETRIEVE/6)
   RETRIEVE_QUEUE = 30
   # Job retrieved and written (Status.JOB_CATALOGUED/7)
   # model or projection file successfully deleted from the node 
   # and/or local database
   CLUSTER_DELETED = 36
   # Obsolete (Status.OBSOLETE/9)
   OBSOLETE = 60
   # (OMJobStatus.EXPIRED/14)
   CLUSTER_EXPIRED = 61
   
   # Not found in database, could be prior to insertion
   NOT_FOUND = 404

   # ==========================================================================   
   # =                             General Errors                             =
   # ==========================================================================
   #GENERAL_ERROR = 1000
   UNKNOWN_ERROR = 1001
   
   # ==========================================================================   
   # =                            Lifemapper Errors                           =
   # ==========================================================================
   
   
SERVICE = "service=wps"
VERSION = "version=1.0.0"
#...............................................................................
STATUS_ACCEPTED  = "Accepted"
STATUS_STARTED   = "Started"
STATUS_FAILED    = "Failed"
STATUS_SUCCEEDED = 300

#...............................................................................
GENERIC_REQUEST = 1
EXECUTE_REQUEST = 2
#...............................................................................
FIND_STATUS = "{http://www.opengis.net/wps/1.0.0}Status"

STATUS_FAILED_EXCEPTION = '{http://www.opengis.net/wps/1.0.0}Status/{http://www.opengis.net/wps/1.0.0}ProcessFailed/{http://www.opengis.net/wps/1.0.0}ExceptionReport/{http://www.opengis.net/ows/1.1}Exception'
DATA_ELEMENT_PATH = '{http://www.opengis.net/wps/1.0.0}ProcessOutputs/{http://www.opengis.net/wps/1.0.0}Output/{http://www.opengis.net/wps/1.0.0}Data'
