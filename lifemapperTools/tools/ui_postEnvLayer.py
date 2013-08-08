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
from lifemapperTools.common.lmClientLib import LMClient
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
import sys
import os.path
from urllib2 import HTTPError
from collections import Counter, defaultdict, namedtuple






class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(700, 580)
      self.setMinimumSize(700,580)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      #self.gridLayout.setColumnMinimumWidth(0,330)
      #self.gridLayout.setColumnMinimumWidth(1,570)
      
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout_input.setRowMinimumHeight(0,160)
      self.gridLayout_input.setRowMinimumHeight(1,90)
      self.gridLayout_input.setRowMinimumHeight(2,190)
      
      
      
      self.outerGroup = QtGui.QGroupBox() 
      style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outerGroup.setStyle(style)
      self.outerGroup.setTitle("Upload Environmental Layer") 
      
      #################### first group #####################
      
      self.titleGroup = QtGui.QGroupBox()
      style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.titleGroup.setStyle(style)
      
      
      self.titleLayout = QtGui.QGridLayout() 
      self.titleLayout.setRowMinimumHeight(0,30)
      self.titleLayout.setRowMinimumHeight(1,30)
      self.titleLayout.setRowMinimumHeight(2,30)
      self.titleLayout.setRowMinimumHeight(3,30)
      
      self.titleLayout.setColumnMinimumWidth(0,205)
      self.titleLayout.setColumnMinimumWidth(1,180)
      self.titleLayout.setColumnMinimumWidth(2,80)
           
      
      self.layerNameLabel = QtGui.QLabel("Layer Name")
      self.layerTitleLabel = QtGui.QLabel("Layer Title")
      
      
      self.layerName = QtGui.QLineEdit()
      self.userEntersName = EnterTextEventHandler()
      self.layerName.installEventFilter(self.userEntersName)
      self.inputElements.append(self.formElement('line',self.layerName))
      #self.layerName.setMaximumWidth(300)
      self.layerTitle = QtGui.QLineEdit()
      self.userEntersTitle = EnterTextEventHandler()
      self.layerTitle.installEventFilter(self.userEntersTitle)
      self.inputElements.append(self.formElement('line',self.layerTitle))
      #self.layerTitle.setMaximumWidth(300)
      
      
      
      self.fileLabel = QtGui.QLabel("File")
      self.fileEdit = QtGui.QLineEdit()
      self.userEntersFile = EnterTextEventHandler()
      self.fileEdit.installEventFilter(self.userEntersFile)
      self.inputElements.append(self.formElement('file',self.fileEdit))
      #self.fileEdit.setMinimumSize(220, 27)
      #self.fileEdit.setMaximumSize(220,27)
      self.fileButton = QtGui.QPushButton("Browse")
      self.fileButton.setMaximumSize(100, 27)
      QtCore.QObject.connect(self.fileButton, QtCore.SIGNAL("clicked()"), self.showFileDialog)
      
      
      self.titleLayout.addWidget(self.layerNameLabel,  0,0,1,1) 
      self.titleLayout.addWidget(self.fileLabel,       0,1,1,1)  
      self.titleLayout.addWidget(self.layerName,       1,0,1,1) 
      self.titleLayout.addWidget(self.fileEdit,        1,1,1,1)
      self.titleLayout.addWidget(self.fileButton,      1,2,1,1)
      self.titleLayout.addWidget(self.layerTitleLabel, 2,0,1,3)
      self.titleLayout.addWidget(self.layerTitle,      3,0,1,3)
      
      self.titleGroup.setLayout(self.titleLayout)
      
      self.gridLayout_input.addWidget(self.titleGroup,0,0,1,1)
     
      ################## 2cnd Group ################
      
      self.layerTypeCodeLabel = QtGui.QLabel("Layer Type Code")
      self.layerTypeCodeLabel.setMaximumHeight(28)
      
      self.selectTypeCode = QtGui.QComboBox()
      self.selectTypeCode.addItem('',
                                     QtCore.QVariant(0))
      self.selectTypeCode.addItem('new...',
                                     QtCore.QVariant(1))
      
      QObject.connect(self.selectTypeCode, 
                      SIGNAL("currentIndexChanged(int)"), self.newTypeCode)
      
      self.inputElements.append(self.formElement('typeCode',self.selectTypeCode))
      self.selectTypeCode.setMaximumHeight(28)
      
      #self.layerTypeCode = QtGui.QLineEdit()
      #self.userEntersType = EnterTextEventHandler()
      #self.layerTypeCode.installEventFilter(self.userEntersType)
      #self.inputElements.append(self.formElement('line',self.layerTypeCode))
      #self.layerTypeCode.setMaximumHeight(28)
      
      self.epsgGroup = QtGui.QGroupBox()
      style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.epsgGroup.setStyle(style)
      
      self.epsgCodeLabel = QtGui.QLabel("EPSG Code")
      self.epsgCodeLabel.setMaximumHeight(28)
 
      
      self.epsgCodeEdit = QtGui.QLineEdit()
      self.userEntersEPSG = EnterTextEventHandler()
      self.epsgCodeEdit.installEventFilter(self.userEntersEPSG)
      self.inputElements.append(self.formElement('epsg',self.epsgCodeEdit))
      self.epsgCodeEdit.setMaximumHeight(28)
     
      self.epsgButton = QtGui.QPushButton("Browse")
      QtCore.QObject.connect(self.epsgButton, QtCore.SIGNAL("clicked()"), self.openProjSelectorSetEPSG)
      
      self.unitsLabel = QtGui.QLabel("Map Units")
      self.unitsLabel.setMaximumHeight(28)
      
      self.selectUnits = QtGui.QComboBox()
      self.inputElements.append(self.formElement('combo',self.selectUnits))
      self.selectUnits.setMaximumHeight(28)
      
      self.selectUnits.addItem("decimal degrees",
           QtCore.QVariant('dd'))
      self.selectUnits.addItem("meters",
           QtCore.QVariant('meters'))
      self.selectUnits.addItem("feet",
           QtCore.QVariant('feet'))
      self.selectUnits.addItem("inches",
           QtCore.QVariant('inches'))
      self.selectUnits.addItem("kilometers",
           QtCore.QVariant('kilometers'))
      self.selectUnits.addItem("miles",
           QtCore.QVariant('miles'))
      self.selectUnits.addItem("nauticalmiles",
           QtCore.QVariant('nauticalmiles'))
      self.selectUnits.setMaximumWidth(300)
      
      self.epsgLayout = QtGui.QGridLayout()
      self.epsgLayout.setRowMinimumHeight(0,30)
      self.epsgLayout.setRowMinimumHeight(1,30)
      self.epsgLayout.setColumnMinimumWidth(0,190)
      self.epsgLayout.setColumnMinimumWidth(1,120)
      self.epsgLayout.setColumnMinimumWidth(2,80)
      self.epsgLayout.setColumnMinimumWidth(3,120)
      
      self.epsgLayout.addWidget(self.layerTypeCodeLabel,0,0,1,1)
      self.epsgLayout.addWidget(self.epsgCodeLabel,     0,1,1,1)
      self.epsgLayout.addWidget(self.unitsLabel,        0,3,1,1)
      self.epsgLayout.addWidget(self.selectTypeCode,     1,0,1,1)
      self.epsgLayout.addWidget(self.epsgCodeEdit,      1,1,1,1)
      self.epsgLayout.addWidget(self.epsgButton,        1,2,1,1)
      self.epsgLayout.addWidget(self.selectUnits,       1,3,1,1)
      
      
      self.epsgGroup.setLayout(self.epsgLayout)
      self.gridLayout_input.addWidget(self.epsgGroup,1,0,1,1)
      
      ##################3rd Group #############################
      
      self.descGroup = QtGui.QGroupBox()
      style = QtGui.QStyleFactory.create("motif")
      self.descGroup.setStyle(style)
      
      self.descLayout = QtGui.QGridLayout()
      self.descLayout.setRowMinimumHeight(0,20)
      self.descLayout.setRowMinimumHeight(1,100)
      
      self.layerDescLabel = QtGui.QLabel("Layer Description")
      self.layerDescLabel.setMaximumHeight(20)
        
      self.layerDesc = QtGui.QTextEdit()
      self.inputElements.append(self.formElement('block',self.layerDesc))
      self.layerDesc.setMinimumHeight(100)
      self.layerDesc.setMaximumHeight(100)
      
      
      
      self.descLayout.addWidget(self.layerDescLabel, 0,0,1,1)#,QtCore.Qt.AlignTop
      self.descLayout.addWidget(self.layerDesc,      1,0,1,1)
      
      self.descGroup.setLayout(self.descLayout)
      self.gridLayout_input.addWidget(self.descGroup,2,0,1,1)
      
     
      
      #############  progress bar ##########
      
      self.progressbar = QtGui.QProgressBar()
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.hide()
      
      self.helpBut = QtGui.QPushButton("?")
      self.helpBut.setMaximumSize(30, 30)
      
      self.acceptBut = QtGui.QPushButton("OK")
      self.rejectBut = QtGui.QPushButton("Close")
      
      self.buttonBox = QtGui.QDialogButtonBox()
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept)
      QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      
      self.outerGroup.setLayout(self.gridLayout_input)   
      
      self.gridLayout.addWidget(self.outerGroup,    0,0,1,1)
      #self.gridLayout.addLayout(self.verticalLayout, 0,0,8,2)
      self.gridLayout.addWidget(self.progressbar,   7,0,1,3)
      self.gridLayout.addWidget(self.buttonBox,     8,0,1,3)
      
      self.setWindowTitle("Upload Layer")
      
   
