 # -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2014 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

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
import time
import types
import sys
import zipfile
import urllib2
from types import StringType
from collections import namedtuple
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.tools.ui_postEnvLayer import PostEnvLayerDialog
from lifemapperTools.tools.ui_postSDMExp import Ui_Dialog
from lifemapperTools.tools.postOccSet import UploadOccSetDialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.tools.ui_postScenario import PostScenarioDialog
from lifemapperTools.common.communicate import Communicate
from LmCommon.common.lmconstants import MASK_TYPECODE
from lifemapperTools.common.pluginconstants import  QGISProject,GENERIC_REQUEST


# .............................................................................

def toUnicode(value, encoding='utf-8'):
   """
   @summary: Encodes a value for a element's text
   @param value: The object to make text
   @param encoding: (optional) The encoding of the text
   @todo: Encoding should be a constant
   """
   if isinstance(value, basestring):
      if not isinstance(value, unicode):
         value = unicode(value, encoding)
   else:
      value = unicode(str(value), encoding)
   return value
      
def fromUnicode(uItem, encoding="utf-8"):
   """
   @summary: Converts a unicode string to text for display
   @param uItem: A unicode object
   @param encoding: (optional) The encoding to use
   """
   return uItem.encode("utf-8")

class PostSDMExpDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   #__metaclass__ = classmaker()
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, inputs=None, client=None, email=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.workspace = Workspace(iface,client)
      self.setupUi()     
      self.email = email
      self.client = client
      self.algos = self.client.sdm.algos
      self.inputs = inputs 
      self.interface = iface 
      self.algSubWindow = None
      self.epsgCode = None
      self.occListModel = LmListModel([], self)
      self.occSetCombo.setModel(self.occListModel)
      self.BackSpaceEvent = BackSpaceEventHandler()
      self.occSetCombo.installEventFilter(self.BackSpaceEvent)
      self.userEnters = EnterTextEventHandler(self.occSetCombo,self.occListModel,self.download)
      self.occIdText.installEventFilter(self.userEnters)
      # build initial models and delegates
      self.scenProjListModel = LmListModel([], self)
      self.scenModelListModel = LmListModel([],self, model=True)
      self.maskListModel = LmListModel([MaskSearchResult('','')],self)
      #####################################
      self.projDelegate = SDMDelegate()
      self.modelDelegate = SDMDelegate()
      # set models and delegates for projections 
      self.projectionScenListView.setModel(self.scenProjListModel)
      self.modelScenCombo.setModel(self.scenModelListModel)
      self.projectionScenListView.setItemDelegateForRow(0,self.projDelegate)     
      self.modelScenCombo.setItemDelegate(self.modelDelegate)
      self.modelMaskCombo.setModel(self.maskListModel)
      self.projectionMaskCombo.setModel(self.maskListModel)
      
      
      _Controller.__init__(self, iface, cancel_close=self.rejectBut,okayButton=self.acceptBut,
                           initializeWithData=False, client=client)
      
     
      
      Communicate.instance().postScenarioFailed.connect(self.setModelCombo)
      Communicate.instance().postedScenario.connect(self.refreshScenarios)
      Communicate.instance().postedOccurrenceSet.connect(self.setExpValues)
      
      
      self.populateAlgoCombo()
      if iface is not None:
         self.checkExperiments()
# .....................................................................................
   def uploadNewMask(self):
      # need to be able to set epsg from occ set in upload dialog, and check layer 
      # that the user tries to upload for epsg
      if self.epsgCode is not None:
         self.uploadEnvLayerDialog = PostEnvLayerDialog(interface=self.interface,
                                                     client=self.client,parent=self,
                                                     epsgCode=self.epsgCode,fromMaskinSDM=True)
         self.uploadEnvLayerDialog.exec_()
# .....................................................................................   
   def getMaskLayers(self,typeCode=None,epsgCode=None,getFull=False):
      """
      @summary: gets a list of layer atoms
      @param typeCode: typeCode string to filter on from typeCode combo
      @param epsgCode: epsgCode [integer] to filter on
      @return: list of tuples (title, id)
      """
      #layers = []
      try:
         userMaskLyrs = self.client.sdm.listLayers(public=False,typeCode=typeCode,
                                                 epsgCode=epsgCode,fullObjects=getFull)         
      except Exception, e:
         print "EXCEPTION IN GET MASKS ",str(e)
      else:
         if len(userMaskLyrs) > 0:
            check = [int(x) for x in self.maskListModel.listData[1:]]
            data = list(self.maskListModel.listData)
            for lyr in userMaskLyrs:
               if int(lyr.id) not in check:
                  data.append(MaskSearchResult(lyr.name,lyr.id))
            self.maskListModel.updateList(data)
         self.maskGroup.setEnabled(True)
# .....................................................................................
   def setCombosToNewMask(self,newLyrName,id):
      
      
      data = list(self.maskListModel.listData)
      data.append(MaskSearchResult(newLyrName,id))
      self.maskListModel.updateList(data)
      self.modelMaskCombo.setCurrentIndex(self.modelMaskCombo.findText(newLyrName))
      self.projectionMaskCombo.setCurrentIndex(self.modelMaskCombo.findText(newLyrName))
      
