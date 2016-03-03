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
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.etree.ElementTree as ET
from lifemapperTools.common.model import RequestModel
from LmClient.lmClientLib import LMClient
from lifemapperTools.common.pluginconstants import  GENERIC_REQUEST,EXECUTE_REQUEST
from LmCommon.common.lmconstants import JobStatus
import pdb



# .............................................................................

class _Controller:
   
   """
   Controller Class, subclasses can override accept button function
   """
   


   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, BASE_URL=None, STATUS_URL=None, REST_URL=None,
                cancel_close=None, okayButton=None, ids=None,
                initializeWithData=False, outputfunc=None, requestfunc=None,
                client=None, inputs={}):
      """
      @param initialREST: flag for REST instead of WPS for first call,needs
      to be replaced
      @param iface: QGIS interface object
      @param mode: describe process or execute mode, deprecated
      @param BASE_URL: constant for the url of a particular process
      @param STATUS_URL: constant for checking on status of a process
      @param cancel_close: cancel close button from dialog
      @param okayButton: Accept button from dialog
      @param inputGroup: input group object from dialog
      @param outputGroup: output group object from dialog
      @param statuslabel: statuslabel object from dialog
      @param progressbar: progress bar object from dialog
      @param ids: dictionary of ids from previous processes
      """
      
      self.RADids = ids
      self.REST_URL = REST_URL
      self.BASE_URL = BASE_URL
      self.STATUS_URL = STATUS_URL
      self.iface = iface
      self.cancel_close = cancel_close 
      self.buttonOk = okayButton
      self.clientmethod = requestfunc
      self.outputfunction = None
      
      if client is None:
         client = LMClient()         
      if initializeWithData:
         # the model, because of thread and signals, has to live in the 
         # thread and the client lives in the model, so here we 
         # just send it the client
         self.startThread(GENERIC_REQUEST,outputfunc=outputfunc, 
                          requestfunc=self.clientmethod, client=client,
                          inputs=inputs)
         

# ............................................................................. 
   def cancelThread( self ):
      """
      @summary: cancel thread, is connected to cancel_stop button after
      doWPS is called
      """
      
      self.wpsThread.stop()      
  
# .............................................................................   
   def wpsThreadFinished(self, output):
      """
      @summary: gets called when a thread finishes, receives results and 
      informs the dialog
      @param output: tuple with results which are python deserialized
      objects, and the current model instance
      """
      
      
      results = output[0]
      model = output[1]
      type = output[2]
      callOutputonError = output[3]
      self.cancel_close.setText("Close")
      
      #QObject.disconnect( self.cancel_close, SIGNAL( "clicked()" ), self.cancelThread )
      #QObject.disconnect( self.wpsThread, SIGNAL("wpsFinished(PyQt_PyObject)"), self.wpsThreadFinished)
      #QObject.disconnect( self.wpsThread, SIGNAL("wpsStatus(PyQt_PyObject)"), self.wpsThreadStatus)
      
      self.cancel_close.clicked.disconnect(self.cancelThread)
      self.wpsThread.wpsFinished.disconnect(self.wpsThreadFinished)
      self.wpsThread.wpsStatus.disconnect(self.wpsThreadStatus)
      
      if self.wpsThread.error == 0:
         # needs to just use one function here maybe called setDialog,
         # output could include, the type, and given that do WPS types of
         # output messaging, like Process Succeeded
         if type == GENERIC_REQUEST:
            self.outputfunction(results, model)            
         if type == EXECUTE_REQUEST:
            self.statuslabel.setText('Process Succeeded')
            self.outputfunction(results, model)          
      else:
         self.statuslabel.setText('Process Failed')
         self.buttonOk.setEnabled(False)
         if not callOutputonError:
            QMessageBox.warning(self,"error",str(self.wpsThread.error))
         else:
            self.outputfunction(results, model) 
            

# .............................................................................         
   def wpsThreadStatus(self, progress):
      """
      @summary: updates the progress bar
      @param progress: progress percentage
      """ 
           
      self.progressbar.setValue(progress)

# .............................................................................          
   def accept( self ):
      """
      @summary: method connected to accept button, can be overridden in the
      subclass if there is a standard Ok button
      """     
      pass