class EnterTextEventHandler(QObject):
  
   def __init__(self):
      super(EnterTextEventHandler, self).__init__()
      
   def eventFilter(self,object,event):
      if event.type() == QtCore.QEvent.FocusIn:
         if object.styleSheet() == 'background-color: #F5693B':
            object.setStyleSheet(QtCore.QString( "background-color: white"))
      return QtGui.QWidget.eventFilter(self, object, event)
# ............................................................................. 

class Ui_SubDialog(object):
   
   def setupUi(self):
      
      self.resize(360, 260)
      self.setMinimumSize(360,260)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
      self.gridLayout = QtGui.QGridLayout(self) 
      self.verticalLayout = QtGui.QVBoxLayout()
      self.typeCodeLabel = QtGui.QLabel("Type Code Name")
      self.typeCodeName = QtGui.QLineEdit()
      self.typeCodeTitleLabel = QtGui.QLabel("Type Code Title")
      self.typeCodeTitle = QtGui.QLineEdit()
      self.typeCodeDescLabel = QtGui.QLabel("Description")
      self.typeCodeDesc = QtGui.QTextEdit()
      self.verticalLayout.addWidget(self.typeCodeLabel)
      self.verticalLayout.addWidget(self.typeCodeName)
      self.verticalLayout.addWidget(self.typeCodeTitleLabel)
      self.verticalLayout.addWidget(self.typeCodeTitle)
      self.verticalLayout.addWidget(self.typeCodeDescLabel)
      self.verticalLayout.addWidget(self.typeCodeDesc)
      
      self.acceptBut = QtGui.QPushButton("Ok")
      self.rejectBut = QtGui.QPushButton("Close")
      self.helpBut = QtGui.QPushButton("?")
      self.helpBut.setMaximumSize(30, 30)
      
      self.buttonBox = QtGui.QDialogButtonBox()
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      # self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept)
      QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      
      self.gridLayout.addLayout(self.verticalLayout,0,0,1,1)
      self.gridLayout.addWidget(self.buttonBox,     8,0,1,3)
      self.setWindowTitle("Create New Type Code")
          