# ......................................................................................    
   def refreshScenarios(self,postedScenId,match):  
   
      if match:
         currentModelIdx = self.modelScenCombo.currentIndex()
         self.populateProjScenCombo(currentModelIdx)
      else:     
         self.populateModelScenCombo(newScenId=int(postedScenId),epsg=self.epsgCode)
# ......................................................................................           
   def setModelCombo(self,match):
      if not match:
         self.modelScenCombo.setCurrentIndex(0)
# ......................................................................................       
   def checkExperiments(self):
      """
      @summary: gets the current expId, if there is one it gets the current
      project path associated with that id.  If there is a project path, it 
      triggers a save project.  If there is no path, it asks a save as, and sets 
      the project path for the id. The last thing it does is to open a new 
      qgis project
      """   
      s = QSettings()
      currentExpId  = s.value("currentExpID",QGISProject.NOEXPID,type=int)
      #############################
      # this saves any changes that might have been made if using an existing
      # experiment to that experiment's (existing) project
      project = QgsProject.instance()
      if project.fileName() != '':
         if project.isDirty():
            self.interface.actionSaveProject().trigger()
         
      #else:  July 24, 2013, why do we do anything if the project doesn't have a path/filename,
      #       in other words, its a new project and has layers
      #   if len(QgsMapLayerRegistry.instance().mapLayers().items()) > 0:
      #         #self.interface.actionSaveProjectAs().trigger()
      #         self.workspace.saveQgsProjectAs(currentExpId)
               
               
      s.setValue("currentExpID",QGISProject.NOEXPID) 
        
      
# ......................................................................................       
   def setNewExperiment(self):
      """
      @summary: sets the currentExpID key in settings and creates a project folder in workspace 
      and quietly save the new QGIS project to it
      """
      try:
         s = QSettings()
         s.setValue("currentExpID", int(self.expId))
         self.workspace.saveQgsProjectAs(self.expId)
      except:
         QMessageBox.warning(self,"status: ",
                         "Could not save expId to settings")         
# ......................................................................................         
   def closeEvent(self, event):
      """
      @summary: over ride close event 
      succeeded 
      """
      pass

# ..............................................................................
   def reject(self):
      """
      @summary: over ride reject 
      succeeded
      """     
      self.close()
      
# ..............................................................................
   def newExperimentCallBack(self,expObj,model):
      if expObj is not None:
         self.expId = expObj.id
         prj = QgsProject.instance()
         prj.dirty(False)
         self.interface.actionNewProject().trigger()
         self.setNewExperiment()
         #QgsProject.instance().emit( SIGNAL( "ActivateSDMExp(PyQt_PyObject)" ), self.expId)
         Communicate.instance().activateSDMExp.emit(self.expId)
         self.resetInputs()
         self.acceptBut.setEnabled(True)
         
         self.outputGroup.hide()
         message = "Successfully posted experiment, the ID assigned is %s" % (expObj.id)
         msgBox = QMessageBox.information(self,
                                            "Completed",
                                             message,
                                             QMessageBox.Ok)
         
      else:
         self.outputGroup.hide()
         message = "Problem with post experiment web service"
         msgBox = QMessageBox.warning(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok)   
# ..............................................................................
   def accept(self):
      """
      @summary: called on submit experiment, checks inputs, posts exp and clears form elements
      """
      self.outputGroup.show()
         
      self.acceptBut.setEnabled(False)
      valid = True
      prjScns = self.getProjScenIds()
      occSetId = self.occIdText.text()
      mdlScn = self.getModelScenId()
      algoCode = self.getAlgoCode()
      expName = self.expName.text()
      desc = self.expDesc.text()
      mdlMaskId, projMaskId = self.getMaskIds()
      if algoCode == 'ATT_MAXENT' and (bool(mdlMaskId) ^ bool(projMaskId)):
         message = """To use a mask with Maxent you must use both 
                   a model mask and a projection mask"""
         valid = False   
      if len(expName) == 0:
         message = "You must provide an experiment name"
         valid = False
      if len(occSetId) <= 0:
         message = "You must provide an occurrence set id"
         valid = False
      if mdlScn == -999:
         message = "You must provide an environmental scenario to model on"
         valid = False
      if algoCode == "select":
         message = "You must provide an algorithm"
         valid = False
      else:
         self.setParamsOnAlgCopy()
         if self.algSubWindow:
            if self.algSubWindow.continueWithoutProj:
               self.projectionScenListView.clearSelection()
               prjScns = []
            else:
               if len(prjScns) <= 0:
                  message = "You must provide at least one scenario to project on"
                  valid = False 
         else:
            if len(prjScns) <= 0:
               message = "You must provide at least one scenario to project on"
               valid = False       
      
      if valid: 
         postSDMParams = {'algorithm':self.algCopy,'mdlScn':mdlScn,'occSetId':occSetId,'prjScns':prjScns,
                          'email':self.email,'name':expName,'description':desc, 'mdlMask':mdlMaskId, 'prjMask':projMaskId}
         
         self.startThread(GENERIC_REQUEST,outputfunc = self.newExperimentCallBack, 
                          requestfunc=self.client.sdm.postExperiment, client=self.client,
                          inputs=postSDMParams)
      else:
         self.outputGroup.hide()
         self.acceptBut.setEnabled(True)
         msgBox = QMessageBox.warning(self,
                                      "Problem...",
                                      message,
                                      QMessageBox.Ok)
