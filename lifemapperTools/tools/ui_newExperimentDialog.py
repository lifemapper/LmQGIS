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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import operator
#from lifemapperTools.common.pluginconstants import KUNHM_GC_DESCRIBE_PROCESS_URL, \
#  STATUS_ACCEPTED, STATUS_FAILED, STATUS_SUCCEEDED, STATUS_STARTED, FIND_STATUS


class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(648, 428)
      self.setMinimumSize(648,428)
      self.setMaximumSize(648,428)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      
      self.inputGroup = QtGui.QGroupBox(self)
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.gridLayout_input = QtGui.QGridLayout(self.inputGroup)
      self.gridLayout_input.setObjectName("gridLayout_input")
      self.gridLayout.addWidget(self.inputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
     
      
      self.expNameLabel = QtGui.QLabel(self.inputGroup)
      self.expNameLabel.setGeometry(QtCore.QRect(10, 30, 123, 25))
      self.expNameLabel.setText('Experiment Name')
      
      self.expNameEdit = QtGui.QLineEdit(self.inputGroup)
      self.expNameEdit.setGeometry(QtCore.QRect(10, 60, 233, 25))
      self.expNameEdit.setObjectName('expNameEdit')
      
      
      
      self.epsgLabel = QtGui.QLabel(self.inputGroup)
      self.epsgLabel.setGeometry(QtCore.QRect(10, 110, 223, 25))
      self.epsgLabel.setText('Define Experiment Projection')
      
      
      self.epsgEdit = QtGui.QLineEdit(self.inputGroup)
      self.epsgEdit.setGeometry(QtCore.QRect(10, 140, 163, 25))
      self.epsgEdit.setObjectName('epsgEdit')
      
      self.openProjSelectBut = QtGui.QPushButton('Browse',self)
      self.openProjSelectBut.clicked.connect(self.openProjSelectorSetEPSG)
      self.openProjSelectBut.setMinimumSize(60, 25)
      self.openProjSelectBut.setMaximumSize(60,25)
      self.openProjSelectBut.setGeometry(QtCore.QRect(191, 151, 20, 20))
      
      self.descLabel   = QtGui.QLabel(self.inputGroup)  
      self.descLabel.setText("Experiment Description") 
      self.descLabel.setGeometry(QtCore.QRect(10, 190, 170, 20)) 
      self.description = QtGui.QTextEdit(self.inputGroup)
      self.description.setMaximumSize(230, 78)
      self.description.setGeometry(QtCore.QRect(10, 220, 230, 90))
      
      buttonList = []
      #self.gridRadio = QtGui.QRadioButton('Define Input Grid',self.inputGroup)
      self.gridRadio = QtGui.QPushButton('Define Input Grid',self.inputGroup)
      self.gridRadio.setGeometry(QtCore.QRect(343, 30, 255, 25))
      self.gridRadio.setObjectName('gridRadio')
      self.gridRadio.setChecked(True)
      buttonList.append((self.gridRadio,"Grid"))
      
      self.addLocalSpeciesRadio = QtGui.QPushButton('Add Local Species Layers',self.inputGroup)
      self.addLocalSpeciesRadio.setGeometry(QtCore.QRect(343, 80, 255, 25))
      self.addLocalSpeciesRadio.setObjectName('speciesRadio')
      buttonList.append((self.addLocalSpeciesRadio,"Local"))
      
      self.treesLyrsRadio =  QtGui.QPushButton('Add Tree and Local Species',self.inputGroup)
      self.treesLyrsRadio.setToolTip("Begin an experiment with Newick phylo tree and supporting lyrs")
      self.treesLyrsRadio.setGeometry(QtCore.QRect(343,130,255,25))
      self.treesLyrsRadio.setObjectName("treeRadio")
      buttonList.append((self.treesLyrsRadio,"Tree"))
      #130,180,230,280
      
      self.addSDMLayerRadio = QtGui.QPushButton('Add LM species distribution model',self.inputGroup)
      self.addSDMLayerRadio.setToolTip('Serach for and add Species Distribution Model from Lifemapper')
      self.addSDMLayerRadio.setGeometry(QtCore.QRect(343, 180, 255, 25))
      self.addSDMLayerRadio.setObjectName("addlayer") 
      buttonList.append((self.addSDMLayerRadio,"SDM"))
      
      
      self.emptyRadio = QtGui.QPushButton('Empty Experiment',self.inputGroup)
      self.emptyRadio.setGeometry(QtCore.QRect(343, 230, 255, 25))
      self.emptyRadio.setObjectName('emptyRadio')
      buttonList.append((self.emptyRadio,"Empty"))
      
     
      
      self.listBucketsRadio = QtGui.QPushButton('List Grids',self.inputGroup)
      self.listBucketsRadio.setGeometry(QtCore.QRect(343, 280, 255, 25))
      self.listBucketsRadio.setObjectName('listBucketsRadio')
      self.listBucketsRadio.setEnabled(False)
      buttonList.append((self.listBucketsRadio,"ListBuckets"))
      
      self.listPALayersRadio = QtGui.QPushButton('List Layers',self.inputGroup)
      self.listPALayersRadio.setGeometry(QtCore.QRect(343, 330, 255, 25))
      self.listPALayersRadio.setObjectName('listPALayersRadio')
      self.listPALayersRadio.setEnabled(False)
      buttonList.append((self.listPALayersRadio,"ListLayers"))
      
      self.mapper = QSignalMapper(self)
      for button,code in buttonList:
         self.mapper.setMapping(button, code)
         button.clicked.connect(self.mapper.map)
      self.mapper.mapped['QString'].connect(self.postNewOpen)
      
      
      self.outputGroup = QtGui.QGroupBox(self)
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout_output.setObjectName("gridLayout_output")
      self.gridLayout.addWidget(self.outputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
       
      self.statuslabel = QtGui.QLabel(self.outputGroup)
      self.statuslabel.setObjectName('status')
      self.gridLayout_output.addWidget(self.statuslabel)
      self.statuslabel.setText(QtGui.QApplication.translate("self", 
         'Running Process', None, QtGui.QApplication.UnicodeUTF8))
      
      self.progressbar = QtGui.QProgressBar(self.outputGroup)
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.gridLayout_output.addWidget(self.progressbar)
       
      self.outputGroup.hide()
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      self.helpBut.clicked.connect(self.help)
      
      #self.acceptBut = QtGui.QPushButton("OK",self)
      #self.acceptBut.setDefault(True)
      self.rejectBut = QtGui.QPushButton("Close",self)
      #
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      #self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      #self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
      
     
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
      
      
      self.retranslateUi()
      
      self.rejectBut.clicked.connect(self.reject)
      #self.acceptBut.clicked.connect(self.accept)
       
      
          
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         " New Range and Diversity Experiment", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