class PostTypeCodeDialog(QtGui.QDialog,Ui_SubDialog):
      def __init__(self,client=None,interface=None):
         QtGui.QDialog.__init__(self)
         self.setupUi()
         self.typeSubmited = False
         self.client = client
      
      def unHighLiteAll(self):
         self.typeCodeName.setStyleSheet(QtCore.QString( "background-color: white"))
         self.typeCodeTitle.setStyleSheet(QtCore.QString( "background-color: white"))
      def validate(self):
         valid = True
         self.unHighLiteAll()
         if self.typeCodeName.text() == '':
            valid = False
            self.typeCodeName.setStyleSheet(QtCore.QString( "background-color: #F5693B")) 
         if self.typeCodeTitle.text() == '':
            valid = False
            self.typeCodeTitle.setStyleSheet(QtCore.QString( "background-color: #F5693B"))  
         return valid
      
      def reject(self):
         # emit a signal here to the parent to reset type code
         # combo to first index
         self.close()
         if not self.typeSubmited:
            QgsProject.instance().emit( SIGNAL( "insertTypeCode(PyQt_PyObject)" ), None)
         
         
      def closeEvent(self,event):
         if not self.typeSubmited:
            QgsProject.instance().emit( SIGNAL( "insertTypeCode(PyQt_PyObject)" ), None)
      
      def insertTypeCode(self,typeCodeCode):
         QgsProject.instance().emit( SIGNAL( "insertTypeCode(PyQt_PyObject)" ), typeCodeCode)
         
      def accept(self):
         valid = self.validate()
         if valid:
            typeCodeName = self.typeCodeName.text()
            typeCodeTitle = self.typeCodeTitle.text()
            description = str( self.typeCodeDesc.toPlainText())
            try:
               newCode = self.client.sdm.postTypeCode(typeCodeName, title=typeCodeTitle, description=description)
            except Exception,e:
               message = "Could not post new type code "+str(e)
               msgBox = QMessageBox.warning(self, "Problem...", message, QMessageBox.Ok)
            else:
               self.typeSubmited = True
               self.insertTypeCode(typeCodeName)
               message = "Created new type code"
               msgBox = QMessageBox.information(self, "Success...", message, QMessageBox.Ok)
            self.close()
            
      def help(self):
         helpWindow = QtGui.QDialog()
         helpWindow.setWindowTitle("Lifemapper Help")
         self.help = QWidget(helpWindow)
         #self.help.setWindowTitle('Lifemapper Help')
         self.help.resize(600, 400)
         self.help.setMinimumSize(600,400)
         self.help.setMaximumSize(1000,1000)
         layout = QVBoxLayout()
         helpDialog = QTextBrowser()
         helpDialog.setOpenExternalLinks(True)
         #helpDialog.setSearchPaths(QStringList('documents'))
         helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
         helpDialog.setSource(QUrl.fromLocalFile(helppath))
         helpDialog.scrollToAnchor('newTypeCode')
         layout.addWidget(helpDialog)
         self.help.setLayout(layout)
         #if self.isModal():
         #   self.setModal(False)
         #self.help.show() 
         helpWindow.exec_()
               
