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
import os
import types
import zipfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from lifemapperTools.tools.ui_listBucketsDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.tools.uploadLayers import UploadDialog
from lifemapperTools.tools.constructGrid import ConstructGridDialog
from lifemapperTools.tools.randomizePAM import RandomizePAMDialog
from lifemapperTools.tools.pamSumsStats import PamSumsStatsDialog
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.common.communicate import Communicate
from lifemapperTools.common.pluginconstants import ListExperiments, GENERIC_REQUEST, EXECUTE_REQUEST,\
                                         STAGELOOKUP, STAGEREVLOOKUP, STATUSLOOKUP, \
                                         STATUSREVLOOKUP, PER_PAGE, Messages 
from LmCommon.common.lmconstants import JobStage, JobStatus
from lifemapperTools.tools.radTable import  RADTable, RADTableModel                                       







class ListBucketsDialog(_Controller,QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, epsg=None,
                mapunits=None,resume=False):
      
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      self.interface = iface
      self.client = client
      self.workspace = Workspace(self.interface,self.client)
      self.inputs = inputs
      self.origPamSumId = None
      if resume:
         self.interface.addProject(resume)
      self.epsg = epsg
      if mapunits is None and self.epsg is not None:
         self.setMapUnits()
      else:   
         self.mapunits = mapunits
      buttonlist = self.buttonBox.buttons()
      cc = self.rejectBut
      bok = buttonlist[1]
      if inputs.has_key('expId'):
         self.expId = inputs['expId']
      else:
         self.expId = None
      _Controller.__init__(self, iface, cancel_close=cc, okayButton=bok,
                           initializeWithData=False,outputfunc=self.showTable,
                           requestfunc=self.client.rad.listBuckets, inputs=inputs,
                           client=client)
      
      if self.expId is not None:
         expFolder = self.workspace.getExpFolder(self.expId)
         if not expFolder:
            expFolder = self.workspace.createProjectFolder(self.expId)
         self.expDir = expFolder
      else:
         self.expDir = None
      
      try:
         firstTableInputs = {}
         firstTableInputs.update(inputs) 
         firstTableInputs.update({'perPage':PER_PAGE,'fullObjects':True})
         items = self.client.rad.listBuckets(**firstTableInputs) 
      except Exception, e:
         self.close()
         message = "There is a problem with the grids listing service. "+str(e)
         msgBox = QMessageBox.information(self,
                                          "Problem...",
                                          message,
                                          QMessageBox.Ok)
      else: 
         self.showTable(items)
         

# ..............................................................................         
   def setMapUnits(self): 
      """
      @summary: sets the map units attribute given the epsg of the experiment
      """
      crs = QgsCoordinateReferenceSystem()
      crs.createFromOgcWmsCrs('EPSG:%s'% (self.epsg))
      mapunitscode = crs.mapUnits()
      if mapunitscode == 0:
         self.mapunits = 'meters'
      elif mapunitscode == 1:
         self.mapunits = 'feet'
      elif mapunitscode == 2:
         self.mapunits = 'dd'

# ..............................................................................            
   def getPamSumStatusFunctions(self, bucketId, inputs):
      """
      @summary: builds a list of pamsum status functions, with params
      """
      ids = self.getRandomPamSumIds(inputs)
      statusFunctions = [lambda : self.client.rad.getPamSumStatus(self.expId, bucketId, 'original')]
      if len(ids) > 0:
         for id in ids:
            statusFunctions.append(lambda : self.client.rad.getPamSumStatus(self.expId, bucketId, id))
      return statusFunctions      
# ..............................................................................         
           
   def getRandomPamSumIds(self, inputs):
      newinputs = {}
      ids = []
      newinputs.update({'randomized':1})
      newinputs.update(inputs)
      pamsums = self.client.rad.listPamSums(**newinputs)
      for ps in pamsums:
         ids.append(ps.id)
      return ids