# ...................................................................................... 
   def clearLayout(self, layout):
      """
      @summary: recursive function that deletes
      all children of a layout
      """
      if layout is not None:
         while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
               widget.deleteLater()
            else:
               self.clearLayout(item.layout())  
               
# ......................................................................................
   def clearScenarios(self):
      """
      @summary: clears the models for both scenario controls
      """
      
      self.modelScenCombo.setCurrentIndex(0)
      self.modelScenCombo.setEnabled(False)
      self.projectionScenListView.setEnabled(False)
      self.maskGroup.setEnabled(False)
      
   
# ......................................................................................    
   def resetInputs(self):
      """
      @summary: called after experiment is posted,
      resets all the inputs
      """
      self.expName.setText('')
      self.expDesc.setText('')
      # reset occSetCombo model
      self.occListModel.updateList([])
      self.occSetCombo.setCurrentIndex(0)
      # reset and enable occIdText
      self.occIdText.setEnabled(True)
      self.occIdText.setText('')
      self.epsgCode = None
      self.modelScenCombo.setEnabled(False)
      self.projectionScenListView.setEnabled(False)
      self.maskGroup.setEnabled(False)
      # enable upload button
      self.uploadOccBut.setEnabled(True)
      # reset algCodeCombo
      self.algCodeCombo.setCurrentIndex(0)
      self.download.setToolTip("optional: Load Data from search")
      self.download.setEnabled(False)
      # reset scenCombo
      self.clearScenarios()
      
      
      self.modelScenCombo.setCurrentIndex(0)
# ......................................................................................       
   def populateAlgoDesc(self):
      
      
      self.algoDesc.clear()
      if self.algCodeCombo.currentIndex() != 0:
         code = self.getAlgoCode()
         algObj = self.client.sdm.getAlgorithmFromCode(code)
         self.algoDesc.insertPlainText(algObj.description)
# .......................................................................................      
      
   def setParamsOnAlgCopy(self):
      """
      @summary: gets missing params from algorithms and highlites missing
      @return: bool 
      """
      if self.algSubWindow is not None:
         for lineEdit,param in zip(self.algSubWindow.algParamLineEdits,self.algSubWindow.algParams):
            #print param.name," ",param.value
            value = lineEdit.text()
            param.value = value
            #print param.name," ",param.value
         self.algCopy = self.algSubWindow.algCopy
      else:     
         code = self.getAlgoCode()
         self.algCopy = self.client.sdm.getAlgorithmFromCode(code)
      
            
   def getAlgoCode(self):
      """
      @summary: gets the algo code from the algo object in the user role
      from the alg combo box
      @return: algo code string
      """
      currentIdx = self.algCodeCombo.currentIndex()
      algoCode = str(self.algCodeCombo.itemData(currentIdx, role=Qt.UserRole))
      return algoCode  
   
   def getModelScenId(self):
      """
      @summary: gets the current model scen id from the model scen combo as an integer
      @return: model scen integer
      """
      currentIdx = self.modelScenCombo.currentIndex()
      if currentIdx != 0:
         modelScenId = str(self.modelScenCombo.itemData(currentIdx, role=Qt.UserRole))         
      else:
         modelScenId = -999
      return modelScenId
     
   def getProjScenIds(self):
      indexObjs = self.projectionScenListView.selectedIndexes()
      rowIdxs = [x.row() for x in indexObjs]
      prjScns = []
      for idx in rowIdxs:
         prjScns.append(self.scenProjListModel.listData[idx].scenId) 
      return prjScns
   
   def getMaskIds(self):
      """
      @summary: gets current mask ids
      """
      currentMdlIdx = self.modelMaskCombo.currentIndex()
      if currentMdlIdx != -1 and currentMdlIdx != 0:
         try:
            mdlId = int(self.maskListModel.listData[currentMdlIdx])
         except:
            mdlId = None
      else:
         mdlId = None
         
      currentProjIdx = self.projectionMaskCombo.currentIndex()
      if currentProjIdx != -1 and currentMdlIdx != 0:
         try:
            prjId = int(self.maskListModel.listData[currentProjIdx])
         except:
            prjId = None
      else:
         prjId = None
      
      return mdlId,prjId
         
      
# ..............................................................................
   def setExpValues(self,occSetId,displayName,epsgCode):
      """
      @summary:  callback from post occurrence set,
      gathers the experiment inputs, and sets them to attributes,
      disables inputs, sets the preview and download text.
      """
      
      
      self.displayName = displayName
      self.occSetId = occSetId
      self.occIdText.setText(occSetId)
      self.epsgCode = int(epsgCode)
      
      
      
      self.occIdText.setEnabled(False)
      self.occSetCombo.setEnabled(False)
      self.uploadOccBut.setEnabled(False)
      self.download.setEnabled(False)
      
      self.download.setToolTip("optional: Load Data for %s" % (str(displayName)))
      msgBox = QMessageBox.information(self,
                                               "Completed...",
                                               "Uploaded occurrence set",
                                               QMessageBox.Ok)
      

