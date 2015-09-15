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
from lifemapperTools.common.lmClientLib import LMClient as client
from lifemapperTools.common.pluginconstants import JobStatus
from urllib2 import HTTPError
PER_PAGE = 600
#from lmClientLib import LMClient as client

from LmServer.common.log import ConsoleLogger
from LM.common.peruser import Peruser
from LmServer.db.scribe import Scribe
me = client(userId='blank',pwd='blank')

exps = me.rad.listExperiments()

print exps

#bckts = me.rad.listBuckets(440,fullObjects=False)

#peruser = Peruser(ConsoleLogger(),overrideDB=HL_HOST)
#peruser.openConnections()

#scribe = Scribe(ConsoleLogger(),overrideDB=HL_HOST)
#scribe.openConnections()
#expids = [293,292,287,286,274]
#for id in expids:
#   
#   exp = peruser.getRADExperiment('demo', expid=id)
#   scribe.deleteRADExperiment(exp)
#   print "deleted ",id
#print 'deleted [293,292,287,286,274]'
# this bucket has one grid, and has been intersected, which also means it has been calculated
# and compressed, which means it has an original pamsum with the correct stage and status,
## that part works fine
#expId = 342
#bucketId = 411
#
## now we randomize it and would it expect it to create a new pamsum, which it does and then
## calculate the new pamsum, which it does (and writes the sum pickle), but then the status of the original pamsum gets changed
## from 300 to 10, which looks like a stage constant rather than a status
#statusFunction = me.randomizeBucket(expId=expId,bucketId=411,method='swap',iterations=123)
#
#
#layers = me.rad.getPALayers(205)
#
#currentLayerNames = []
##currentLayers = []
#for x in layers:
#   currentLayerNames.append(x.name.split(' ')[0])
#   #currentLayers.append(x.name.split(' Projection ')[0])
#print len(layers)
#currentGenusSet = set(currentLayerNames)
#genera = list(currentGenusSet)
#print genera
#
#tps = me.sdm.listTypeCodes(public=False,fullObjects=True)

#for t in tps:
#   print dir(t)
#exps = me.sdm.listExperiments()
#for x in exps:
#   print dir(x)
#exp = me.sdm.getExperiment(536523)

#print exp.description

#ps = me.rad.getPamSum(399,466,'original')
#layerCount = int(ps.pam.columnCount)
#print layerCount
#SDMexps = me.sdm.listExperiments()
#for exp in SDMexps:
#   try:
#      print exp.modTime
#   except:
#      print "no mod time on ",exp.id
#
#namedtuples = me.sdm.hint("Ursus")
#print len(namedtuples)
#frogToadGenera = ['Bufo','Rana','Ascaphus','Gastrophryne',"Hyla","Pseudacris"]
##futureSpecies = []
##
#currentSpecies = []
#frogToadProjGeneraTitles = []
#count = 0
#for genus in frogToadGenera:
#
#   projections = me.sdm.listProjections(displayName=genus, perPage=PER_PAGE,
#                                                     status=JobStatus.RETRIEVE_COMPLETE,public=True,
#                                                     scenarioId=34,algorithmCode="BIOCLIM",epsgCode=4326,
#                                                     fullObjects=True)
#   
#   for species in projections:
#      #futureSpecies.append(species)
#      if species.title.split(' ')[0] in frogToadGenera:
#         count += 1
#         currentSpecies.append(species)
#print count
##      
##print len(futureSpecies)
##    
##
##
#addAndUploaded = 0
#for species in currentSpecies:
#   try:
#      layerurl = me.sdm.getProjectionUrl(species.id,frmt="tiff")
#      postresponse = me.rad.postRaster(species.title,layerUrl=layerurl)
#   except:
#      print "could not post ",species.title
#   else:
#      try:
#         layerId = postresponse.id
#         inputs = {'attrPresence':'pixel','minPresence':127,
#                   'maxPresence':254, 'percentPresence':25,'lyrId':layerId,'expId':217}
#         addresponse = me.rad.addPALayer(**inputs)
#      except:
#         print "could not add ",species.title
#      else:
#         addAndUploaded += 1
#
#print "Added %s species to experiment 217" % (addAndUploaded)

