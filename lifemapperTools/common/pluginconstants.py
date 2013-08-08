# -*- coding: utf-8 -*-
"""
@license: gpl2
@copyright: Copyright (C) 2013, University of Kansas Center for Research

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
STAGELOOKUP =    {0:'initial',10:'calculated',20:'compressed',30:'randomized',40:'calculated'}
STAGEREVLOOKUP = {'initial':0,'intersected':10,'compressed':20,'randomized':30,'calculated':10}


PER_PAGE = 100

STATUSLOOKUP = {0:'general',1:'initialized',10:'in queue',11:'accepted by cluster',\
                15:'dispatch complete',20:'in waiter queue',21:'dispatched to node',\
                22: 'cluster wrote file',25:'done waiting',30:'in retriever queue',\
                90:'pull requested',100:'pull complete',\
                110:'compute init',120:'running',130:'computed',140:'push requested',\
                150:'pushed',200:'push complete',300:'completed',1000:'error'}

STATUSREVLOOKUP = {'general':0,'initialized':1,'in queue':10,'accepted by cluster':11,\
                  'dispatch complete':15,'in waiter queue':20,'dispatched to node':21,\
                  'cluster wrote file':22,'done waiting':25,'in retriever queue':30,\
                  'pull requested':90,'pull complete':100,\
                  'compute init':110,'running':120,'computed':130,'push requested':140,\
                  'pushed':150,'push complete':200,'completed':300,'error':1000}
# ............................................................................
class RADJobStage:
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
   LM_GENERAL_ERROR = 2000
   
   # Python errors
   # ............................................
   LM_PYTHON_ERROR = 2100
   LM_PYTHON_MODULE_IMPORT_ERROR = 2101
   LM_PYTHON_ATTRIBUTE_ERROR = 2102
   LM_PYTHON_EXPAT_ERROR = 2103

   # Lifemapper job errors
   # ............................................
   LM_JOB_ERROR = 2200
   LM_JOB_NOT_FOUND = 2201
   LM_JOB_NOT_READY = 2202
      
   # Lifemapper data errors
   # ............................................
   LM_DATA_ERROR = 2300
   LM_POINT_DATA_ERROR = 2300
   
   # Lifemapper Pipeline errors
   LM_PIPELINE_ERROR = 2400
   LM_PIPELINE_WRITEFILE_ERROR = 2401
   LM_PIPELINE_WRITEDB_ERROR = 2402
   LM_PIPELINE_UPDATEOCC_ERROR = 2403

   LM_PIPELINE_DISPATCH_ERROR = 2415

   # ==========================================================================   
   # =                           openModeller Errors                          =
   # ==========================================================================
   OM_GENERAL_ERROR = 3000
      
   # Error in request file
   # ............................................
   OM_REQ_ERROR = 3100
      
   # Algorithm error
   # ............................................
   OM_REQ_ALGO_ERROR = 3110
   OM_REQ_ALGO_MISSING_ERROR = 3111
   OM_REQ_ALGO_INVALID_ERROR = 3112
      
   # Algorithm Parameter error
   # ............................................
   # ............................................
   OM_REQ_ALGOPARAM_ERROR = 3120
   OM_REQ_ALGOPARAM_MISSING_ERROR = 3121
   OM_REQ_ALGOPARAM_INVALID_ERROR = 3122
   OM_REQ_ALGOPARAM_OUT_OF_RANGE_ERROR = 3123
    
   # Layer error
   # ............................................
   OM_REQ_LAYER_ERROR = 3130
   OM_REQ_LAYER_MISSING_ERROR = 3131
   OM_REQ_LAYER_INVALID_ERROR = 3132
   OM_REQ_LAYER_BAD_FORMAT_ERROR = 3134
   OM_REQ_LAYER_BAD_URL_ERROR = 3135
    
   # Points error
   # ............................................
   OM_REQ_POINTS_ERROR = 3140
   OM_REQ_POINTS_MISSING_ERROR = 3141
   OM_REQ_POINTS_OUT_OF_RANGE_ERROR = 3143
   
   # Projection error
   # ............................................
   OM_REQ_PROJECTION_ERROR = 3150
   
   # Coordinate system error
   # ............................................
   OM_REQ_COORDSYS_ERROR = 3160
   OM_REQ_COORDSYS_MISSING_ERROR = 3161
   OM_REQ_COORDSYS_INVALID_ERROR = 3162
   
   # Error in openModeller execution
   # ............................................
   OM_EXEC_ERROR = 3200
   
   # Error generating model
   # ............................................
   OM_EXEC_MODEL_ERROR = 3210
   
   # Error generating projection
   # ............................................
   OM_EXEC_PROJECTION_ERROR = 3220
    
   # ==========================================================================   
   # =                               HTTP Errors                              =
   # ==========================================================================
   # Last 3 digits are the http error code, only 400 and 500 levels listed
   HTTP_GENERAL_ERROR = 4000
      
   # Client error
   # ............................................
   HTTP_CLIENT_BAD_REQUEST = 4400
   HTTP_CLIENT_UNAUTHORIZED = 4401
   HTTP_CLIENT_FORBIDDEN = 4403
   HTTP_CLIENT_NOT_FOUND = 4404
   HTTP_CLIENT_METHOD_NOT_ALLOWED = 4405
   HTTP_CLIENT_NOT_ACCEPTABLE = 4406
   HTTP_CLIENT_PROXY_AUTHENTICATION_REQUIRED = 4407
   HTTP_CLIENT_REQUEST_TIMEOUT = 4408
   HTTP_CLIENT_CONFLICT = 4409
   HTTP_CLIENT_GONE = 4410
   HTTP_CLIENT_LENGTH_REQUIRED = 4411
   HTTP_CLIENT_PRECONDITION_FAILED = 4412
   HTTP_CLIENT_REQUEST_ENTITY_TOO_LARGE = 4413
   HTTP_CLIENT_REQUEST_URI_TOO_LONG = 4414
   HTTP_CLIENT_UNSUPPORTED_MEDIA_TYPE = 4415
   HTTP_CLIENT_REQUEST_RANGE_NOT_SATISFIABLE = 4416
   HTTP_CLIENT_EXPECTATION_FAILED = 4417

   # Server error
   # ............................................
   HTTP_SERVER_INTERNAL_SERVER_ERROR = 4500
   HTTP_SERVER_NOT_IMPLEMENTED = 4501
   HTTP_SERVER_BAD_GATEWAY = 4502
   HTTP_SERVER_SERVICE_UNAVAILABLE = 4503
   HTTP_SERVER_GATEWAY_TIMEOUT = 4504
   HTTP_SERVER_HTTP_VERSION_NOT_SUPPORTED = 4505
   
   # ==========================================================================   
   # =                             Database Errors                            =
   # ==========================================================================
   #   """
   #   Last digit meaning:
   #      0: General error
   #      1: Failed to read
   #      2: Failed to write
   #      3: Failed to delete
   #   """
   DB_GENERAL_ERROR = 5000
   
   # Job
   # ............................................
   DB_JOB_ERROR = 5100
   DB_JOB_READ_ERROR = 5101
   DB_JOB_WRITE_ERROR = 5102
   DB_JOB_DELETE_ERROR = 5103
   
   # Layer
   # ............................................
   DB_LAYER_ERROR = 5200
   DB_LAYER_READ_ERROR = 5201
   DB_LAYER_WRITE_ERROR = 5202
   DB_LAYER_DELETE_ERROR = 5203
   
   # Layer node
   # ............................................
   DB_LAYERNODE_ERROR = 5300
   DB_LAYERNODE_READ_ERROR = 5301
   DB_LAYERNODE_WRITE_ERROR = 5302
   DB_LAYERNODE_DELETE_ERROR = 5303
   
   # ==========================================================================   
   # =                                IO Errors                               =
   # ==========================================================================
   #   """
   #   Last digit meaning:
   #      0: General error
   #      1: Failed to read
   #      2: Failed to write
   #      3: Failed to delete
   #   """
   IO_GENERAL_ERROR = 6000
   
   # Model
   # ............................................
   IO_MODEL_ERROR = 6100

   # Model request
   # ............................................
   IO_MODEL_REQUEST_ERROR = 6110
   IO_MODEL_REQUEST_READ_ERROR = 6111
   IO_MODEL_REQUEST_WRITE_ERROR = 6112
   IO_MODEL_REQUEST_DELETE_ERROR = 6113
   
   # Model script
   # ............................................
   IO_MODEL_SCRIPT_ERROR = 6120
   IO_MODEL_SCRIPT_READ_ERROR = 6121
   IO_MODEL_SCRIPT_WRITE_ERROR = 6122
   IO_MODEL_SCRIPT_DELETE_ERROR = 6123

   # Model output
   # ............................................
   IO_MODEL_OUTPUT_ERROR = 6130
   IO_MODEL_OUTPUT_READ_ERROR = 6131
   IO_MODEL_OUTPUT_WRITE_ERROR = 6132
   IO_MODEL_OUTPUT_DELETE_ERROR = 6133
   
   # Projection
   # ............................................
   IO_PROJECTION_ERROR = 6200

   # Projection request
   # ............................................
   IO_PROJECTION_REQUEST_ERROR = 6210
   IO_PROJECTION_REQUEST_READ_ERROR = 6211
   IO_PROJECTION_REQUEST_WRITE_ERROR = 6212
   IO_PROJECTION_REQUEST_DELETE_ERROR = 6213
   
   # Projection script
   # ............................................
   IO_PROJECTION_SCRIPT_ERROR = 6220
   IO_PROJECTION_SCRIPT_READ_ERROR = 6221
   IO_PROJECTION_SCRIPT_WRITE_ERROR = 6222
   IO_PROJECTION_SCRIPT_DELETE_ERROR = 6223

   # Projection output
   # ............................................
   IO_PROJECTION_OUTPUT_ERROR = 6230
   IO_PROJECTION_OUTPUT_READ_ERROR = 6231
   IO_PROJECTION_OUTPUT_WRITE_ERROR = 6232
   IO_PROJECTION_OUTPUT_DELETE_ERROR = 6233
   
   # Layer
   # ............................................
   IO_LAYER_ERROR = 6300
   IO_LAYER_READ_ERROR = 6301
   IO_LAYER_WRITE_ERROR = 6302
   IO_LAYER_DELETE_ERROR = 6303
   
   # Matrix
   # ............................................
   IO_MATRIX_ERROR = 6400
   IO_MATRIX_READ_ERROR = 6401
   IO_MATRIX_WRITE_ERROR = 6402
   IO_MATRIX_DELETE_ERROR = 6403

   # Pickled RAD Objects
   # ............................................
   IO_INDICES_ERROR = 6500
   IO_INDICES_READ_ERROR = 6501
   IO_INDICES_WRITE_ERROR = 6502
   IO_INDICES_DELETE_ERROR = 6503

   # ==========================================================================   
   # =                               SGE Errors                               =
   # ==========================================================================
   SGE_GENERAL_ERROR = 7000
   SGE_BASH_ERROR = 7100
   
   
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