# ..............................................................................         
   def openFileDialog(self,occSetId):
      
      currentIdx = self.occSetCombo.currentIndex() 
      filename = self.occListModel.listData[currentIdx].displayName
      
      settings = QSettings()
      shpPath = settings.value( "/UI/lastShapefileDir" )
      if not os.path.exists(shpPath):
         shpPath = settings.value("UI/lastProjectDir")     
      dirName = shpPath +"/"+filename.replace(' ','_')
      fileDialog = QgsEncodingFileDialog( self, "Save .zip File", dirName,"Zip Files (*.zip)")
      fileDialog.setDefaultSuffix(  "zip"  )
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )    
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return ''
      filename = fileDialog.selectedFiles() 
      return str(filename[0])
      

# ..............................................................................   
   def addToCanvas(self,path):
     
      zippath = os.path.dirname(str(path))                         
      z = zipfile.ZipFile(str(path),'r')
      for name in z.namelist():
         f,e = os.path.splitext(name)
         if e == '.shp':
            shapename = name
         z.extract(name,str(zippath))
      print "HERE"
      vectorpath = os.path.join(zippath,toUnicode(shapename))
      print "VECTOR PATH ",vectorpath
      vectorLayer = QgsVectorLayer(vectorpath,toUnicode(shapename.replace('.shp','')),'ogr')
      warningname = shapename    
      if not vectorLayer.isValid():
         QMessageBox.warning(self,"status: ",
           warningname)           
      else:
         lyrs = QgsMapLayerRegistry.instance().mapLayers()
         for id in lyrs.keys():
            if str(lyrs[id].name()) == shapename.replace('.shp',''):
               QgsMapLayerRegistry.instance().removeMapLayer(id)
            
      
         QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
# ..............................................................................
   def downloadLayer(self):
      
      # right here, maybe?
      #self.occSetCombo.model
      
      occSetId = self.occIdText.text()
      if occSetId != '':
         #filename = self.openFileDialog(occSetId)
         occFolder = self.workspace.getOccSetFolder()
         if not occFolder:
            occFolder = self.workspace.createOccFolder()
         zipName = "%s.%s" % (str(occSetId),"zip")
         filename = os.path.join(occFolder,zipName)
         if filename != '':
            try:
               #print filename
               self.client.sdm.getOccurrenceSetShapefile(occSetId,filename)
            except Exception, e:
               message = str(e)
               #print message
               QMessageBox.warning(self,"Error: ",
              "Problem with the shapefile service") 
            else:
               try:
                  self.addToCanvas(filename)
               except:
                  pass
# ..............................................................................      
   def setPreviewDownloadText(self, displayName):
      
      if id == '':
         self.download.setEnabled(False)
         self.download.setToolTip("optional: Load Data from search")
      else:
         self.download.setEnabled(True)
         self.download.setToolTip("optional: Load Data for %s" % (displayName))
# .............................................................................         
   def getIdxFromTuples(self,currentText):
      
      idx = 0
      # sO search result Object
      for sH in self.namedTuples:
         if sH.name.lower() in currentText.lower():
            break
         idx += 1
      return idx

# ..............................................................................
   def onTextChange(self, text):
      #print text
      #displayName = self.searchText.text()
      displayName = text
      noChars = len(displayName)
      # %20
      occurrenceSetId = None
      if text == '':
         self.occSetCombo.clear()
         self.occIdText.setText('')
         self.epsgCode = None
         self.clearScenarios()
         
      if noChars >= 3:
         if  "points)" in text:
           
            currText = self.occSetCombo.currentText()
            idx = self.getIdxFromTuples(currText)
             
            self.occSetCombo.setCurrentIndex(idx) 
            currentIdx = self.occSetCombo.currentIndex()                       
            occurrenceSetId = self.occListModel.listData[currentIdx].occurrenceSetId
            displayName = self.occListModel.listData[currentIdx].displayName
            self.setPreviewDownloadText(displayName)
            self.clearScenarios()
            self.occIdText.setText(str(occurrenceSetId))
            self.epsgCode = 4326
            return
         if ' ' in text:
            text.replace(' ','%20')
         self.occIdText.setText('')
         self.epsgCode = None
         self.setPreviewDownloadText('')
         self.searchOccSets(text)
         

# ........................................
   def searchOccSets(self,searchText=''):
      try:
         self.namedTuples = self.client.sdm.hint(searchText,maxReturned=60)         
      except Exception, e:
         pass 
      else:
         items = []
         if len(self.namedTuples) > 0:
            for species in self.namedTuples:
               items.append(SpeciesSearchResult(species.name,species.id,species.numPoints))
         else:
            items.append(SpeciesSearchResult('', '', ''))
         self.occListModel.updateList(items)
      
           

#...............................................................................
   def openOccUpload(self):
      """
      @summary: opens upload dialog
      """
      # updating the list for occurences and setting the index
      # triggers textchange event connected to occ combo, and 
      # therefore clears and disables the scenarios
      self.occListModel.updateList([])
      self.occSetCombo.setCurrentIndex(0)
      self.occIdText.setText('')
      self.epsgCode = None
      self.download.setEnabled(False)
      self.uploadOccSetDialog = UploadOccSetDialog(self.interface, client=self.client)
      self.uploadOccSetDialog.exec_()