# ..............................................................................

   def checkforOrignalPAM(self,psparams):
      """
      @summary: checks for existence of orginal pam, returns boolean
      """
      
      try:
         checkinputs = psparams.copy()
         checkinputs.update({'randomized':0})
         items = self.client.rad.listPamSums(**checkinputs)
      except:
         QMessageBox.warning(self,"error: ",
                      "There is a problem with the pam service")
      else:
         if len(items) > 0:
            return True
         else:
            return False
      
# ..............................................................................    
   def listPamSums(self):
      """
      @summary: opens pamSumStats dialog
      """
      selectedrowindex = self.bucketTableView.tableView.selectionModel().currentIndex().row()
      selModel = self.bucketTableView.tableView.selectionModel()
      if selectedrowindex == -1 or not(selModel.hasSelection()):
         # or not (selectionModel().hasSelection())
         QMessageBox.warning(self,"status: ",
                         "Please select one Grid")
         return 
      selectedrow = self.bucketTableView.tableView.model().data[selectedrowindex]
      bucketId = selectedrow[1]
      listPSinputs = {}
      listPSinputs.update(self.inputs)
      listPSinputs.update({'bucketId':bucketId})     
      origPSCheck = self.checkforOrignalPAM(listPSinputs)     
      if origPSCheck:
         PSstagestatus = self.getPamSumStatus(self.expId,bucketId)
         origPamSumId = self.origPamSumId
         shpGrd = selectedrow[6]
         if PSstagestatus:
            PSstage = PSstagestatus[0]
            PSstatus = PSstagestatus[1]
            if PSstage == JobStage.CALCULATE and PSstatus == JobStatus.COMPLETE:
               pamsumstats = PamSumsStatsDialog(self.interface, inputs=listPSinputs,
                               client=self.client, parent=self, expEPSG=self.epsg,
                               gridName=self.gridName, origPamSumId = origPamSumId,
                               shpGrd=shpGrd) 
               self.close()
               pamsumstats.exec_()
            else:
               message = "Calculations have not been performed on this pam, wait for completed status"
               msgBox = QMessageBox.information(self,
                                       "Problem...",
                                       message,
                                       QMessageBox.Ok)
         else:
            message = "PAM status cannot be determined"
            msgBox = QMessageBox.information(self,
                                       "Problem...",
                                       message,
                                       QMessageBox.Ok)          
      else:
         message = "There are no pams for this grid, check if status is completed for intersect"
         msgBox = QMessageBox.information(self,
                                       "Problem...",
                                       message,
                                       QMessageBox.Ok)
# ..............................................................................      
   def addBucket(self):
      """
      @summary: adds a new bucket, spawns a construct grid dialog
      """
      if self.expId is not None:
         inputs = {'expId': self.expId}
         self.refreshBut.setEnabled(True)
         
         self.constructGridDialog = ConstructGridDialog( self.interface, inputs = inputs,
                                        client = self.client, epsg=self.epsg, parent=self, 
                                        mapunits=self.mapunits)
         self.setModal(False)
         self.constructGridDialog.show()
         
      else:
         QMessageBox.warning(self,"status: ", "No Experiment Id")     
