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

#from lifemapperTools.common.pluginconstants import KUNHM_GC_DESCRIBE_PROCESS_URL, \
#  STATUS_ACCEPTED, STATUS_FAILED, STATUS_SUCCEEDED, STATUS_STARTED, FIND_STATUS


class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(508, 590)
      self.setMinimumSize(308,390)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.inputGroup.setTitle('Metadata')
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout_input.setObjectName("gridLayout_input")
      self.gridLayout.addLayout(self.gridLayout_input, 0,0,1,1)
      
      
      self.gridLayout_input.setRowMinimumHeight(0,20)
      self.gridLayout_input.setRowMinimumHeight(1,170)
      self.gridLayout_input.setRowMinimumHeight(2,400)
      self.gridLayout_input.setColumnMinimumWidth(0,15)
      self.gridLayout_input.setColumnMinimumWidth(1,490)
      
      self.metaDataGrid = QtGui.QGridLayout()
      self.metaDataGrid.setRowMinimumHeight(0,10)
      self.metaDataGrid.setRowMinimumHeight(1,65)
      self.metaDataGrid.setRowMinimumHeight(2,10)
      self.metaDataGrid.setRowMinimumHeight(3,65)
      self.metaDataGrid.setColumnMinimumWidth(0,90)
      self.metaDataGrid.setColumnMinimumWidth(1,100)
      self.metaDataGrid.setColumnMinimumWidth(2,40)
      self.metaDataGrid.setColumnMinimumWidth(3,90)
      
      self.displayNameLabel = QtGui.QLabel("Point Layer Name")
      self.epsgCodeLabel = QtGui.QLabel("EPSG Code")
      self.displayNameEdit = QtGui.QLineEdit()
      self.epsgCodeEdit = QtGui.QLineEdit()
      self.projectionPickerBut = QtGui.QPushButton("Browse")
      self.projectionPickerBut.clicked.connect(self.openProjSelectorSetEPSG)
      
      
      self.metaDataGrid.addWidget(self.displayNameLabel,   0,1,1,1)
      self.metaDataGrid.addWidget(self.displayNameEdit,    1,1,1,2)
      self.metaDataGrid.addWidget(self.epsgCodeLabel,      2,1,1,1)
      self.metaDataGrid.addWidget(self.epsgCodeEdit,       3,1,1,1)
      self.metaDataGrid.addWidget(self.projectionPickerBut,3,2,1,1)
      
      self.stepLabel1 = QtGui.QLabel("1.")
      self.stepLabel2 = QtGui.QLabel("2.")
      
      
      self.gridLayout_input.addWidget(self.stepLabel1,  1,0,1,1,QtCore.Qt.AlignTop)
      self.inputGroup.setLayout(self.metaDataGrid) 
      self.gridLayout_input.addWidget(self.inputGroup,1,1,1,1)
      
      
      self.inputGroup2 = QtGui.QGroupBox()
      self.inputGroup2.setObjectName("inputGroup2")
      self.inputGroup2.setTitle('File')
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup2.setStyle(self.style)
      
      self.fileGrid = QtGui.QGridLayout()
      self.fileGrid.setRowMinimumHeight(0,10)
      self.fileGrid.setRowMinimumHeight(1,45)
      self.fileGrid.setRowMinimumHeight(2,10)
      self.fileGrid.setRowMinimumHeight(3,45)
      self.fileGrid.setRowMinimumHeight(4,30)
      self.fileGrid.setRowMinimumHeight(5,10)
      self.fileGrid.setRowMinimumHeight(6,45)
      
      self.fileGrid.setColumnMinimumWidth(0,40)
      self.fileGrid.setColumnMinimumWidth(1,280)
      self.fileGrid.setColumnMinimumWidth(2,60)
      self.fileGrid.setColumnMinimumWidth(3,40)
      
      self.fileTypeLabel = QtGui.QLabel("File type")
      self.fileTypeCombo = QtGui.QComboBox()
      self.filePathLabel = QtGui.QLabel("Upload file")
      self.file = QtGui.QLineEdit()
      self.browseBut = QtGui.QPushButton("Browse")
      self.browseBut.clicked.connect(self.showFileDialog)
      self.orLabel = QtGui.QLabel("OR")
      self.canvasLabel = QtGui.QLabel("Select from occurrence layers in canvas")
      self.canvasLayersCombo = QtGui.QComboBox()
      
      
      self.fileGrid.addWidget(self.fileTypeLabel,    0,1,1,1)
      self.fileGrid.addWidget(self.fileTypeCombo,    1,1,1,1)
      self.fileGrid.addWidget(self.filePathLabel,    2,1,1,1)
      self.fileGrid.addWidget(self.file,             3,1,1,1)
      self.fileGrid.addWidget(self.browseBut,        3,2,1,1)
      self.fileGrid.addWidget(self.orLabel,          4,1,1,1,QtCore.Qt.AlignCenter)
      self.fileGrid.addWidget(self.canvasLabel,      5,1,1,1)
      self.fileGrid.addWidget(self.canvasLayersCombo,6,1,1,1)
      
      self.gridLayout_input.addWidget(self.stepLabel2,  2,0,1,1,QtCore.Qt.AlignTop)
      self.inputGroup2.setLayout(self.fileGrid)
      self.gridLayout_input.addWidget(self.inputGroup2,2,1,1,1)
      
      ############ combo initial populate #######
      display = ["CSV","SHAPEFILE"]
      userData = ["csv","shp"]
      for d,uD in zip(display,userData):
         self.fileTypeCombo.addItem(d,userData=uD)
      
      ###### button box ######################### 
      self.uploadBut = QtGui.QPushButton("Upload",self)
      self.buttonBox = QtGui.QDialogButtonBox(self)      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      
     
      self.uploadBut.clicked.connect(self.accept)
      self.helpBut.clicked.connect(self.help)
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.uploadBut, QtGui.QDialogButtonBox.ActionRole)
      
      
      self.buttonBox.setObjectName("buttonBox")
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
           
   
      self.retranslateUi()
      
       
      
     
      
           
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Upload Point Data", None, QtGui.QApplication.UnicodeUTF8))
      
   