class PostEnvLayerDialog(QtGui.QDialog, Ui_Dialog):   
   
   def __init__(self, client=None, interface=None):
      QtGui.QDialog.__init__(self)
      self.inputElements = []
      self.formElement = namedtuple('QLineElement',['type','element'])
      self.iface = interface
      self.client = client
      self.postSucceeded = False
      self.setupUi()
      QObject.connect(QgsProject.instance(),
                      SIGNAL("insertTypeCode(PyQt_PyObject)"),
                      self.insertTypeCode)
      self.typeCodes = self.getTypeCodes()
      if self.typeCodes is not None:
         self.populateTypeCodes()
         
   def insertTypeCode(self,newTypeCode):
      """
      @summary: inserts new type code into combobox, connected to signal from new
      type code sub dialog
      """
      if newTypeCode is not None:
         self.selectTypeCode.insertItem(2, newTypeCode, userData=QVariant(newTypeCode))
         self.selectTypeCode.setCurrentIndex(2)
      else:
         self.selectTypeCode.setCurrentIndex(0)
      
# .............................................................................
   def newTypeCode(self, index):
      if self.selectTypeCode.styleSheet():
         self.selectTypeCode.setStyleSheet(QtCore.QString(""))
      if index == 1:
         self.uploadTypeCode = PostTypeCodeDialog(interface=self.iface, client=self.client)
         self.uploadTypeCode.exec_()
# .............................................................................       
   def addFileName(self,file):
      
      self.fileEdit.setText(file) 
# .............................................................................    
   def unHighLiteAll(self):
      for t in self.inputElements:
         if t.type != 'combo' and t.type != 'block' and t.type != 'typeCombo':
            t.element.setStyleSheet(QtCore.QString( "background-color: white"))

# ............................................................................. 
   def getTypeCodes(self):
      try:
         typeCodes = self.client.sdm.listTypeCodes(public=False,fullObjects=True)
         
      except:
         typeCodes = None
      return typeCodes
# .............................................................................          
   def populateTypeCodes(self):
      
      for code in self.typeCodes:
         try:
            self.selectTypeCode.addItem(code.typeTitle,
                                     QtCore.QVariant(code.typeCode))
         except:
            try:
               self.selectTypeCode.addItem(code.typeCode,
                                     QtCore.QVariant(code.typeCode))
            except:
               pass
# ................................................................................            
   def validate(self):
      self.unHighLiteAll()
      valid = True
      for t in self.inputElements:
         if t.type != 'combo' and t.type != 'block' and t.type != 'typeCode':
            if t.type == 'file':
               if not(os.path.exists(t.element.text())):
                  valid = False
                  t.element.setStyleSheet(QtCore.QString( "background-color: #F5693B"))             
            elif t.type == 'epsg':
               try:
                  int(t.element.text())
               except:
                  valid = False
                  t.element.setStyleSheet(QtCore.QString( "background-color: #F5693B"))                                  
            else:
               if len(t.element.text()) == 0:
                  valid = False
                  t.element.setStyleSheet(QtCore.QString( "background-color: #F5693B")) 
         elif t.type == 'typeCode':
            currentIdx = t.element.currentIndex()
            if currentIdx == 0 or currentIdx == 1:
               t.element.setStyleSheet(QtCore.QString( "background-color: #F5693B"))
            
                                          
      return valid                 