# ..............................................................................         
   def intersectPAM(self):
      """
      @summary: intersects a PAM
      """
      
      selectedrowindex = self.bucketTableView.tableView.selectionModel().currentIndex().row()
      selModel = self.bucketTableView.tableView.selectionModel()
      if selectedrowindex == -1 or not(selModel.hasSelection()):
         QMessageBox.warning(self,"status: ",
                         "Please select one experiment")
         return 
      selectedrow = self.bucketTableView.tableView.model().data[selectedrowindex]
      stagestring = selectedrow[2]
      stage = self.getStageCode(stagestring)
      status = int(selectedrow[5])
      # this was: if stage == JobStage.GENERAL:
      if status == JobStatus.GENERAL:
         
         try:
            self.getStatsBut.setEnabled(False)
            #self.calcBut.setEnabled(False)
            self.intersectBut.setEnabled(False)
            self.addBucketBut.setEnabled(False)
            self.randomizeBut.setEnabled(False)
            self.refreshBut.setEnabled(False)
         except:
            pass
         try:
            # here we make sure there are layers for the experiment         
            layers = self.client.rad.getPALayers(self.expId)
         except Exception, e:
            canGetLyrs = False
         else:
            canGetLyrs = True
         if (layers is not None) and (len(layers) != 0) and (canGetLyrs):         
            
            self.hideButtonsWidget.hide()
            self.progressbar.show()
            if self.expId is not None:
               inputs = {'expId': self.expId}
            inputs.update({'bucketId':selectedrow[1]})
            self.bucketId = selectedrow[1]
            #self.startThread(EXECUTE_REQUEST,outputfunc = self.getShapeFile, 
            #                 requestfunc=self.client.rad.intersect, client=self.client,
            #                 inputs=inputs)
            try:
               statusStageFunc = self.client.rad.intersectBucket(**inputs)
               status, stage = statusStageFunc()
               status = int(status)
               stage = int(stage)
            except Exception,e:
               message = "Error in Intersect request %s" % (str(e))
               msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
               self.progressbar.hide()
               self.hideButtonsWidget.show()
               
            else:  # in preparation to replace with csv
               #self.getShapeFile(status, fromIntersect = True)
               statusMsg = self.getStatusString(status)
               message = "Intersect will be available later: status "
               self.showMessage(message, type=Messages.INFO, status = statusMsg)
               self.readyView()
            
         else:
            reply = QMessageBox.question(self, 'No layers to intersect',
                                               "Do you want to Add Layers?", QMessageBox.Yes | 
                                               QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
               d = UploadDialog(self.interface,inputs={'expId': self.expId},client=self.client,
                                epsg=self.epsg,mapunits=self.mapunits)
               d.exec_()
            #else:
            try:
               self.helpBut.setEnabled(True)
               self.getStatsBut.setEnabled(True)
               self.intersectBut.setEnabled(True)
               self.addBucketBut.setEnabled(True)
               self.randomizeBut.setEnabled(True)
               self.refreshBut.setEnabled(True)
            except:
               pass   
           
      else:
         message = "Grid has already been intersected"
         msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)            

# ..............................................................................            
   def randomizeBucket(self):  
      """
      @summary: randomized bucket
      """
      selectedrowindex = self.bucketTableView.tableView.selectionModel().currentIndex().row()
      selModel = self.bucketTableView.tableView.selectionModel()
      if selectedrowindex == -1 or not(selModel.hasSelection()):
         QMessageBox.warning(self,"status: ",
                         "Please select one experiment")
         return 
      try:
         self.getStatsBut.setEnabled(False)
         #self.calcBut.setEnabled(False)
         self.randomizeBut.setEnabled(False)
         self.addBucketBut.setEnabled(False)
         self.intersectBut.setEnabled(False)
         self.refreshBut.setEnabled(False)
      except:
         pass
      selectedrow = self.bucketTableView.tableView.model().data[selectedrowindex]
      bucketId = selectedrow[1]
      bucket = self.client.rad.getBucket(self.expId, bucketId)
      status, stage = self.client.rad.getStatusStage(bucket)
      #status, stage = self.client.rad.getBucketStatus(self.expId, bucketId)
      status = int(status)
      stage = int(stage)
      if stage >= JobStage.INTERSECT and status == JobStatus.COMPLETE:
         randominputs = {}
         randominputs.update(self.inputs)
         randominputs.update({'bucketId':bucketId})
         d = RandomizePAMDialog( self.interface, inputs = randominputs,
                                     client = self.client)
         d.exec_()
      else:
         QMessageBox.warning(self,"Problem: ",
                      "Grid has not been intersected")        
      try:
         self.helpBut.setEnabled(True)
         self.getStatsBut.setEnabled(True)
         #self.calcBut.setEnabled(True)
         self.randomizeBut.setEnabled(True)
         self.addBucketBut.setEnabled(True)
         self.intersectBut.setEnabled(True)
         self.refreshBut.setEnabled(True)
      except:
         pass