# ..............................................................................
   def getOccSet(self, occId):
      #if self.occIdText.isModified():
      
      #if not self.outOfOccId[0]:
      #occId = self.occIdText.text()
      
      try:
         occSet = self.client.sdm.getOccurrenceSet(occId) 
      except Exception,e:
         self.epsgCode = None
         QMessageBox.warning(self,"Error: ",
           "Problem with the Occurrence Set service %s" % (str(e)))
      else:
         self.epsgCode = int(occSet.epsgcode)
         
# ..............................................................................
   def getScenariosMasks(self): 
      """
      @summary: checks for epsgCode, if None requests the occset
      """  
      
      occId = self.occIdText.text() 
      if self.epsgCode is None and len(occId) > 0:
         try:
            int(occId)
         except:
            self.epsgCode = None
            message = "invalid occurrence set id, must be an integer"
            QMessageBox.warning(self,"Error: ",
                            message)
         else:
            self.getOccSet(occId) # sets self.epsgCode
            if self.epsgCode is not None:
               self.getMaskLayers(typeCode=MASK_TYPECODE,epsgCode=self.epsgCode, getFull=True)
               self.populateModelScenCombo(epsg=self.epsgCode)
      elif self.epsgCode is not None:
         
         self.getMaskLayers(typeCode=MASK_TYPECODE,epsgCode=self.epsgCode, getFull=True)
         self.populateModelScenCombo(epsg=self.epsgCode)
           
# ..............................................................................          
    
   def populateModelScenCombo(self,newScenId=None,epsg=4326):
      """
      @summary: populates the model scenario combo
      @param newScenId: id of new scenario if new..., sets to its index
      """
      
      self.modelScenCombo.clear()
      try:
         userScenarios = []
         publicScenarios = []
         if epsg == 4326 or epsg == 2163:
            publicScenarios = self.client.sdm.listScenarios(keyword=['observed'],epsgCode=epsg,public=True)
            userScenarios = self.client.sdm.listScenarios(keyword=['observed'],epsgCode=epsg,public=False)
         else:
            userScenarios = self.client.sdm.listScenarios(keyword=['observed'],epsgCode=epsg,public=False)
         scenarios = userScenarios+publicScenarios
      except:
         QMessageBox.warning(self,"Error: ",
              "Problem with the scenario listing service")
      else:
         items = []
         items.append(ScenarioSearchResult('','select'))
         items.append("<a href='www.fake.fake'>build new modeling layer set</a>")
         for scen in userScenarios:
            try:
               str(scen.title)
            except:
               title = str(int(scen.id))
            else:
               title = str(scen.title)
            items.append(ScenarioSearchResult(title,int(scen.id)))
         if len(publicScenarios) > 0:
            for scen in publicScenarios:
               try:
                  str(scen.title)
               except:
                  title = str(int(scen.id))
               else:
                  title = str(scen.title)
               items.append(ScenarioSearchResult(title,int(scen.id),match=False))
               
         self.scenModelListModel.updateList(items)
         #self.scenModelListModel.listData = items
         if newScenId is None:
            self.modelScenCombo.setCurrentIndex(0)
         else:
            #newScenIdx = self.modelScenCombo.findData(newScenId, role=Qt.UserRole)
            # using this loop against the data model since UserRole doesn't always apply
            for idx, resultObj in enumerate(self.scenModelListModel.listData):
               try:
                  scenId = int(resultObj)      
               except Exception, e:
                  newScenIdx = 0
               else:
                  if scenId == newScenId:
                     newScenIdx = idx
                     break
                  else:
                     newScenIdx = 0
            self.modelScenCombo.setCurrentIndex(newScenIdx)
         # enable scenarios
         
         self.modelScenCombo.setEnabled(True)
         self.projectionScenListView.setEnabled(True)
         
# ..............................................................................
   def populateProjScenCombo(self, index): 
      """
      @summary: connected to currentIndexChanged signal on modelScen combo
      populates the QListView for projection scenarios
      @param index: current index (not Qindex obj) from the model scenario combo
      """
      # get the model Scen Id using the index
      # print index
      # what happens if there are no matching scenarios?
      if index != 0 and index != 1:
         modelScenId = self.modelScenCombo.itemData(index, role=Qt.UserRole)
         try:
            publicmatchingScens = []
            usermatchingScens = []
            if self.epsgCode == 4326 or self.epsgCode == 2163:
               publicmatchingScens = self.client.sdm.listScenarios(matchingScenario=modelScenId,public=True)
               usermatchingScens = self.client.sdm.listScenarios(matchingScenario=modelScenId,public=False)
            else:
               usermatchingScens = self.client.sdm.listScenarios(matchingScenario=modelScenId,public=False)
            matchingScens = usermatchingScens+publicmatchingScens
         except:
            QMessageBox.warning(self,"Error: ",
              "Problem with the scenario listing service")
         else:
            items = []
            if self.scenModelListModel.listData[index].match:
               items.append("<a href='www.fake.fake'>build new matching layer set</a>")
            for scen in matchingScens:
               try:     
                  items.append(ScenarioSearchResult(scen.title,int(scen.id)))
               except:
                  items.append(ScenarioSearchResult(str(scen.id),int(scen.id)))
            self.scenProjListModel.updateList(items)
      elif index == 1:
         self.scenProjListModel.updateList([ScenarioSearchResult('','')])
         self.postScenarioDialog = PostScenarioDialog(client=self.client,epsg=self.epsgCode)
         self.postScenarioDialog.exec_()          
      else:
         self.scenProjListModel.updateList([ScenarioSearchResult('','')]) 