# ..............................................................................
   def startThread(self, type, requestfunc=None, outputfunc=None, model=None,
                   inputs={}, client=None, completedStage=None, 
                   statusFunctions = None, callOutputonError=False):
      """
      @summary: builds and starts a thread for a WPS process, the only way
      the model should be sent to the thread is if it starts there 
      in the first place, in other words as part of an iterative 
      set of requests, like if it starts with a DescribeProcess request
      """
      
      self.outputfunction = outputfunc
      self.buttonOk.setEnabled( False )
      self.wpsThread = WPSThread(self.iface.mainWindow(),
                                 type, 
                                 self.inputGroup.children(),
                                 model, 
                                 self.BASE_URL,
                                 self.STATUS_URL,
                                 self.RADids,
                                 requestfunc=requestfunc,
                                 inputs=inputs,
                                 client=client,
                                 completedStage=completedStage,
                                 statusFunctions=statusFunctions,
                                 callOutputonError=callOutputonError)
      
      
      #QObject.connect( self.wpsThread, SIGNAL("wpsFinished(PyQt_PyObject)"), self.wpsThreadFinished)
      #QObject.connect( self.wpsThread, SIGNAL("wpsStatus(PyQt_PyObject)"), self.wpsThreadStatus)
      
      self.wpsThread.wpsFinished.connect(self.wpsThreadFinished)
      self.wpsThread.wpsStatus.connect(self.wpsThreadStatus)
      
      self.cancel_close.setText("Cancel")
      #self.connect( self.cancel_close, SIGNAL("clicked()"), self.cancelThread )
      self.cancel_close.clicked.connect(self.cancelThread)
      self.wpsThread.start()

      
class WPSThread(QThread):
   """
   WPS Thread class, subclasses QThread
   """
   wpsFinished = pyqtSignal(tuple)
   wpsStatus = pyqtSignal(int)
# .............................................................................
# Constructor
# .............................................................................
  
   def __init__(self, parentThread, type, inputchildren, model, baseurl, statusurl,
               ids, requestfunc=None,inputs=None, client=None,completedStage=None,
               statusFunctions=None,callOutputonError=False):
      
      QThread.__init__(self,parentThread)
      self.client = client        
      self.RADids = ids
      self.BASE_URL = baseurl
      self.STATUS_URL = statusurl
      self.children = inputchildren
      self.running = False
      self.requestType = type        
      self.threadinputs = inputs
      self.progress = 0
      self.clientmethod = requestfunc
      self.completedStage = completedStage
      self.statusFunctions = statusFunctions
      self.callOutputonError = callOutputonError

         
# .............................................................................     
   def run(self):
      
      self.running = True
      self.model = RequestModel(client=self.client, url=self.BASE_URL, 
                                   getStatusUrl=self.STATUS_URL)     
      if self.requestType == GENERIC_REQUEST:
         self.error = 0
         self.genericRequest()
      if self.requestType == EXECUTE_REQUEST:
         self.error = 0
         self.results, self.model = self.executeProcess()   
      
      #self.emit( SIGNAL( "wpsFinished(PyQt_PyObject)" ), (self.results, self.model,
      #                                                    self.requestType) )
      self.wpsFinished.emit((self.results,self.model,self.requestType,self.callOutputonError))

# .............................................................................         
   def httpError(self, msgtype, http):
      
      messageString = msgtype+" "+http
      self.error = messageString
      
# .............................................................................    
   def stop(self):
      
      self.running = False 