# ..............................................................................
   def readyView(self):
      """
      @summary: sets the dialog to normal, ready presentation
      """
      if self.progressbar.isVisible():
         self.progressbar.hide()
         self.hideButtonsWidget.show()
         self.refresh()
      
      if self.outputGroup.isVisible():
         self.outputGroup.hide()
         self.inputGroup.show()
         self.refresh()
         
      self.helpBut.setEnabled(True)
      self.getStatsBut.setEnabled(True)
      self.intersectBut.setEnabled(True)
      self.addBucketBut.setEnabled(True)
      self.randomizeBut.setEnabled(True)
      self.refreshBut.setEnabled(True)            

# ..............................................................................         
   def refresh(self):
      try:
         self.getStatsBut.setEnabled(False)
         self.intersectBut.setEnabled(False)
         self.addBucketBut.setEnabled(False)
         self.randomizeBut.setEnabled(False)
         self.refreshBut.setEnabled(False)
         
      except:
         pass
      try:
         currentPage = self.bucketDataView.model().currentPage
      except:
         # no current view, which means there isn't a table in case of exp with no
         # intial buckets
         currentPage = 0
      refreshinputs = {'expId':self.expId} 
      refreshinputs.update({'perPage':PER_PAGE,'fullObjects':True,'page':currentPage})
      try:
         items = self.client.rad.listBuckets(**refreshinputs) 
      except:
         pass
      else:
         self.addtoTable(items,None,currentPage)   
# ..............................................................................
   def getLayerCount(self):
      try:
         ps = self.client.rad.getPamSum(self.expId,self.bucketId,'original')
         
         layerCount = int(ps.pam.columnCount)
      except:
         
         layerCount = None
      return layerCount
# ..............................................................................


   def getPamCSV(self):
      # need filename and path
      error = None
      success = False
      if self.expDir is not None:
         self.pamFilePath = os.path.join(self.expDir,'pam_csv_%s.csv' % (str(self.bucketId)))
         if self.bucketId is not None and self.expId is not None:
            try:
               self.client.rad.getOriginalPamCsv(self.expId,self.bucketId,headers=True,filePath=self.pamFilePath) 
            except Exception, e:
               error = str(e)
            else:
               #print resp
               if os.path.exists(self.pamFilePath):
                  success = True              
      return success, error
   
# ..............................................................................
   def getShapeFile(self, status, fromIntersect=True): 
      """
      @deprecated: used to be called from download link in table, and on intersect
      """
      if status == JobStatus.COMPLETE:         
         if fromIntersect:
            columnCount = self.getLayerCount()
            if columnCount is not None:
               if columnCount > 245:
                  self.addtoCanvas(False)
               else:
                  self.addtoCanvas(True)
            else:
               QMessageBox.warning(self.outputGroup,"warning: ",
                               "Can't get layer count, calculations might not be done")                              
               self.readyView()
         else:
            self.addtoCanvas(False)
      else:
         # it only got in here from intersectPAM
         if status < JobStatus.COMPLETE:
            statusMsg = self.getStatusString(status)
            QMessageBox.warning(self.outputGroup,"status: ",
                                "Intersect will be available later: status "+statusMsg)
            
         if status > JobStatus.COMPLETE:
            statusMsg = self.getStatusString(status)
            QMessageBox.warning(self.outputGroup,"status: ",
                                "Unable to Intersect: status "+statusMsg)
         self.readyView()

# ..............................................................................
   def showMessage(self,message, type = Messages.INFO, status = ""):  
        
      if type == Messages.WARNING:         
         QMessageBox.warning(self,"status: ",
                                "%s %s" % (message,status))  
      if type == Messages.INFO:
         msgBox = QMessageBox.information(self,
                                              "Problem...",
                                               message,
                                               QMessageBox.Ok)      
