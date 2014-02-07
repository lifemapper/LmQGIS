# -*- coding: utf-8 -*-
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
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *

class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(400, 690)
      self.setMinimumSize(310,630)
      self.setMaximumSize(800,1430)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      
      self.gridLayout_input = QtGui.QVBoxLayout()
      
      self.inputGroup.setLayout(self.gridLayout_input)
      
      
      self.useSelectedFeature = QtGui.QRadioButton('Use selected feature')
      self.useSelectedFeature.setChecked(False)
      self.useSelectedFeature.setAutoExclusive(False)
      #QtCore.QObject.connect(self.useSelectedFeature, QtCore.SIGNAL("clicked()"), self.checkUseSelected)
      self.useSelectedFeature.clicked.connect(self.checkUseSelected)
      self.gridLayout_input.addWidget(self.useSelectedFeature)
      
      self.drawPoly = QtGui.QRadioButton('Draw Polygon')
      self.drawPoly.setChecked(False)
      self.drawPoly.setAutoExclusive(False)
      self.drawPoly.setEnabled(False)
      self.gridLayout_input.addWidget(self.drawPoly)
      
      self.enterCoords = QtGui.QRadioButton('Enter Coords')
      self.enterCoords.setChecked(True)
      self.enterCoords.setAutoExclusive(False)   
      #QtCore.QObject.connect(self.enterCoords, QtCore.SIGNAL("clicked()"), self.checkEnterCoords)
      self.enterCoords.clicked.connect(self.checkEnterCoords)
      self.gridLayout_input.addWidget(self.enterCoords)
      
      
      self.boundingBoxLayout = QtGui.QGridLayout()
      self.boundingBoxLayout.setRowMinimumHeight(0,15)
      self.boundingBoxLayout.setRowMinimumHeight(1,20)
      self.boundingBoxLayout.setRowMinimumHeight(2,23)
      self.boundingBoxLayout.setRowMinimumHeight(3,20)
      self.boundingBoxLayout.setRowMinimumHeight(4,23)
      self.boundingBoxLayout.setRowMinimumHeight(5,20)
      self.boundingBoxLayout.setRowMinimumHeight(6,23)
      
      self.boundingBoxLayout.setColumnMinimumWidth(0,5)
      self.boundingBoxLayout.setColumnMinimumWidth(1,119)
      self.boundingBoxLayout.setColumnMinimumWidth(2,5)
      self.boundingBoxLayout.setColumnMinimumWidth(3,119)
      self.boundingBoxLayout.setColumnMinimumWidth(4,5)
      self.boundingBoxLayout.setColumnMinimumWidth(5,119)
      self.boundingBoxLayout.setColumnMinimumWidth(6,20)
      
      
      
      self.nlabel = QtGui.QLabel("Max Y")
      self.northEdit = QtGui.QLineEdit()
      self.northEdit.setMaximumHeight(25)
      self.northEdit.setMinimumWidth(118)
      self.northEdit.setEnabled(True)
      self.northEdit.setReadOnly(False)
       
      self.slabel = QtGui.QLabel("Min Y")
      self.southEdit = QtGui.QLineEdit()
      self.southEdit.setMaximumHeight(25)
      self.southEdit.setMinimumWidth(118)
      
      self.wlabel = QtGui.QLabel("Min X")
      self.westEdit = QtGui.QLineEdit()
      self.westEdit.setMaximumHeight(25)
      self.westEdit.setMinimumWidth(118)

      self.elabel = QtGui.QLabel("Max X")
      self.eastEdit = QtGui.QLineEdit()
      self.eastEdit.setMaximumHeight(25)
      self.eastEdit.setMinimumWidth(118)
      
      self.boundingBoxLayout.addWidget(self.nlabel,   1,3,1,1,alignment=QtCore.Qt.AlignHCenter)
      self.boundingBoxLayout.addWidget(self.northEdit,2,3,1,1)
      self.boundingBoxLayout.addWidget(self.slabel,   5,3,1,1,alignment=QtCore.Qt.AlignHCenter)
      self.boundingBoxLayout.addWidget(self.southEdit,6,3,1,1)
      
      self.boundingBoxLayout.addWidget(self.wlabel,   3,1,1,1,alignment=QtCore.Qt.AlignHCenter)
      self.boundingBoxLayout.addWidget(self.westEdit, 4,1,1,1)
      self.boundingBoxLayout.addWidget(self.elabel,   3,5,1,1,alignment=QtCore.Qt.AlignHCenter)
      self.boundingBoxLayout.addWidget(self.eastEdit, 4,5,1,1)
      
      self.gridLayout_input.addLayout(self.boundingBoxLayout)
      #
      #
      #
      self.shapelabel = QtGui.QLabel("Cell Shape")
      
      self.shapeHorizBox = QtGui.QHBoxLayout()
      self.hexCheck = QtGui.QRadioButton('hexagonal')
      self.hexCheck.setChecked(True)
      self.shapeHorizBox.addWidget(self.hexCheck)
      self.squareCheck = QtGui.QRadioButton('square')
      self.squareCheck.setChecked(False)
      self.shapeHorizBox.addWidget(self.squareCheck)
      self.shapeHorizBox.addSpacing(189)
      
      self.gridLayout_input.addSpacing(15)
      self.gridLayout_input.addWidget(self.shapelabel)
      self.gridLayout_input.addLayout(self.shapeHorizBox)
      self.gridLayout_input.addSpacing(15)
      
      
      self.epsglabel = QtGui.QLabel("EPSG Code")    
      self.epsgEdit = QtGui.QLineEdit()
      self.epsgEdit.setMaximumWidth(218)
      self.gridLayout_input.addWidget(self.epsglabel)
      self.gridLayout_input.addWidget(self.epsgEdit)
      
      #
      #
      ## map units????????????
      ## [feet|inches|kilometers|meters|miles|nauticalmiles|dd]
      #
      self.mapunitslabel = QtGui.QLabel("Map Units")
      self.selectUnits = QtGui.QComboBox()
      self.selectUnits.setMaximumWidth(218)
      self.selectUnits.addItem("feet",
           '1')
      self.selectUnits.addItem("inches",
          'inches')
      self.selectUnits.addItem("kilometers",
           'kilometers')
      self.selectUnits.addItem("meters",
           '0')
      self.selectUnits.addItem("miles",
           'miles')
      self.selectUnits.addItem("nauticalmiles",
           'nauticalmiles')
      self.selectUnits.addItem("dd",
           '2')
      self.gridLayout_input.addWidget(self.mapunitslabel)
      self.gridLayout_input.addWidget(self.selectUnits)
      #   
      # 
      self.reslabel = QtGui.QLabel("Cell Size in map units")
      self.resEdit = QtGui.QLineEdit()
      self.resEdit.setMaximumWidth(218)
      self.gridLayout_input.addWidget(self.reslabel)
      self.gridLayout_input.addWidget(self.resEdit)
      #
      #
      # 
      
      #self.outlabel = QtGui.QLabel("Output filename")
      #self.gridLayout_input.addWidget(self.outlabel)
      #
      #self.fileHorizLayout = QtGui.QHBoxLayout()
      #self.outEdit = QtGui.QLineEdit()
      ##self.outEdit.setMaximumWidth(218)
      #self.fileHorizLayout.addWidget(self.outEdit)
      #
      #self.fileButton = QtGui.QPushButton("Browse")
      #self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
      #self.fileHorizLayout.addWidget(self.fileButton)
      #self.fileHorizLayout.addSpacing(47)
      #
      #self.gridLayout_input.addLayout(self.fileHorizLayout)
      #
      self.namelabel = QtGui.QLabel("Grid Name")
      self.nameEdit = QtGui.QLineEdit()
      self.nameEdit.setMaximumWidth(218)
      self.gridLayout_input.addWidget(self.namelabel)
      self.gridLayout_input.addWidget(self.nameEdit)
      #
      
      ################ output group ############################### 
      self.outputGroup = QtGui.QGroupBox(self)
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout.addWidget(self.outputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
       
      self.statuslabel = QtGui.QLabel(self.outputGroup)
      self.gridLayout_output.addWidget(self.statuslabel)
      self.statuslabel.setText(QtGui.QApplication.translate("self", 
         'Running Process', None, QtGui.QApplication.UnicodeUTF8))
      
      self.progressbar = QtGui.QProgressBar(self.outputGroup)
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.gridLayout_output.addWidget(self.progressbar)
       
      self.outputGroup.hide()
      
      ##############################################################
       
      self.acceptBut = QtGui.QPushButton("OK",self)
      self.acceptBut.setDefault(True)
      self.rejectBut = QtGui.QPushButton("Close",self)
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      #QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      self.helpBut.clicked.connect(self.help)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      
      self.gridLayout.addWidget(self.inputGroup,0,0,1,3)
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
         
   
      self.retranslateUi()
      
      #QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      #QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept)
      
      self.rejectBut.clicked.connect(self.reject)
      self.acceptBut.clicked.connect(self.accept)
       
      
      
      
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QtCore.QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" )
      fileDialog = QgsEncodingFileDialog( self, "Save .zip File", dirName,"Zip Files (*.zip)")
      fileDialog.setDefaultSuffix( "zip"  )
      fileDialog.setFileMode( QtGui.QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QtGui.QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      self.addFile(filename[0])

   def addFile(self,filename):
      self.outEdit.setText(filename)


     

           
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Construct Macroecology Grid", None, QtGui.QApplication.UnicodeUTF8))
      #self.checkBoxExisting.setText(QtGui.QApplication.translate("self", 
      #   "Choose Existing Process", None, QtGui.QApplication.UnicodeUTF8))
      #self.checkBoxURL.setText(QtGui.QApplication.translate("self", 
      #   "Enter Describe Process URL", None, QtGui.QApplication.UnicodeUTF8))
      #self.btnSubmitDescribe.setText(QtGui.QApplication.translate("self",
      #   "Submit Request", None, QtGui.QApplication.UnicodeUTF8))
   
   