# .............................................................................
   def executeProcess(self):      
      """
      @summary: builds executeModel and posts against it
      """
      #QObject.connect( self.model, SIGNAL("HTTPError"), self.httpError)
      #QObject.connect( self.model, SIGNAL("DocumentError"), self.documentError)
      
      self.model.HTTPError.connect(self.httpError)
      try:
            # first call just gets the status function
            callBacks = []
            callBack = self.model.executeRequest(requestfunc=self.clientmethod,
                                                   inputs=self.threadinputs)
            callBacks.append(callBack)
            if callBack == "error":
               raise Exception, "error in model's execute request"
            if self.statusFunctions is not None:
               callBacks = self.statusFunctions
            # here we call the status function through a method in the
            # model to get the status the first time, function is returned as 
            # a lambda populated with args
            status, stage = self.model.getStatus(requestfunc=callBacks[0])       
            status = int(status)
            stage = int(stage)  
      except Exception, e:
         return None, None
      else:
         if not(self.completedStage):
            if not(status >= JobStatus.GENERAL_ERROR):
               if status == JobStatus.COMPLETE:
                  #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), 100)  
                  self.wpsStatus.emit(100)                                   
                  return status, self.model  
               else:
                  callBackCounter = 0
                  for statusfunc in callBacks:
                     callBackCounter += 1
                     loops = 0
                     model = True
                     while (not(status >= JobStatus.GENERAL_ERROR) and status != JobStatus.COMPLETE) or \
                     ((callBackCounter <= len(callBacks)) and not(status > JobStatus.COMPLETE)):
                        status, stage = self.model.getStatus(requestfunc=statusfunc)
                        status = int(status)
                        stage = int(stage)
                        if status != JobStatus.COMPLETE:
                           if self.progress == 100 and loops < 1:
                              self.progress = 0 
                              loops += 1
                           elif self.progress < 100 and loops < 1:
                              self.progress += 10
                           else:
                              break
                        else:
                           #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), 100)
                           self.wpsStatus.emit(100)
                           break
                                                          
                        #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), self.progress)
                        self.wpsStatus.emit(self.progress)
                        time.sleep(2)
                     if status >= JobStatus.GENERAL_ERROR:
                        # need to get a more informative error code here, like below                  
                        self.error = "error-status "+str(status)
                        model = False
                        break
                        #return status, None
                     elif status == JobStatus.COMPLETE:                
                        #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), 100)
                        self.wpsStatus.emit(100)
                        #return status, self.model
                     elif status != JobStatus.COMPLETE and status < JobStatus.GENERAL_ERROR:
                        model = False
                        #return status, None
                  if model:
                     return status, self.model
                  else:
                     return status, None
                  
            elif status >= JobStatus.GENERAL_ERROR:
               self.error = "status already above JobStatus.GENERAL_ERROR"
               return status, None
         else:
            if not(status >= JobStatus.GENERAL_ERROR):
               if stage == self.completedStage:
                  #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), 100)     
                  self.wpsStatus.emit(100)                                
                  return stage, self.model
               
               else:
                  callBackCounter = 0
                  for statusfunc in callBacks:
                     callBackCounter += 1
                     loops = 0
                     model = True
                     while ((stage < self.completedStage) and not(status > JobStatus.COMPLETE)) or \
                     ((callBackCounter <= len(callBacks)) and not(status > JobStatus.COMPLETE)):
                        status, stage = self.model.getStatus(requestfunc=statusfunc)
                        status = int(status)
                        stage = int(stage)
                        if stage != self.completedStage:  #!!!
                           if self.progress == 100 and loops < 1:
                              self.progress = 0 
                              loops += 1
                           elif self.progress < 100 and loops < 1:
                              self.progress += 10
                           else:
                              break
                        else:
                           #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), 100)
                           self.wpsStatus.emit(100)
                           break
                                                          
                        #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), self.progress)
                        self.wpsStatus.emit(self.progress)
                        time.sleep(2)
                     if status >= JobStatus.GENERAL_ERROR:       
                        self.error = "error-status "+str(status)
                        model = False
                        break
                        
                     elif stage == self.completedStage and status == JobStatus.COMPLETE:                
                        #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), 100)
                        self.wpsStatus.emit(100)
                        
                     elif JobStatus.COMPLETE < status < JobStatus.GENERAL_ERROR:
                        self.error = "cluster error or not found"
                        model = False
                        
                     elif status != JobStatus.COMPLETE and status < JobStatus.GENERAL_ERROR:
                        model = False
                        
                  if model:
                     return status, self.model
                  else:
                     return status, None
                  
            elif status >= JobStatus.GENERAL_ERROR:
               self.error = "status already above JobStatus.GENERAL_ERROR"
               return stage, None
              
# .............................................................................          
   def genericRequest(self):
      """
      @summary: describeProcess function, builds describeModel, connects signals
      retrieves data for the model
      @return: returns results from parsed model data, and describeModel
      """
      
      #QObject.connect( self.model, SIGNAL("HTTPError"), self.httpError)
      #QObject.connect( self.model, SIGNAL("DocumentError"), self.documentError)
      
      self.model.HTTPError.connect(self.httpError)
      
      try: 
       
         outputs,status = self.model.makeRequest(requestfunc=self.clientmethod,
                                                 inputs=self.threadinputs)        
      except Exception, e:
        
         self.results = None
         self.error = str(e)        
      else:
        
         self.progress = 100   #maybe                         
         #self.emit( SIGNAL( "wpsStatus(PyQt_PyObject)" ), self.progress)
         self.wpsStatus.emit(self.progress)
         self.results = outputs
      
         
         
      
      
   