# ..............................................................................

   def buildCSVLayer(self):
      # turn self.pamFilePath into URI, for all platforms
      url = QUrl.fromLocalFile(self.pamFilePath)
      url.addQueryItem('delimiter',',')
      url.addQueryItem('xField','centerX')  # probably use a constant here
      url.addQueryItem('yField','centerY')  # probably use a constant here
      
      pLayer = QgsVectorLayer(url.toString(),"pam_csv_%s" % (str(self.bucketId)),"delimitedtext")
      if not(pLayer.isValid()):
         pLayer = False
      return pLayer

# ..............................................................................

   def addJoin(self, pLayer, grdLyr):
      
      joinLyrId = pLayer.id()
      joinInfo = QgsVectorJoinInfo()
      joinInfo.memoryCache = True
      joinInfo.joinLayerId = joinLyrId
      joinInfo.joinFieldName = 'siteid'
      joinInfo.targetFieldName = 'siteid'
      grdLyr.addJoin(joinInfo)

# ..............................................................................
   def addGridtoMap(self, index):
      """
      @summary: gets called from table control for retrieving shapegrid
      @param index: QIndex from table view for selected row
      """
      if index.column() in self.bucketTableView.tableModel.controlIndexes:
         try:
            self.getStatsBut.setEnabled(False)
            #self.calcBut.setEnabled(False)
            self.intersectBut.setEnabled(False)
            self.addBucketBut.setEnabled(False)
            self.randomizeBut.setEnabled(False)
            self.refreshBut.setEnabled(False)
         except:
            pass
         else:
            self.bucketId = index.model().data[index.row()][1]
            stagestring = index.model().data[index.row()][2]
            stage = self.getStageCode(stagestring)
            status = int(index.model().data[index.row()][5])
            if stage >= JobStage.INTERSECT and status == JobStatus.COMPLETE:
               gridLyr,error = self.addtoCanvas()
               if gridLyr:
                  pamCSV, error = self.getPamCSV()
                  if pamCSV:
                     pLayer = self.buildCSVLayer() #self.pamFilePath, will be good
                     if pLayer:
                        try:
                           QgsMapLayerRegistry.instance().addMapLayer(pLayer,False)
                           self.addJoin(pLayer,gridLyr)
                        except Exception, e:
                           error = str(e)
                     if not pLayer or error is not None:
                        self.showMessage('could not join PAM',type=Messages.WARNING, status = error)                       
                  else:
                     message = "could not retrieve the PAM"
                     self.showMessage(message,type=Messages.WARNING, status = error)
               else:
                  message = "Could not retrieve the shapefile or layer is invalid"
                  self.showMessage(message,type=Messages.WARNING, status = error)
            elif (stage == JobStage.GENERAL and status == JobStatus.GENERAL) or \
                 (stage == JobStage.GENERAL and status == JobStatus.INITIALIZE):                 
                  
               gridLyr = self.addtoCanvas()
            else:
               QMessageBox.warning(self.outputGroup,"status: ",
                                "Grid must be successfully intersected or not in the middle of a process for download")
               try:
                  self.helpBut.setEnabled(True)
                  self.getStatsBut.setEnabled(True)
                  #self.calcBut.setEnabled(True)
                  self.intersectBut.setEnabled(True)
                  self.addBucketBut.setEnabled(True)
                  self.randomizeBut.setEnabled(True)
                  self.refreshBut.setEnabled(True)
               except:
                  pass