# .............................................................................. 
   def populateAlgoCombo(self):
      """
      @summary: populates the algorithm combo
      """
      self.algCodeCombo.addItem('',userData='select')
      for alg in self.algos:
         self.algCodeCombo.addItem(alg.name,userData=alg.code)
      #QObject.connect(self.algCodeCombo, 
      #                       SIGNAL("currentIndexChanged(int)"), self.enableAdvanced)
      self.algCodeCombo.currentIndexChanged.connect(self.enableAdvanced)
      #QObject.connect(self.advancedBut, 
      #                       SIGNAL("clicked()"), self.showAlgParams)
      self.advancedBut.clicked.connect(self.showAlgParams)
   
   def enableAdvanced(self,index):
      if index != 0:
         self.advancedBut.setEnabled(True)
      else:
         self.advancedBut.setEnabled(False)
      
   def showAlgParams(self):
      index = self.algCodeCombo.currentIndex()
      if index != 0:
         algcode = str(self.algCodeCombo.itemData(index, role=Qt.UserRole))
         if len(self.getProjScenIds()) > 0:
            projs = True
         else:
            projs = False
         self.algSubWindow = AdvancedAlgo(self.client,algcode, self, projections=projs)
         self.algSubWindow.exec_()
      else:
         message = "Choose an algorithm from the drop down"
         msgBox = QMessageBox.warning(self,
                                      "Problem...",
                                      message,
                                      QMessageBox.Ok)
      

# ..............................................................................
   def matchNew(self,index):
      """
      @summary: opens up a dialog to match a layer set using the current index from
      the modelScenCombo
      @param index: Qindex from the projection QListView for projection layer sets
      """
      if index.row() == 0 and type(self.scenProjListModel.listData[index.row()]) == StringType:
            # get the id of model scenario
            self.projectionScenListView.clearSelection()
            currindex = self.modelScenCombo.currentIndex()
            modelScenId = self.modelScenCombo.itemData(currindex, role=Qt.UserRole)
            self.postScenarioDialog = PostScenarioDialog(match=True,scenarioId=modelScenId,client=self.client)
            self.postScenarioDialog.exec_()      
             


### ..............................................................................         
          
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
      helpDialog.scrollToAnchor('newSDMExperiment')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
      
class Ui_SubDialog(object):
   
   def setupUi(self):
      
      self.resize(660, 280)
      self.setMinimumSize(660,280)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
      
      self.gridLayout = QGridLayout(self) 
      
      self.verticalLayout = QVBoxLayout()
      
      self.algoTab = QTabWidget()
      self.firstPage = QWidget()
      
      self.verticalLayout.addWidget(self.algoTab)
      self.algoTab.addTab(self.firstPage,"Parameters")
      
      self.acceptBut = QPushButton("OK")
      self.rejectBut = QPushButton("Cancel")
      #self.helpBut = QPushButton("?")
      #self.helpBut.setMaximumSize(30, 30)
      
      self.buttonBox = QDialogButtonBox()
      #self.buttonBox.addButton(self.helpBut, QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QDialogButtonBox.ActionRole)
      
      #QObject.connect(self.rejectBut, SIGNAL("clicked()"), self.reject)
      #QObject.connect(self.acceptBut, SIGNAL("clicked()"), self.accept)
      
      self.rejectBut.clicked.connect(self.reject)
      self.acceptBut.clicked.connect(self.accept)
      
      #QObject.connect(self.helpBut, SIGNAL("clicked()"), self.help)
      
      self.gridLayout.addLayout(self.verticalLayout,0,0,1,1)
      self.gridLayout.addWidget(self.buttonBox,     8,0,1,3)
      #self.setWindowTitle("Algorithm Parameters for %s" % self.algcode)