#print dir(layers[0])
#occSets = me.sdm.listOccurrenceSets(perPage=400)
#titles = []
#for x in occSets:
#   titles.append(x.title)
#for y in occSets:
#   if '_' in y.title:  
#      title = y.title.replace('_',' ')  
#      if title in titles:
#         print y.id, "   ",y.title
#      else:
#         print y.title," not in list"
#

#scens = me.sdm.listScenarios(keyword=['observed'],epsgCode=4326,public=True)
#for s in scens:
#   print s.title
   
#success = me.rad.getBucketShapegridData('/home/jcavner/Heliconia/HeliconiaPAM_50_2.zip', 187, 190, intersected=True)
#print success


#   GENERAL = 0
#   INITIALIZE = 1
#   PULL_REQUESTED = 90
#   PULL_COMPLETE = 100
#   COMPUTE_INITIALIZED = 110
#   RUNNING = 120
#   COMPUTED = 130
#   PUSH_REQUESTED = 140
#   PUSHED = 150
#   PUSH_COMPLETE = 200
#   RETRIEVE_COMPLETE = 300
#   
#   GENERAL_ERROR = 1000 # repeated below
#   PUSH_FAILED = 1100
#
#   # ==========================================================================
#
#   
#   # ==========================================================================   
#   #                               Valid status                              =
#   # ==========================================================================
#   # Created
#   #GENERAL = 0
#   # Ready to Dispatch (Pre-conditions met)
#   #INITIALIZE = 1
#   # In Pipeline Dispatcher Queue (Status.QUEUED/2)
#   DISPATCH_QUEUE = 10
#   # Queued on frontend (OMJobStatus.QUEUED/10)
#   CLUSTER_ACCEPTED = 11
#   # Pipeline Dispatcher completed (Status.JOB_DISPATCHED/3)
#   DISPATCH_COMPLETE = 15
#   # In Waiter Queue (Status.JOB_BEGIN/4)
#   WAIT_QUEUE = 20 
#   # Frontend successfully dispatched to Node (OMJobStatus,DISPATCHED/11)
#   CLUSTER_DISPATCHED = 21
#   # model or projection file successfully written to the node (OMJobStatus,COMPLETED/12)
#   CLUSTER_COMPLETED = 22
#   # Waiter completed (Status.JOB_COMPLETE/5)
#   WAIT_COMPLETE = 25
#   # In Retriever Queue (Status.JOB_RETRIEVE/6)
#   RETRIEVE_QUEUE = 30
#   # Job retrieved and written (Status.JOB_CATALOGUED/7)
#   # model or projection file successfully deleted from the node 
#   # and/or local database
#   CLUSTER_DELETED = 36
#   # Obsolete (Status.OBSOLETE/9)
#   OBSOLETE = 60
#   # (OMJobStatus.EXPIRED/14)
#   CLUSTER_EXPIRED = 61










#projs = me.sdm.listProjections(perPage=300,fullObjects=True,status=300) #status=JobStatus.RETRIEVE_COMPLETE)
#print len(projs)
#for x in projs:
#   if x.status != '300':
#      print x.id, "  ",x.status," ",x.title
#      #pass
#   elif x.status == '300':
#      #print x.id
#      pass
#   

#types = me.sdm.listTypeCodes(public=False,fullObjects=True)
#print len(types)
#
#everything = 'testnew4'
#
#typecode = me.sdm.postTypeCode(everything, title=everything, description=everything)
#print typecode
#
#types = me.sdm.listTypeCodes(public=False,fullObjects=True)
#print len(types)

#scens = me.sdm.listScenarios(keyword=['observed'],public=True,epsgCode=2163)

##print len(scens)
#for s in scens:
#  try:
#   print s.title
#  except:
#   print s.id
#
#layers = me.sdm.listLayers(public=False,typeCode='RAINCODE',epsgCode=4326,fullObjects=True)

#print layers[0].typeCode
#print len(layers)


#fullShapeGridsDevel = me.rad.listShapegrids(fullObjects=True)
#print dir(fullShapeGridsDevel[0])
#
#fullRadlayersDevel = me.rad.listLayers(fullObjects=True)
#print dir(fullRadlayersDevel[0])
#
#fullexperimentsdevel = me.rad.listExperiments(fullObjects=True)
#
#print dir(fullexperimentsdevel[0])
#
#