# ..............................................................................   
   def addtoCanvas(self):
      """
      @summary: connected to addtomap button, gets empty shapegrid and adds shapefile
      to map canvas
      @param intersected: bool 
      @return: returns vector layer added
      """
      #expFolder = self.workspace.getExpFolder(self.expId)
      #if not expFolder:
      #   expFolder = self.workspace.createProjectFolder(self.expId)
      error = None
      expFolder = self.expDir
      gridZipName = "%s_%s" % (str(self.expId),str(self.bucketId))
      pathname = os.path.join(expFolder,gridZipName)
      try:        
         self.client.rad.getBucketShapegridData(pathname, str(self.expId), str(self.bucketId))    
      except Exception, e:
         vectorLayer = False
         error = str(e)
      else:
         try:
            zippath = os.path.dirname(str(pathname))                         
            z = zipfile.ZipFile(str(pathname),'r')
            for name in z.namelist():
               f,e = os.path.splitext(name)
               if e == '.shp':
                  shapename = name
               z.extract(name,str(zippath))
            vectorpath = os.path.join(zippath,shapename)
            vectorLayer = QgsVectorLayer(vectorpath,self.gridName,'ogr')
         except Exception,e:
            vectorLayer = False
            error = str(e)           
         if not vectorLayer.isValid():
            vectorLayer = False               
         else:
            QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
      
      self.readyView()
      return vectorLayer, error              
        
# ..............................................................................  
   def cleanInputGridLayout(self):
      
      """@summary:  cleans out the input grid layout"""
     
      if not(self.gridLayout_input.isEmpty()):
         for childindex in range(0,self.gridLayout_input.count()):
            item = self.gridLayout_input.takeAt(0)
            if not(type(item) is types.NoneType):
               item.widget().deleteLater()
              
         self.gridLayout_input.update()  
         
   def appendData(self, items):
      
      data = []
      for o in items:
         calculate = False
         calculateDone = False
         status = int(o.status)
         stage = int(o.stage)
         if stage >= JobStage.INTERSECT:
            try:
               #print o.id," ",o.pamSum.stage
               if int(o.pamSum.stage) == JobStage.CALCULATE:
                  calculate = True
                  stage = JobStage.CALCULATE
                  status = int(o.pamSum.status)
            except:
               stage = JobStage.INTERSECT
         if status >= JobStatus.GENERAL_ERROR:
            statusstring = 'error'
         elif status == JobStatus.COMPLETE:
            calculateDone = True
            statusstring = STATUSLOOKUP[status]
         elif status == JobStatus.GENERAL: 
            statusstring = 'not started'
         elif status == JobStatus.INITIALIZE:
            statusstring = 'started'
         else:
            statusstring = "running" 
         try:
            shapegrid = o.shapegrid
         except:
            shapegrid = None 
         if calculate and calculateDone:
            gridOrPam = "PAM"
         else:      
            gridOrPam = "Grid"
         stagestring = self.getStageString(stage)
         data.append([o.name,int(o.id),stagestring,statusstring,"<a href='"+str(o.id)+"'>Get %s</a>" % (gridOrPam),o.status,shapegrid])
         
      return data

# ..............................................................................        
   def addtoTable(self,items,model,currentPage):
      """
      @summary: adds new grids (buckets) to the table upon refresh
      @param items: list of bucket objects
      """
      
      try:
         self.noListLabel.hide()
      except:
         pass 
      try: 
         # branch for if the table exists     
         header = ['  Grid title  ', '  Grid id  ', '  Stage  ', '  Status  ','  Retrieve Grid/PAM  ','','']
         data = self.appendData(items)
         self.bucketTableView.setNoPages(totalCount=len(items))
         self.bucketDataView.model().data = data
         self.bucketDataView.model().setNoPages(self.bucketTableView.noPages)
         self.bucketDataView.model().setCurrentPage(currentPage)
         
         
         self.bucketDataView.model().dataChanged.emit(QModelIndex(),QModelIndex())
         
         self.bucketTableView.viewport().update()
                  
      except Exception,e:
         # branch if the table doesn't exist
         self.showTable(items)
      try:
         self.helpBut.setEnabled(True)
         self.getStatsBut.setEnabled(True)
         self.intersectBut.setEnabled(True)
         self.randomizeBut.setEnabled(True)
         self.addBucketBut.setEnabled(True)
         self.refreshBut.setEnabled(True)
      except:
         pass    