class AdvancedAlgo(QDialog,Ui_SubDialog):     
   
   def __init__(self,client, algcode, parent, projections = False):
      QDialog.__init__(self)
      self.algcode = algcode
      self.client = client
      self.continueWithoutProj = False
      self.notProjectionErrOnProjValue = False
      self.projections = projections
      self.parentDialog = parent
      self.setupUi() 
      self.algCopy = self.client.sdm.getAlgorithmFromCode(self.algcode)
      self.setWindowTitle("Set parameters for %s" % self.algCopy.name) 
      self.extraParamTabs = []
      self.showAlgParams()
      
   def help(self):
      pass
   
   def closeEvent(self,event):
      
      pass
   
   def reject(self):
      
      self.close()
      self.algCopy = self.client.sdm.getAlgorithmFromCode(self.algcode)
      
      
   def accept(self):
      
      missing, message = self.missingParams()
      if not missing:    
         self.close()
      else:         
         if message != "":
            reply = QMessageBox.question(self, 'conflict with parameters',
                                         message, QMessageBox.Yes | 
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
               self.continueWithoutProj = True
               self.parentDialog.projectionScenListView.clearSelection()
               self.close()
            elif reply == QMessageBox.No:
               # now what do we do?
               pass
         else:
            warning = "some parameters are missing or have incorrect values"    
            QMessageBox.warning(self,
                                 "Problem...",
                                 warning,
                                 QMessageBox.Ok)
      
   def missingParams(self):
      """
      @summary: gets missing params from algorithms and highlites missing
      @return: bool 
      """
      message = ""
      missingParams = False  
      for lineEdit,param,label in zip(self.algParamLineEdits,self.algParams,self.algParamLabels):
         value = lineEdit.text()
         if not(self.validateAlgParam(param,value)):
            label.setStyleSheet("color:red;")
            missingParams = True
            if param.allowProjectionsIfValue and not(self.notProjectionErrOnProjValue):
               message = "Cannot use %s with projections.  Continue without projections?" % (param.name)
         else:
            label.setStyleSheet("color:black;")
      return missingParams, message
      
   def validateAlgParam(self, param, value):
      """
      @summary: validates param value set in lineEdit
      with type, min, and max, empty string for the param object
      @param param: Lifemapper param object
      @param value: value set in lineEdit 
      @return: boolean
      """
      
      valid = False
      if value != '':         
         try:
            castValue = float(value)
            if param.type == "Integer":
               if param.min and param.max:
                  r = range(int(param.min),int(param.max)+1)
                  if not castValue in r:
                     raise
               castValue = int(value)                  
         except:
            if param.allowProjectionsIfValue != None:
               self.notProjectionErrOnProjValue = True
         else:
            if param.min and param.max:               
               paramMin = float(param.min)
               paramMax = float(param.max) 
               if paramMin <= castValue <= paramMax:
                  valid = True
            elif param.min:
               paramMin = float(param.min) 
               if paramMin <= castValue:
                  valid = True
            elif param.max:
               paramMax = float(param.max) 
               if paramMax >= castValue:
                  valid = True
            else:
               # doesn't have a min or max
               valid = True
            if param.allowProjectionsIfValue != None and castValue > 1 and self.projections: 
               valid = False                       
      return valid  
   
   def showAlgParams(self):
      """
      @summary: lays out forms in a horizontal container containing
      lineEdits for each parameter
      @param index: index from the algorithm combo
      """

         
      noFieldsPerCol = 6
      if len(self.extraParamTabs) > 0:
         tabCount = self.algoTab.count()
         while tabCount > 1:
            self.algoTab.removeTab(tabCount-1)
            tabCount = self.algoTab.count()
         self.extraParamTabs = []
      columnForm = QFormLayout()
      self.algParamLineEdits = []
      self.algParams = []
      self.algParamLabels = []      
      if self.firstPage.layout() is None:
         algoParamContainer = QHBoxLayout()
         self.firstPage.setLayout(algoParamContainer)
      else:
         algoParamContainer = self.firstPage.layout()
         self.clearLayout(algoParamContainer)
      #################################
      tabIdx = 0  # starts with one      
      rowcount = 0
      columnCount = 1
      paramsAdded = 0
      noParams = len(self.algCopy.parameters)
      for param in self.algCopy.parameters:
         #print "NAME ",param.name
         rowcount += 1
         lineEdit = QLineEdit()
         self.algParamLineEdits.append(lineEdit)
         self.algParams.append(param)
         if param.min and param.max:
            paramNameLimitDesc = "%s (range: %s - %s)" % (str(param.name),str(param.min),str(param.max))
         elif param.min:
            paramNameLimitDesc = "%s (min: %s)" % (str(param.name),str(param.min))
         elif param.max:
            paramNameLimitDesc = "%s (max: %s)" % (str(param.name),str(param.max))
         else:
            paramNameLimitDesc = "%s" % (str(param.name))
         label = QLabel(paramNameLimitDesc)
         label.setToolTip("<p>"+param.doc+"</p>")
         self.algParamLabels.append(label)
         lineEdit.setText(param.default)
         lineEdit.setMaximumSize(70, 19)
         fullColumn = False
         paramsAdded += 1
         if rowcount == noFieldsPerCol:
            fullColumn = True
            columnForm.addRow(label, lineEdit)
            algoParamContainer.addLayout(columnForm)
            columnForm = QFormLayout()
            rowcount = 0
            columnCount += 1       
            if columnCount == 3 and paramsAdded != noParams:
               tabIdx +=1
               columnCount = 1
               newPage = QWidget()
               algoParamContainer = QHBoxLayout()
               newPage.setLayout(algoParamContainer)
               self.extraParamTabs.append(tabIdx)
               self.algoTab.addTab(newPage,"..")             
         else:
            columnForm.addRow(label, lineEdit)
      
      if not fullColumn:
         algoParamContainer.addLayout(columnForm) 
     
#..............................................................................
class BackSpaceEventHandler(QObject):
   
   def eventFilter(self, object, event):
      #print "is gettting to backspace? ",event.type()
      if event.type() == QEvent.KeyPress:
         if event.key() == Qt.Key_Backspace:
            currentText = object.currentText()
            try:             
               numPoints = object.model().listData[object.findText(currentText)].numPoints
               if "("+str(numPoints)+" points)" in currentText:               
                  displayName = object.model().listData[object.findText(currentText)].displayName
                  object.setEditText(displayName+displayName[-1:])
                  
            except Exception, e:
               pass
            
      return QWidget.eventFilter(self, object, event)



   
class EnterTextEventHandler(QObject):
  
   def __init__(self,occSetCombo,occModel,download):
      super(EnterTextEventHandler, self).__init__()
      self.occSetCombo = occSetCombo
      self.occListModel = occModel
      self.download = download
      
   def eventFilter(self,object,event):
      if event.type() == QEvent.FocusIn:
         self.occListModel.updateList([])
         self.occSetCombo.setCurrentIndex(0) 
         self.download.setEnabled(False)
         self.download.setToolTip("optional: Load Data from search")    
      return QWidget.eventFilter(self, object, event)
   
   
class SDMDelegate(QStyledItemDelegate):
   
   def __init__(self, parent=None, *args):
      QItemDelegate.__init__(self, parent, *args)
      
      
   def paint(self, painter, option, index):
      
      text = index.model().listData[index.row()]
      #print type(text),' - ', text
      if not(isinstance(text,ScenarioSearchResult)):
         painter.save()
         document = QTextDocument()
         document.setDefaultFont(option.font)      
         document.setHtml(text)
         painter.translate(option.rect.x(), option.rect.y()-3)
         document.drawContents(painter)
         painter.restore()
     
      else:
         QStyledItemDelegate.paint(self, painter, option, index)
# .............................................................................
class LmListModel(QAbstractListModel):
   """
   @summary: List model used by Lifemapper Qt listing widgets
   @note: Inherits from QtCore.QAbstractListModel 
   """
   # .........................................
   def __init__(self, listData, parent=None, model=False, *args):
      """
      @summary: Constructor for LmListModel
      @param listData: List of objects to insert into list
      @param parent: (optional) The parent of the LmListModel
      @param model: bool, whether or not data model is for modeling layer set
      @param args: Additional arguments to be passed
      """
      QAbstractListModel.__init__(self, parent, *args)
      self.listData = listData
      self.model = model
      
   # .........................................
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
         if index.row() == 1 and self.model:
            return "build new model"
         else:   
            try: return self.listData[index.row()].customData()
            except: return self.listData[index.row()]
           
      if index.isValid() and role == Qt.UserRole:
         return int(self.listData[index.row()])
      else:
         return 
      
   # .........................................
   def rowCount(self, parent=QModelIndex()):
      """
      @summary: Returns the number of rows in the list
      @param parent: (optional) The parent of the object
      @return: The number of items in the list
      @rtype: Integer
      """
      return len(self.listData)
   
   # .........................................
   def updateList(self, newList):
      """
      @summary: Updates the contents of the list
      @param newList: A list of items to use for the new list
      @note: The provided list will replace the old list 
      """
      #print "its at update list ",newList
      self.beginInsertRows(QModelIndex(), 0, len(newList))
      self.listData = newList
      
      self.endInsertRows()

# .............................................................................
class SpeciesSearchResult(object):
   """
   @summary: Data structure for species search results (occurrence sets)
   """
   # .........................................
   def __init__(self, displayName, occurrenceSetId, numPoints):
      """
      @summary: Constructor for SpeciesSearchResult object
      @param displayName: The display name for the occurrence set
      @param occurrenceSetId: The Lifemapper occurrence set id
      @param numPoints: The number of points in the occurrence set
      """
      self.displayName = displayName
      self.occurrenceSetId = occurrenceSetId
      self.numPoints = numPoints

   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      return "%s (%s points)" % (self.displayName, self.numPoints)
      
class MaskSearchResult(object):
   """
   @summary: Data structure for ScenarioSearchResult
   """
   # .........................................
   def __init__(self,name, id):
      """
      @summary: Contstructor for MaskSearchResult
      """
      self.maskId = id
      self.name = name
      
   def customData(self):
      """
      @summary: Creates a string representation of the ScenarioSearchResult 
                   object
      """
      return "%s" % (self.name)
   
   def __int__(self):

      return int(self.maskId)
   
class ScenarioSearchResult(object):
   """
   @summary: Data structure for ScenarioSearchResult
   """
   # .........................................
   def __init__(self, title, id,match=True):
      """
      @summary: Constructor for ScenarioSearchResult object
      @param title: The display name for scenario
      @param id: The Lifemapper scenario id
      """
      self.scenId = id
      self.scenTitle = title
      self.match = match
      
   def customData(self):
      """
      @summary: Creates a string representation of the ScenarioSearchResult 
                   object
      """
      return "%s" % (self.scenTitle)
   
   def __int__(self):
      
      return self.scenId
     

if __name__ == "__main__":
#  
   import_path = "/home/jcavner/ghWorkspace/LmQGIS.git/lifemapperTools/"
   sys.path.append(os.path.join(import_path, 'LmShared'))
   configPath = os.path.join(import_path, 'config', 'config.ini') 
   os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
   from LmClient.lmClientLib import LMClient
   client =  LMClient()
   client.login(userId='Dermot', pwd='Dermot')
   qApp = QApplication(sys.argv)
   d = PostSDMExpDialog(None,client=client)
   #d = AdvancedAlgo()
   d.show()
   sys.exit(qApp.exec_())         
      