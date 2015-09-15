"""
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
from LmClient.lmClientLib import LMClient
from lifemapperTools.common.communicate import Communicate
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
import sys
import os.path
from collections import Counter, defaultdict


class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(900, 590)
      self.setMinimumSize(500,190)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
      
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      
      ###############Scenario name and EPSG #########
      topLevelInfoLayout = QtGui.QGridLayout()
      topLevelInfoLayout.setRowMinimumHeight(0,8)
      topLevelInfoLayout.setRowMinimumHeight(1,32)
      topLevelInfoLayout.setRowMinimumHeight(2,27)
      topLevelInfoLayout.setRowMinimumHeight(3,35)
      #topLevelInfoLayout.setRowMinimumHeight(4,25)
      topLevelInfoLayout.setColumnMinimumWidth(0,170)
      topLevelInfoLayout.setColumnMinimumWidth(1,240)
      topLevelInfoLayout.setColumnMinimumWidth(2,170)
      topLevelInfoLayout.setColumnMinimumWidth(3,30)
      topLevelInfoLayout.setColumnMinimumWidth(4,160)
      
      
      scenarioNameLabel = QtGui.QLabel("Layer Set Short Name")
      scenarioNameLabel.setMaximumHeight(25)
      epsgCodeLabel = QtGui.QLabel("EPSG Code")
      epsgCodeLabel.setMaximumHeight(25)
      
      scenarioTitleLabel = QtGui.QLabel("Layer Set Title")
      scenarioTitleLabel.setMaximumHeight(25)
      
      self.scenarioName = QtGui.QLineEdit()
      self.scenarioName.setMaximumHeight(25)
      
      self.scenarioTitle = QtGui.QLineEdit()
      self.scenarioTitle.setMaximumHeight(25)
      
      self.epsgCodeEdit = QtGui.QLineEdit()
      self.epsgCodeEdit.setMaximumHeight(25)
      self.epsgCodeEdit.editingFinished.connect(self.epsgEdited)
      
      self.epsgButton = QtGui.QPushButton("Browse")
      self.epsgButton.setMaximumSize(80, 30)
      self.epsgButton.setAutoDefault(False)
      self.epsgButton.clicked.connect(self.openProjSelectorSetEPSG)
      
      
      unitsLabel = QtGui.QLabel("Map Units")
      unitsLabel.setMaximumHeight(25)
      self.selectUnits = QtGui.QComboBox()
      self.selectUnits.addItem("decimal degrees",
           'dd')
      self.selectUnits.addItem("meters",
           'meters')
      self.selectUnits.addItem("feet",
           'feet')
      self.selectUnits.addItem("inches",
           'inches')
      self.selectUnits.addItem("kilometers",
           'kilometers')
      self.selectUnits.addItem("miles",
           'miles')
      self.selectUnits.addItem("nauticalmiles",
           'nauticalmiles')
      
     
      topLevelInfoLayout.addWidget(scenarioNameLabel,     1,0,1,1)#,alignment = QtCore.Qt.AlignLeft)
      topLevelInfoLayout.addWidget(scenarioTitleLabel,    1,1,1,1)
      topLevelInfoLayout.addWidget(epsgCodeLabel,         1,2,1,1)#,alignment = QtCore.Qt.AlignLeft)
      topLevelInfoLayout.addWidget(unitsLabel,            1,4,1,1)
      topLevelInfoLayout.addWidget(self.scenarioName,     2,0,1,1)#,alignment = QtCore.Qt.AlignLeft)
      topLevelInfoLayout.addWidget(self.scenarioTitle,    2,1,1,1)
      topLevelInfoLayout.addWidget(self.epsgCodeEdit,     2,2,1,1)#,alignment = QtCore.Qt.AlignLeft)
      topLevelInfoLayout.addWidget(self.epsgButton,       2,3,1,1)#,alignment = QtCore.Qt.AlignLeft)
      topLevelInfoLayout.addWidget(self.selectUnits,      2,4,1,1)
      
      self.gridLayout.addLayout(topLevelInfoLayout,0,0,1,1)
      
      ############### labels ###############
      # this where the labels were
      ################################################
      self.horizontal = QtGui.QFrame()
      self.horizontal.setFrameShape(QtGui.QFrame.HLine)
      self.horizontal.setFrameShadow(QtGui.QFrame.Sunken)
      
      
      
      self.gridLayout.addWidget(self.horizontal,1,0,1,1)#,alignment = QtCore.Qt.AlignTop)
      
      #self.scrollarea = QtGui.QScrollArea()
      #self.scrollarea.setWidgetResizable(True)
      #self.scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
      #self.innerWidget = QtGui.QWidget()
      
      self.gridLayout_input = QtGui.QVBoxLayout()
      
      
      
           
      #self.scrollarea.setWidget(self.gridLayout_input.widget())
      
      self.gridLayout.addLayout(self.gridLayout_input,3,0,1,1,alignment = QtCore.Qt.AlignTop)
            

      self.progressbar = QtGui.QProgressBar()
      self.progressbar.setMinimum(0)
      self.progressbar.hide()
      
      self.helpBut = QtGui.QPushButton("?")
      self.helpBut.setAutoDefault(False)
      self.helpBut.setMaximumSize(30, 30)
      
      self.acceptBut = QtGui.QPushButton("OK")
      self.acceptBut.setAutoDefault(False)
      self.rejectBut = QtGui.QPushButton("Close")
      self.rejectBut.setAutoDefault(False)
      self.buttonBox = QtGui.QDialogButtonBox()
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      
      self.rejectBut.clicked.connect(self.reject)
      self.acceptBut.clicked.connect(self.accept)
      self.helpBut.clicked.connect(self.help)
      
      
      
      self.gridLayout.addWidget(self.progressbar,   7,0,1,3)
      self.gridLayout.addWidget(self.buttonBox,   8,0,1,3)
      
      
      
class LmPushButton(QtGui.QPushButton): 
   def __init__(self,title,parent): 
      super(LmPushButton, self).__init__(title, parent)
      self.setAutoDefault(False)    
      
      
      
class PostScenarioDialog(QtGui.QDialog, Ui_Dialog):   
   
   def __init__(self, match=False, client=None, scenarioId=None, epsg=None):
      QtGui.QDialog.__init__(self)
      self.layerRows = []
      self.client = client
      self.postSucceeded = False
      self.setupUi()
      #self.setTypeCodes()
      if not match:
         self.helpAnchor = "postModelScen"
         self.setTypeCodes()
         self.match = False
         self.keywords = ['observed']
         self.typeCodeIdx = 0
         self.layerIdIdx = 1        
         self.buildFirstModelingLayers()
         if epsg is not None:
            self.epsgCodeEdit.setText(str(epsg))
            self.epsgCodeEdit.setModified(True)
            self.epsgEdited()
            self.epsgCodeEdit.setEnabled(False)
            self.selectUnits.setEnabled(False) 
            self.epsgButton.setEnabled(False)
         self.setWindowTitle("Upload an Environmental Layer Set")
      else:
         self.helpAnchor = "postProjScen"
         self.match = True
         self.keywords = []
         self.typeCodeIdx = 0
         self.layerIdIdx = 2
         self.resize(930, 590)
         if scenarioId is not None:
            scenario = self.getScenario(scenarioId)
            if scenario is not None:
               noLayers = len(scenario.layers)
               self.resize(930,200+(noLayers*60))
               self.buildHeader(175)
               self.populateEPSG_Units(scenario)
               self.populateLayers(scenario)
            else:
               self.buildHeader(0)
               self.buildErrorRow()
         self.setWindowTitle("Upload a Matching Environmental Layer Set")
      
      
# ..............................................................................    
   def setMapUnits(self):
      """
      @summary: sets the select units combo for epsg from epsgCodeEdit form element
      """
      
      authId = "EPSG:%s" % (self.epsgCodeEdit.text())
      crs = QgsCoordinateReferenceSystem() 
      crs.createFromOgcWmsCrs(authId)
      mapunitscode = crs.mapUnits()
      if mapunitscode == 0:
         mapunits = 'meters'
      elif mapunitscode == 1:
         mapunits = 'feet'
      elif mapunitscode == 2:
         mapunits = 'dd' 
      else: #  if mapunitscode doesn't exist set to dd
         mapunits = 'dd'
         
      unitsIdx = self.selectUnits.findData(mapunits, role=QtCore.Qt.UserRole)
      self.selectUnits.setCurrentIndex(unitsIdx)
      
# ..............................................................................       
   def epsgEdited(self):
      """
      @summary: called on the edited signal from the epsg edit, checks to see if
      epsgcode has been modified and sets the map units and enables the prompt
      layers
      """
      if self.epsgCodeEdit.isModified():
         self.setMapUnits()      
         self.setEnableRows(True, addRow=True)
      self.epsgCodeEdit.setModified(False)
# ..............................................................................       
   def setTypeCodes(self):
      codes = []        
      try:
         userTypeCodes = self.client.sdm.listTypeCodes(public=False,fullObjects=True)
      except:
         QtGui.QMessageBox.warning(self,"Error: ",
              "Problem with type code service") 
      else:
         codes.append(('',''))
         for code in userTypeCodes:
            try:
               codes.append((code.typeTitle,code.typeCode))
            except:
               try:
                  codes.append((code.typeCode,code.typeCode))
               except:
                  pass
      self.allTypeCodes = codes   
             
# .............................................................................. 
   def populateEPSG_Units(self,scenario):
      """
      @summary: populates the espg edit and select units from the Lm Scenario object, for matching 
      scenario
      @param scenario: Lm Scenario object
      """
      mapunits = scenario.units
      epsgCode = scenario.epsgcode     
      self.epsgCodeEdit.setText(str(epsgCode))
      self.epsgCodeEdit.setEnabled(False)
      self.epsgButton.setEnabled(False)
      unitsIdx = self.selectUnits.findData(mapunits, role=QtCore.Qt.UserRole)
      self.selectUnits.setCurrentIndex(unitsIdx)
      self.selectUnits.setEnabled(False)
      

# ..............................................................................        
   def buildErrorRow(self): 
      """
      @summary: builds an error row for the table for matching a scenario
      if there was no scenario retrieved in the constructor
      """
      self.scenarioName.setEnabled(False)
      self.scenarioTitle.setEnabled(False)
      self.epsgCodeEdit.setEnabled(False)
      self.epsgButton.setEnabled(False)
      self.selectUnits.setEnabled(False)
      self.acceptBut.setEnabled(False)     
      errorEdit = QtGui.QLineEdit()
      errorEdit.setText("ERROR RETRIEVING LAYER SET")
      errorEdit.setEnabled(False)
      newRow = QtGui.QHBoxLayout()      
      newRow.addWidget(errorEdit)
      self.gridLayout_input.addLayout(newRow)
# ..............................................................................               
   def populateLayers(self,scenario):
      """
      @summary: addRows to the dialog and populates them with values
      from the scenario object, for matching scenarios
      @param scenario: lifemapper scenario object
      """     
      modelingLayers = list(scenario.layers)      
      for layer in modelingLayers:         
         modelTypeCodeEdit = QtGui.QLineEdit()
         modelTypeCodeEdit.setText(layer.typeCode)
         modelTypeCodeEdit.setEnabled(False)
         modelLayerNameEdit = QtGui.QLineEdit()
         modelLayerNameEdit.setText(layer.name)
         modelLayerNameEdit.setEnabled(False)
         epsgCode = str(self.epsgCodeEdit.text())
         matchingLayerNameEdit = QtGui.QComboBox()
         matchingLayerNameEdit.setMinimumWidth(280)
         matchingLayerNameEdit.setMaximumWidth(280)
         layers = self.getLayers(layer.typeCode, epsgCode,getFull=True)
         matchingLayerNameEdit.addItem("",0)
         for idx,layer in enumerate(layers):
            matchingLayerNameEdit.addItem(layer[0],int(layer[1]))
            toolTip = self.conCatToolTip(layer[2])
            matchingLayerNameEdit.setItemData(idx+1,toolTip,QtCore.Qt.ToolTipRole)
         newRow = QtGui.QHBoxLayout()      
         newRow.addWidget(modelTypeCodeEdit )
         newRow.addWidget(modelLayerNameEdit)
         newRow.addWidget(matchingLayerNameEdit)
                           
         self.layerRows.append(newRow)
         self.gridLayout_input.addLayout(newRow)
         
# ..............................................................................      
   def getLayer(self,layerId):
      try:
         layer = self.client.sdm.getLayer(layerId)
      except:
         QtGui.QMessageBox.warning(self,"Error: ",
              "Problem with the layer service") 
         return None
      else:
         return layer
            
# ..............................................................................   
   def getScenario(self, scenarioId):
      """
      @summary: error wrapper for getting scenario from the client
      @param scenarioId: id of the modeling scenario to get,
      it is this scenario that this dialog will also
      provide the inputs for making a matching projection
      scenario
      """
      
      try:
         scenario = self.client.sdm.getScenario(scenarioId)
      except:
         QtGui.QMessageBox.warning(self,"Error: ",
              "Problem with the scenario service") 
         return None
      else:
         return scenario
# ..............................................................................
   def resetForm(self):
      self.progressbar.reset()
      self.progressbar.hide()
      self.scenarioName.setText('')
      #self.scenarioName.setEnabled(True)
      self.scenarioTitle.setText('')
      #self.scenarioTitle.setEnabled(True)
      if not self.match:
         # remove all rows but the first, and clear out values of first row
         self.epsgCodeEdit.setText('')
         self.selectUnits.setCurrentIndex(0)
         rowsToRemove = list(self.layerRows[2:])
         for layer in rowsToRemove:
            self.subtractRow(layer)
         firstLayer = self.layerRows[0]
         firstLayer.itemAt(0).widget().setCurrentIndex(0)
         firstLayer.itemAt(1).widget().setCurrentIndex(0)         
         
         try:
            secondLayer = self.layerRows[1]
            secondLayer.itemAt(0).widget().setCurrentIndex(0)
            secondLayer.itemAt(1).widget().setCurrentIndex(0) 
         except:
            pass
      
         self.setEnableRows(False, addRow=True)
          
      else:
         for layer in self.layerRows:
            layer.itemAt(self.layerIdIdx).widget().setCurrentIndex(0)
            
      #self.postLayerSetCheck.setChecked(True)
            
   def closeEvent(self, event):
      """
      @summary: over ride close event and check if match and post
      succeeded 
      """
      if not self.match and not self.postSucceeded:
         Communicate.instance().postScenarioFailed.emit(self.match)
# ..............................................................................
   def reject(self):
      """
      @summary: over ride reject and check if match and post
      succeeded
      """
      if not self.match and not self.postSucceeded:
         Communicate.instance().postScenarioFailed.emit(self.match)
      self.close()
   
   def getLayerIdFromCombo(self,layer):
      
      combo = layer.itemAt(self.layerIdIdx).widget()
      comboIdx = combo.currentIndex()
      layerId = combo.itemData(comboIdx,role=QtCore.Qt.UserRole)
      
      return layerId

# ..............................................................................
   
   def accept(self):
      if len(self.layerRows) > 0:
         valid = self.validate() 
         self.progressbar.setMaximum(len(self.actualRows)+1) # for test
         if valid:         
            self.progressbar.show()
            epsgCode = str(self.epsgCodeEdit.text())
            unitsIdx = self.selectUnits.currentIndex()
            units = str(self.selectUnits.itemData(unitsIdx, role=QtCore.Qt.UserRole))
            scenarioTitle = self.scenarioTitle.text()
            scenarioCode = self.scenarioName.text()
            layerIds = []
            progress = 0
            for layer in self.actualRows:
               layerId = self.getLayerIdFromCombo(layer)
               layerIds.append(layerId)
               progress += 1
               self.progressbar.setValue(progress)
               
            try:
               scenario = self.client.sdm.postScenario(layerIds, scenarioCode, epsgCode, units,
                                                      title=scenarioTitle,keywords=self.keywords)
            except:
               self.postSucceeded = False
               self.progressbar.reset()
               self.progressbar.hide()
               Communicate.instance().postScenarioFailed.emit(self.match)
               message = "Problem with uploading scenario"
               msgBox = QtGui.QMessageBox.warning(self,
                                                "Problem...",
                                                message,
                                                QtGui.QMessageBox.Ok)
            else: 
               self.progressbar.setValue(progress+1)   
               self.resetForm()
               self.postSucceeded = True                             
               Communicate.instance().postedScenario.emit(scenario.id,self.match)
               message = "Successfully posted environmental layer set"
               msgBox = QtGui.QMessageBox.information(self,
                                             "Success...",
                                             message,
                                             QtGui.QMessageBox.Ok) 
                

# ..............................................................................
   def buildHeader(self, spacer):
      # first build the labels 
      labelBox = QtGui.QHBoxLayout()
      
      typeCodeLabel = QtGui.QLabel("Layer Type Code")
      typeCodeLabel.setMaximumHeight(25)
      modelLayerNameLabel = QtGui.QLabel("Model Layer Name")
      modelLayerNameLabel.setMaximumHeight(25)
      
      matchingLayerNameLabel = QtGui.QLabel("Matching Layer")
      matchingLayerNameLabel.setMaximumHeight(25)
      
      #fileLabel = QtGui.QLabel("File")
      #fileLabel.setMaximumHeight(25)
      
      labelBox.addWidget(typeCodeLabel)
      labelBox.addSpacing(200)
      labelBox.addWidget(modelLayerNameLabel)
      labelBox.addSpacing(220)
      labelBox.addWidget(matchingLayerNameLabel)
      #labelBox.addWidget(fileLabel)
      labelBox.addSpacing(spacer)
      
      self.gridLayout.addLayout(labelBox,2,0,1,1)
      

# ..............................................................................
   def conCatToolTip(self,layer):
      """
      @summary: builds tool tip for a item in the layer combo
      """
      try:
         toolTip = "resolution: %s, maxVal: %s, minVal: %s, nodataVal: %s, keywords: %s" \
         % (layer.resolution,layer.maxVal,layer.minVal,layer.nodataVal,layer.keywords)
      except:
         toolTip = "No Info"
      return toolTip       
# ..............................................................................
   def populateLayerCombo(self, index, typeCodeEdit, layerNameEdit):
      """
      @summary: populates a layer combobox for a row or layer
      @param index: QIndex object from the type code combobox
      @param typeCodeEdit: type code QComboBox for a layer
      @param layerNameEdit: layer QComboBox for a layer      
      """
      if index != 0:
         layerNameEdit.setEnabled(True)
         #typeCode = str(typeCodeEdit.currentText())
         typeCurrentIdx = typeCodeEdit.currentIndex()
         typeCode = str(typeCodeEdit.itemData(typeCurrentIdx, role=QtCore.Qt.UserRole))
         epsgCode = str(self.epsgCodeEdit.text())
         layers = self.getLayers(typeCode,epsgCode,getFull=True)
         layerNameEdit.clear()
         if layers is not None and len(layers) > 0:
            layerNameEdit.addItem('',0)
            for idx,layer in enumerate(layers):
               
               layerNameEdit.addItem(layer[0],int(layer[1]))
               #toolTip = self.layerInfo[layer[1]]
               toolTip = self.conCatToolTip(layer[2])
               layerNameEdit.setItemData(idx+1,toolTip,QtCore.Qt.ToolTipRole)
         else:
            layerNameEdit.addItem("No Layers",0)
      else:
         layerNameEdit.clear()
         

   def getLayers(self,typeCode=None,epsgCode=None,getFull=False):
      """
      @summary: gets a list of layer atoms
      @param typeCode: typeCode string to filter on from typeCode combo
      @param epsgCode: epsgCode [integer] to filter on
      @return: list of tuples (title, id)
      """
      layers = []
      try:
         userLayers = self.client.sdm.listLayers(public=False,typeCode=typeCode,
                                                 epsgCode=epsgCode,fullObjects=getFull)         
      except Exception, e:
         layers = None
      else:
         for layer in userLayers:
            try:
               if getFull:
                  try:
                     layers.append((layer.title,layer.id,layer))
                  except:
                     layers.append((layer.name,layer.id,layer))              
               else:
                  layers.append((layer.title,layer.id))
            except Exception,e:
               #layers.append((layer.id,layer.id))
               pass # if no title on the layer, don't add
      return layers
   
      
   def buildPromptLayer(self):
      """
      @summary: layer to prompt the user, beginning layer
      @return: QHBoxLayout, with with typecode,layer, and subtract button widgets
      """
      typeCodeEdit = QtGui.QComboBox()
      for code in self.allTypeCodes:
         typeCodeEdit.addItem(code[0], userData=code[1])
      #typeCodeEdit.addItems(self.allTypeCodes)     
      layerNameEdit = QtGui.QComboBox()
      layerNameEdit.addItem('',0)
      layerNameEdit.setEnabled(False)  
      populateLayerCombo = lambda index: self.populateLayerCombo(index, typeCodeEdit, layerNameEdit) 
      typeCodeEdit.currentIndexChanged.connect(populateLayerCombo)  
      subtractButton = LmPushButton("-",self)
      subtractButton.setMaximumSize(20, 20)      
      firstLayer = QtGui.QHBoxLayout()    
      
      subtractButton.clicked.connect(lambda: self.subtractRow(firstLayer))
      
      firstLayer.addWidget(typeCodeEdit )
      firstLayer.addWidget(layerNameEdit)     
      firstLayer.addWidget(subtractButton)
      
      return firstLayer
# ..............................................................................   
   def buildFirstModelingLayers(self):
      """
      @summary: builds first two blank layers for non match scenario
      """
      
      # first build the labels and add
      labelBox = QtGui.QHBoxLayout()
      
      typeCodeLabel = QtGui.QLabel("Layer Type Code (Unique)")
      typeCodeLabel.setMaximumHeight(25)
      layerNameLabel = QtGui.QLabel("Layer (Unique)")
      layerNameLabel.setMaximumHeight(25)
      
      labelBox.addWidget(typeCodeLabel)
      labelBox.addWidget(layerNameLabel)
      
      self.gridLayout.addLayout(labelBox,2,0,1,1)
      
      
      firstLayer = self.buildPromptLayer()
      secondLayer = self.buildPromptLayer()
      
      ##################################
      addButton = LmPushButton("+",self)
      addButton.setMaximumSize(20, 20)
      
      addButton.clicked.connect(lambda: self.addRow())
      
      self.addRowLayout = QtGui.QHBoxLayout()
      
      self.addRowLayout.addSpacing(self.size().width()+70)
      self.addRowLayout.addWidget(addButton)
      
      
      
      self.layerRows.append(firstLayer)
      self.layerRows.append(secondLayer)
      
      self.setEnableRows(False,addRow=True)
      
      self.gridLayout_input.addLayout(firstLayer)
      self.gridLayout_input.addLayout(secondLayer)
      self.gridLayout_input.addLayout(self.addRowLayout)
# ..........................................................................      
   def setEnableRows(self,enable,addRow=False):
      """
      @summary: enables or disables rows in self.addRowLayout if addRow
      and layer rows in self.layerRows
      """
      if not enable: # if turning off layers
         if addRow:
            for itemIdx in range(0,self.addRowLayout.count()):
               try:
                  self.addRowLayout.itemAt(itemIdx).widget().setEnabled(enable)    
               except:
                  pass    
         for layer in self.layerRows:
            for itemIdx in range(0,layer.count()):
               layer.itemAt(itemIdx).widget().setEnabled(enable)
      else: # if turning on layers
         if addRow:
            for itemIdx in range(0,self.addRowLayout.count()):
               try:
                     self.addRowLayout.itemAt(itemIdx).widget().setEnabled(enable)    
               except:
                  pass    
         for layer in self.layerRows:
            for itemIdx in range(0,layer.count()):
               if itemIdx != 1:
                  layer.itemAt(itemIdx).widget().setEnabled(enable)
         
        
# ..............................................................................   
   def duplicates(self,lst):
      cnt= Counter(lst)
      return [key for key in cnt.keys() if cnt[key]> 1]
# ..............................................................................   
   def indices(self,lst, items= None):
      items, ind= set(lst) if items is None else items, defaultdict(list)
      for i, v in enumerate(lst):
         if v in items: ind[v].append(i)
      return ind
# ..............................................................................   
   def highLiteLayerErrors(self,position):
      """
      @summary: highlites cells that are empty or repeats
      @param position: list of tuples (x,y) of position
      that needs to be highlited
      """
      for y,x in position:
         self.layerRows[y].itemAt(x).widget().setStyleSheet("background-color: #F5693B")

# ..............................................................................         
   def unHighLiteAll(self):
      """
      @summary: unhighlites every elment in the form
      """
      self.scenarioName.setStyleSheet("background-color: white")
      self.scenarioTitle.setStyleSheet("background-color: white")
      self.epsgCodeEdit.setStyleSheet("background-color: white")
      for layer in self.layerRows:
         for itemIdx in range(0,layer.count()):
            if type(layer.itemAt(itemIdx).widget()) == QtGui.QLineEdit:
               layer.itemAt(itemIdx).widget().setStyleSheet("background-color: white")
            elif type(layer.itemAt(itemIdx).widget()) == QtGui.QComboBox:
               layer.itemAt(itemIdx).widget().setStyleSheet("")   
               
# ..............................................................................   
   def validate(self):
         
      self.unHighLiteAll()
      uniqueCompare = []
      problemIdxs = []
      valid = True
      self.actualRows = list(self.layerRows)
      # check for layer set name, and epsg
      layerSetName = self.scenarioName.text()
      layerSetTitle = self.scenarioTitle.text()
      epsgCode = str(self.epsgCodeEdit.text())
      #if self.postAsLayerSet:
      if len(layerSetName) == 0:
         valid = False
         self.scenarioName.setStyleSheet("background-color: #F5693B")
      if len(layerSetTitle) == 0: 
         valid = False
         self.scenarioTitle.setStyleSheet("background-color: #F5693B")
            
      try:
         int(epsgCode)
      except:
         self.epsgCodeEdit.setStyleSheet("background-color: #F5693B")
         valid = False
      else:
         if len(epsgCode) == 0: 
            self.epsgCodeEdit.setStyleSheet( "background-color: #F5693B")
            valid = False
      
             
      # check for repeats and empty fields in layers
      for idx,layout in enumerate(self.layerRows):
         
         if not self.match:
            currentTypecodeIdx = layout.itemAt(self.typeCodeIdx).widget().currentIndex()
            typecode = layout.itemAt(self.typeCodeIdx).widget().currentText()
         else:
            currentTypecodeIdx = 1
            typecode = layout.itemAt(self.typeCodeIdx).widget().text()
             
         currentLayerIdIdx =  layout.itemAt(self.layerIdIdx).widget().currentIndex() 
         layerId = layout.itemAt(self.layerIdIdx).widget().itemData(currentLayerIdIdx,role=QtCore.Qt.UserRole)
         layerName = layout.itemAt(self.layerIdIdx).widget().currentText() 
                       
         if  (currentTypecodeIdx == 0 or currentLayerIdIdx == 0) and \
         (not(currentTypecodeIdx == 0 and currentLayerIdIdx == 0)):           
            if currentTypecodeIdx == 0:
               valid = False
               problemIdxs.append((idx,self.typeCodeIdx))
            if currentLayerIdIdx == 0:
               valid = False
               problemIdxs.append((idx,self.layerIdIdx))
            #uniqueCompare.append([typecode,layerId]) 
         elif  currentTypecodeIdx == 0 and currentLayerIdIdx == 0:
            self.actualRows.remove(layout) 
         else:
            uniqueCompare.append([typecode,layerName])  
      # now check for duplicates 
      if len(uniqueCompare) > 0:    
         typecolumn = list(zip(*uniqueCompare)[0]) 
                   
         layernamecolumn = list(zip(*uniqueCompare)[1])  
          
         typedups = self.indices(typecolumn, self.duplicates(typecolumn))
         layernamedups = self.indices(layernamecolumn, self.duplicates(layernamecolumn)) 
         if typedups:
            valid = False
            for value in typedups.values():
               for idx in value:
                  problemIdxs.append((idx,self.typeCodeIdx))
         if layernamedups:
            valid = False
            for value in layernamedups.values():
               for idx in value:
                  problemIdxs.append((idx,self.layerIdIdx))  
      if not valid:
         self.highLiteLayerErrors(problemIdxs)        
      return valid
         
         
# ....................................................................................
   def showFileDialog(self, layerLayout):
      """
      @summary: Shows a file selection dialog
      """
      fileEdit = layerLayout.itemAt(self.fileNameIdx).widget()
      if not fileEdit.isEnabled():
         hiddenId = layerLayout.itemAt(self.fileNameIdx+1).widget()
         hiddenId.setText('')
         fileEdit.setEnabled(True)
         if not self.match:
            layerLayout.itemAt(self.typeCodeIdx).widget().setText('')
            layerLayout.itemAt(self.typeCodeIdx).widget().setEnabled(True)
            layerLayout.itemAt(self.layerNameIdx).widget().setText('')
            layerLayout.itemAt(self.layerNameIdx).widget().setEnabled(True)
         else:
            layerLayout.itemAt(self.layerNameIdx).widget().setText('')
            layerLayout.itemAt(self.layerNameIdx).widget().setEnabled(True)
      settings = QtCore.QSettings()
      filetypestr = "raster Files (*.*)"
      dirName = settings.value( "/UI/lastShapefileDir" )
      fileDialog = QgsEncodingFileDialog( self, "Open File", dirName,filetypestr)
      fileDialog.setDefaultSuffix("shp"  )
      fileDialog.setFileMode( QtGui.QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptOpen )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QtGui.QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      file = filename[0]
      self.addFileName(file,fileEdit)
# ..........................................................................   
   def addFileName(self,file,fileEdit):
      
      fileEdit.setText(file)
# ..........................................................................      
   def subtractRow(self,layout):
      """
      @summary: deletes a HBox layout from the vertical layout for rows, and delete from layerRows
      @param layout: layout to remove
      """
      if len(self.layerRows) > 1:
         self.layerRows.remove(layout)
         while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
               widget.deleteLater()
        
# ..........................................................................         
   def addRow(self):
      """
      @summary: adds a row for user input to a layer set
      """

      typeCodeEdit = QtGui.QComboBox()
      layerNameEdit = QtGui.QComboBox()
      layerNameEdit.addItem('', userData=0)
      layerNameEdit.setEnabled(False)
      #typeCodeEdit.addItems(self.allTypeCodes)
      for code in self.allTypeCodes:
         typeCodeEdit.addItem(code[0], userData=code[1])
      populateLayerCombo = lambda index: self.populateLayerCombo(index, typeCodeEdit, layerNameEdit)
      typeCodeEdit.currentIndexChanged.connect(populateLayerCombo)
      subtractButton = QtGui.QPushButton("-")
      subtractButton.setMaximumSize(20, 20)
      
            
      newRow = QtGui.QHBoxLayout()
      
      newRow.addWidget(typeCodeEdit )
      newRow.addWidget(layerNameEdit)      
      newRow.addWidget(subtractButton)
      
      
      subtractButton.clicked.connect(lambda: self.subtractRow(newRow))
      self.layerRows.append(newRow)  
           
    
      count = self.gridLayout_input.count()
      self.gridLayout_input.insertLayout(count-1,newRow)                                                             
      #self.gridLayout_input.addLayout(newRow)
# ..........................................................................      
   def openProjSelectorSetEPSG(self):
      """
      @summary: opens the stock qgis projection selector
      and sets epsg edit field and set map units attribute
      """
      projSelector = QgsGenericProjectionSelector(self)
      dialog = projSelector.exec_()
      epsgCode = projSelector.selectedAuthId().replace('EPSG:','')
      # some projections don't have epsg's
      if dialog != 0:
         if epsgCode != 0:  # will be zero if projection doesn't have an epsg
            self.epsgCodeEdit.setText(str(epsgCode))
            self.epsgCodeEdit.setModified(True)
            self.epsgEdited()            
         else:      
            message = "The projection you have chosen does not have an epsg code"
            msgBox = QtGui.QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QtGui.QMessageBox.Ok)
      
# ..........................................................................                 
   def help(self):
      helpWindow = QtGui.QDialog()
      helpWindow.setWindowTitle("Lifemapper Help")
      self.help = QtGui.QWidget(helpWindow)
      #self.help.setWindowTitle('LmSDM Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QtGui.QVBoxLayout()
      helpDialog = QtGui.QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QtCore.QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor(self.helpAnchor)
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      #if self.isModal():
      #   self.setModal(False)
      #self.help.show()   
      helpWindow.exec_()
      
      
      
      
if __name__ == "__main__":
#  
   client =  LMClient(userId='', pwd='')
   qApp = QtGui.QApplication(sys.argv)
   #d = PostScenarioDialog(match=True,scenarioId=204,client=client)
   d = PostScenarioDialog(client=client)
   d.show()
   sys.exit(qApp.exec_())
   
   
   
   