# ..............................................................................   
   def getPamSumStatus(self,expId, bucketId):
      """
      @summary: gets the stage and status of the original pamsum
      @param expId: Lm expId
      @param bucketId: Lm bucketId
      """
      try:
         pamsum = self.client.rad.getPamSum(expId,bucketId,'original')
         status, stage = self.client.rad.getStatusStage(pamsum)
         #status, stage = self.client.rad.getPamSumStatus(expId,bucketId,'original')
      except Exception, e:
         #print "Exception in getPamSumStatus ",str(e)
         return False
      else:
         try:
            self.origPamSumId = pamsum.id
         except:
            pass
         return int(stage),int(status)
         
      
# ..............................................................................      
   def tablerowselected(self,itemselectionSelected,itemselectionDeselected):
      
      """
      @summary: if conditions are met emits signal to project instance to active
      Grid menu item
      @note: two things have to be true, origPS has to exist (grid intersected) and calc stage has to be
      completed on the PS
      """
      # getStageCode, getStatusCode
      self.gridName = str(itemselectionSelected.indexes()[0].data())
      shpGrd = itemselectionSelected.indexes()[6].data()
      origPamSumId = self.origPamSumId
      bucketId = itemselectionSelected.indexes()[1].data()
      bucketstage = str(itemselectionSelected.indexes()[2].data())
      stage =  self.getStageCode(bucketstage)
      status = int(itemselectionSelected.indexes()[5].data())
      self.activateButtons(stage,status,bucketId)
      if stage >= JobStage.INTERSECT and status == JobStatus.COMPLETE:
         #QgsProject.instance().emit( SIGNAL( "ActivateGrid(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)" ), self.expId, bucketId,stage,status)
         Communicate.instance().activateGrid.emit(self.expId, bucketId, stage, status, self.epsg, self.gridName, shpGrd)
               
   def activateButtons(self,bucketstage,bucketstatus,bucketId): 
      """
      @summary: activates and deactivates buttons based on combination of bucket stage and pamsum stage
      """ 
      
      if bucketstatus > JobStatus.GENERAL and bucketstage >= JobStage.INTERSECT:
         # this means a job has been sent
         self.intersectBut.setEnabled(False) 
         self.randomizeBut.setEnabled(True) 
         self.getStatsBut.setEnabled(True)    
      else:
         self.intersectBut.setEnabled(True)   
         self.getStatsBut.setEnabled(False)
         self.randomizeBut.setEnabled(False)
# ..............................................................................      
   def splitBucket(self):
      pass   

# ..............................................................................         
   def resizeEvent(self, event):
      pass
      #print self.size().width()
      #print self.size().height()  
# ..............................................................................         
   def getStageString(self,stage): 
      stageStr = 'undetermined'
      if STAGELOOKUP.has_key(stage):
         stageStr = STAGELOOKUP[stage] 
      return stageStr
# ..............................................................................   
   def getStageCode(self,stage):
      stageCode = 99
      if STAGEREVLOOKUP.has_key(stage):
         stageCode = STAGEREVLOOKUP[stage]
      return stageCode
# ..............................................................................   
   def getStatusString(self,status):
      statusStr = 'undetermined'
      if STATUSLOOKUP.has_key(status):
         statusStr = STATUSLOOKUP[status]
      return statusStr
# ..............................................................................   
   def getStatusCode(self,status):
      statusCode = 99
      if STATUSREVLOOKUP.has_key(status):
         statusCode = STATUSREVLOOKUP[status]
      return statusCode
      
      
# ...........................................................................
   def getBucketCount(self):
      try:
         count = self.client.rad.countBuckets(self.expId)
      except:
         count = None
      return count
# ...........................................................................   
   def listBuckets(self,pageSize=PER_PAGE,page=0):
      """
      @summary: lists buckets
      @return: returns a list of experiment atoms
      """
      items = None
      try:
         items = self.client.rad.listBuckets(self.expId,perPage=pageSize,page=page,fullObjects=True)
      except:
         items = None
         message = "There is a problem with the grid listing service"
         messageBox = QMessageBox.warning(self,
                                 "Problem...",
                                 message,
                                 QMessageBox.Ok)      
      return items