#fullcodes = me.sdm.listTypeCodes(public=False,fullObjects=True)
#codeatoms =  me.sdm.listTypeCodes(public=False)
#for f,a in zip(fullcodes,codeatoms):
#  
#  try:  
#     print f.typeTitle," ",a.title, "           | f.typeTitle, and a.title"
#  except:
#     print f.typeCode," ",a.title, "            | f.typeCode, and a.title"

#d = {'expId': 118, 'fullObjects': True}
#count = me.rad.countBuckets(119)
#print 'count ',count
#fullbucketsdevel = me.rad.listBuckets(119,fullObjects=False)
#print fullbucketsdevel
#
##fullpamsumdevel = me.rad.listPamSums(114, 204, fullObjects=True)
#
#
#fullSDMLayersdevel = me.sdm.listLayers(fullObjects=True)
#print dir(fullSDMLayersdevel[0])
#
#fullSDMExpdevel = me.sdm.listExperiments(fullObjects=True)
#print dir(fullSDMExpdevel[0])
#
#fullOccDevel = me.sdm.listOccurrenceSets(fullObjects=True,epsgCode=3410)
#print dir(fullOccDevel[0]), fullOccDevel[0].maxX
##print dir(fullbucketsdevel[0])
#

#layers = me.rad.listLayers(layerName='Giraffa Projection 2dd064181',epsgCode='4326')

#print layers

#exps = me.sdm.listExperiments()

#print dir(exps[0])

#count = me.rad.countLayers(layerName='Giraffa Projection 2dddsfsdf064181',epsgCode=4326)
#print count

#fullProjsDevel = me.sdm.listProjections(fullObjects=True)
#for x in fullProjsDevel:
#   try:
#      print x.name
#   except:
#      print "printing title ",x.title
#print dir(fullProjsDevel[0])
#
#
#fullScensDevel = me.sdm.listScenarios(keyword=['observed'],public=True,fullObjects=True)
#print fullScensDevel[0].code

#print me.sdm.getExperiment(598963)

#projs = me.sdm.listProjections(displayName="Accipiter",
#                                                  status=300,public=False)
#print dir(projs[0])
#print len(projs)

#projs = me.sdm.listProjections(public=False)
#for x in projs:
#   print x.title
#print len(me.rad.listBuckets(**{'expId': 129, 'perPage': 20}))

#print me.rad.countExperiments()

#print me.rad.listPamSums(112, 202)
#
#exps = me.rad.listLayers()
#
#for x in exps:
#   print x.title
#
#
#shp = me.rad.listShapegrids(epsgCode=3410)
#for x in shp:
#   print x.epsgcode
#bucketCount = me.rad.countBuckets(120)
#print bucketCount
#status,stage = me.rad.getBucketStatus(79, 154)
#print status, stage
#2fadfa = me.sdm.getProjectionTiff(2356657,'/home/jcavner/dfafadasfasf.tif')
#exps = me.sdm.listExperiments()
#for exp in exps:
#   print exp.title,exp.modTime
#layers = me.sdm.listLayers(typeCode='RAINCODE',epsgCode=342)
#print 'layers ',layers

#print me.sdm.listTypeCodes()[0].title
#scenarios = me.sdm.listScenarios(keyword=['observed'])
#name = 'testDevRain23224343'
#epsgCode = 4326
#envLayerType = 'RAINCODE'
#units = 'dd'
#fileName = '/home/jcavner/workspaceOld/lm2/branches/cj/layerScenarioPosting/test/sampleData/rain_coolest.tif'
#result = me.sdm.postLayer(name, epsgCode, envLayerType, 
#                 units, fileName=fileName)
#
#print result.id
#for scenario in scenarios:
#  print dir(scenario)
   
#listToDelete = []
#for scen in scenarios:
#   if int(scen.id) >= 115:
#      print scen.id, ' ',scen.title
#      #
#      clientScenario = me.sdm.getScenario(int(scen.id))
#      code = clientScenario.code
#      scenario = peruser.getScenario(code)
#      listToDelete.append(scenario)
#
#print listToDelete      
#for scen in listToDelete:
#   print "deleting ",scen.title
#   scribe.deleteScenario(scen)
#   
#peruser.closeConnections()     
#scribe.closeConnections()
