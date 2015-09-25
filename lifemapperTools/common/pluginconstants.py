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

class ARCHIVE_DWL_TYPE:
   
   PROJ = 'projection'
   OCCURRENCE = 'occurrencset'

class Messages:
   
   INFO = 'info'
   WARNING = 'warning'


class Renderers:
   GRADUATED = 'graduated'
   CATEGORICAL = 'categorical'

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
   
   QGISLayerNames = ['Species Richness',
                     'Mean Proportional Range Size',
                     'Proportional Species Diversity',
                     "Per-site Range Size of a Locality",
                     'stats']
   
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

# TODO: get this from LmCommon.common.lmconstants




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


#...............................................................................

#...............................................................................
GENERIC_REQUEST = 1
EXECUTE_REQUEST = 2
#...............................................................................