# ...........................................................................   
   def getNextPage(self,currentPage,forward):
      
      if forward:
         page = currentPage + 1  
      else:
         page = currentPage - 1  
      nextPage = self.listBuckets(page=page)
      if nextPage is not None:
         data = self.appendData(nextPage)
         
         self.bucketDataView.model().data = data
         self.bucketDataView.model().setCurrentPage(page)
         
         self.bucketDataView.model().dataChanged.emit(QModelIndex(),QModelIndex())

         readOut = "%s/%s" % (str(page+1),str(self.bucketTableView.noPages))
         self.bucketTableView.pageReadOut.clear()
         self.bucketTableView.pageReadOut.setText(readOut)
         if page == self.bucketTableView.noPages - 1:
            self.bucketTableView.pageForward.setEnabled(False)
         if page == 0:
            self.bucketTableView.pageBack.setEnabled(False)
         if forward:
            self.bucketTableView.pageBack.setEnabled(True)
         else:
            self.bucketTableView.pageForward.setEnabled(True)
      else:
         message = "Could not get the next page"
         msgBox = QMessageBox.warning(self,
                                                  "Problem...",
                                                  message,
                                                  QMessageBox.Ok)
# ..............................................................................           
   def showTable(self, items):
      bucketCount = self.getBucketCount()
      try:
         #data = []
         if len(items) == 0:
            raise Exception, "No Buckets"
         data = self.appendData(items)
         
         self.bucketTableView =  RADTable(data,totalCount=bucketCount)
         header = ['  Grid title  ', '  Grid id  ', '  Stage  ', '  Status  ','  Retrieve Grid/PAM  ','','']
         self.bucketDataView = self.bucketTableView.createTable(header,htmlIndexList=[4],
                                                                editsIndexList=[999],
                                                                controlsIndexList=[4],hiddencolumns=[5,6])
         #QObject.connect(self.bucketDataView.model(),SIGNAL("getMore(PyQt_PyObject,PyQt_PyObject)"),self.getNextPage)
         self.bucketDataView.model().getNext.connect(self.getNextPage)
         if self.bucketDataView.model().noPages == 1:
            self.bucketTableView.pageForward.setEnabled(False)
                   
         self.bucketDataView.selectionModel().selectionChanged.connect(self.tablerowselected)
         self.bucketDataView.clicked.connect(self.addGridtoMap)
         
         self.bucketDataView.setSelectionBehavior(QAbstractItemView.SelectRows)
         self.bucketDataView.setSelectionMode(QAbstractItemView.SingleSelection)
      
         self.gridLayout_input.addWidget(self.bucketTableView,1,2,3,1)
         # from row, from Column, rowSpan, columnSpan
         try:
            self.helpBut.setEnabled(True)
            self.getStatsBut.setEnabled(True)
            #self.calcBut.setEnabled(True)   
            self.intersectBut.setEnabled(True)
            self.addBucketBut.setEnabled(True)
            self.randomizeBut.setEnabled(True)
            self.refreshBut.setEnabled(True)
         except:
            pass
      except Exception, e:
         try:
            self.getStatsBut.setEnabled(False)
            #self.calcBut.setEnabled(False)
            self.intersectBut.setEnabled(False)
            self.addBucketBut.setEnabled(True)
            self.randomizeBut.setEnabled(False)
            self.refreshBut.setEnabled(False)
            #print "should have enabled refresh"
         except:
            pass
         self.noListLabel = QLabel(self.outputGroup)
         self.noListLabel.setObjectName('noList')
         self.noListLabel.setText("No grids to view")
         self.gridLayout_input.addWidget(self.noListLabel,1,2,2,1)
         message = "There are no grids for this experiment"
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
# ..............................................................................         
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('listgrids')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()

 
        
 

      
      