# ................................................................................... 
   def resetForm(self):
      self.progressbar.reset()
      self.progressbar.hide()
      for t in self.inputElements:
         if t.type != 'combo' and t.type != 'typeCode':
            t.element.setText('')
         else:
            t.element.setCurrentIndex(0)
            
   def getDataFormat(self,extension):
      if extension == "asc":
         extension = 'AAIGrid'
      elif extension == 'tif':
         extension = 'GTiff'
      return extension
# ...................................................................................                       
   def accept(self):
      valid = self.validate()
      if valid:
         self.progressbar.show()
         #print "it should be showing progress"
         try:
            name = str(self.layerName.text())
            epsgCode = str(self.epsgCodeEdit.text())
            title = str(self.layerTitle.text())
            typeIdx = self.selectTypeCode.currentIndex()
            envLayerType = str(self.selectTypeCode.itemData(typeIdx,role=QtCore.Qt.UserRole).toString())
            unitsIdx = self.selectUnits.currentIndex()
            units = str(self.selectUnits.itemData(unitsIdx, role=QtCore.Qt.UserRole).toString())
            fileName = str(self.fileEdit.text())
            description = str(self.layerDesc.toPlainText())
            #     GTiff 
            extension = os.path.basename(fileName).split(".")[1]
            dataFormat = self.getDataFormat(extension)
            obj = self.client.sdm.postLayer(name, epsgCode, envLayerType, 
                                            units, dataFormat, title=title,
                                            description=description,
                                            fileName=fileName)
         except HTTPError,e:
            if e.code == 409:
               message = "Layer already exists with this name with a different type code, unable to upload"
         except Exception, e:
            message = "Upload Layer Failed "+str(e)
            self.progressbar.reset()
            self.progressbar.hide()
         else:
            for progress in range(1,100):
               self.progressbar.setValue(progress) 
            self.resetForm()
            message = "Successfully uploaded environmental layer"
         msgBox = QtGui.QMessageBox.information(self,
                                                "Status...",
                                                message,
                                                QtGui.QMessageBox.Ok)                                            
# ..................................................................................             
   def openProjSelectorSetEPSG(self):
      """
      @summary: opens the stock qgis projection selector
      and sets epsg edit field and set map units attribute
      """
      projSelector = QgsGenericProjectionSelector(self)
      dialog = projSelector.exec_()
      epsgCode = projSelector.selectedEpsg()
      # some projections don't have epsg's
      if dialog != 0:
         if epsgCode != 0:  # will be zero if projection doesn't have an epsg
            crs = QgsCoordinateReferenceSystem()
            crs.createFromOgcWmsCrs( projSelector.selectedAuthId() )
            mapunitscode = crs.mapUnits()
            if mapunitscode == 0:
               mapunits = 'meters'
            elif mapunitscode == 1:
               mapunits = 'feet'
            elif mapunitscode == 2:
               mapunits = 'dd' 
            self.epsgCodeEdit.setText(str(epsgCode))
            unitsIdx = self.selectUnits.findData(QtCore.QVariant(mapunits), role=QtCore.Qt.UserRole)
            self.selectUnits.setCurrentIndex(unitsIdx)
         else:
            # error message saying that the users chosen projection doesn't have a epsg
            
            message = "The projection you have chosen does not have an epsg code"
            msgBox = QtGui.QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QtGui.QMessageBox.Ok)
      else:
         pass  
# ...........................................................................       
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      
      settings = QtCore.QSettings()
      filetypestr = "raster Files (*.tif  *.asc)"
      dirName = settings.value( "/UI/lastShapefileDir" ).toString()
      fileDialog = QgsEncodingFileDialog( self, "Open File", dirName,filetypestr)
      #fileDialog.setDefaultSuffix( QtCore.QString( "shp" ) )
      fileDialog.setFileMode( QtGui.QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptOpen )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QtGui.QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      file = filename.first()
      self.addFileName(file)
# ...........................................................................      
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(QStringList('documents'))
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('uploadEnvLayer')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
            
      
if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QtGui.QApplication(sys.argv)
   #d = PostScenarioDialog(match=True,scenarioId=112,client=client)
   d = PostEnvLayerDialog(client=client)
   d.show()
   sys.exit(qApp.exec_())
         
      