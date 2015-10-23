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
from lifemapperTools.icons import icons
import os


#..............................................................................

class Ui_Dialog(object):
   
   def showMaskCombos(self,checked):
      if checked:
         self.hideyWidget.show()
      else:
         self.hideyWidget.hide()
   
   def setupUi(self, experimentname=''):
      self.setObjectName("Dialog")
      self.resize(915, 676)
      #x,y
      
      #############style############
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      ##############################
      
      self.setMinimumSize(700,600)
      self.setMaximumSize(1988,1600)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
     
      
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout.addLayout(self.gridLayout_input,0,0,1,1)
      self.gridLayout_input.setObjectName("gridLayout_input")
      
      self.gridLayout_input.setRowMinimumHeight(0,323)
      self.gridLayout_input.setRowMinimumHeight(1,100)
      
      
      
      # this layout goes inside of new inputGroup
      self.points_envLayout = QtGui.QGridLayout()
      self.points_envLayout.setRowMinimumHeight(0,40)
      self.points_envLayout.setRowMinimumHeight(1,100)
      self.points_envLayout.setRowMinimumHeight(2,10)
      self.points_envLayout.setRowMinimumHeight(3,290)
      
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setStyle(self.style)
      self.inputGroup.setTitle("Inputs")
      
      self.inputGroup.setLayout(self.points_envLayout)
      
      
      ##########Title and Desc input group ###################
      
      self.titleDescGroup = QtGui.QGroupBox()
      self.titleDescGroup.setMaximumHeight(100)
      self.titleDescGroup.setStyle(self.style)
      self.titleDescGroup.setTitle("Name and Description")
      
      self.titleDescLayout = QtGui.QGridLayout()
      self.titleDescLayout.setColumnMinimumWidth(0,120)
      self.titleDescLayout.setColumnMinimumWidth(1,300)
      self.titleDescLayout.setRowMinimumHeight(0,28)
      self.titleDescLayout.setRowMinimumHeight(1,48)
      
      self.expLabel = QtGui.QLabel("Experiment Name")
      self.expName = QtGui.QLineEdit()
      self.expName.setMaximumWidth(300)
      self.expName.setMinimumWidth(300)
      self.expDescLabel = QtGui.QLabel("Experiment Description")
      self.expDesc = QtGui.QLineEdit()
      
      self.titleDescLayout.addWidget(self.expLabel,    0,0,1,1)
      self.titleDescLayout.addWidget(self.expDescLabel,0,1,1,1)
      self.titleDescLayout.addWidget(self.expName,     1,0,1,1)
      self.titleDescLayout.addWidget(self.expDesc,     1,1,1,1)
      
      self.titleDescGroup.setLayout(self.titleDescLayout)
      
      self.points_envLayout.addWidget(self.titleDescGroup,0,0,1,1)
      
      ######################################################3#
      
      self.occGroup = QtGui.QGroupBox()
      
      self.occGroup.setStyle(self.style)
      self.occGroup.setTitle("Species Points")
      left,top,right,bottom = self.occGroup.getContentsMargins()
      self.occGroup.setContentsMargins(left, top-20, right, bottom)
      
     
      
      
      self.occSetLayout = QtGui.QGridLayout()
      
      
      self.occSetLayout.setColumnMinimumWidth(0,180)
      self.occSetLayout.setColumnMinimumWidth(1,33)
      self.occSetLayout.setColumnMinimumWidth(2,320)
      self.occSetLayout.setColumnMinimumWidth(3,30)
      self.occSetLayout.setColumnMinimumWidth(4,33)
      self.occSetLayout.setColumnMinimumWidth(5,200)
      self.occSetLayout.setColumnMinimumWidth(6,40)
      
      
      self.occSetLayout.setRowMinimumHeight(0,18)
      self.occSetLayout.setRowMinimumHeight(1,30)
      #self.occSetLayout.setRowMinimumHeight(2,37)
      
     
      self.upLoadLabel = QtGui.QLabel("Upload your own species points")
      self.upLoadLabel.setMaximumHeight(18)
      
      self.uploadOccBut = QtGui.QPushButton("Upload")
      self.uploadOccBut.setAutoDefault(False)
      self.uploadOccBut.clicked.connect(self.openOccUpload)
      self.uploadOccBut.setMaximumWidth(180)
     
      
      self.occSearchLabel = QtGui.QLabel("Search Lifemapper species points") 
      self.occSearchLabel.setMaximumHeight(18)
      
      self.occSetCombo = QComboBox() #keyedQComboBox()     
      self.occSetCombo.setMaximumWidth(320)
      self.occSetCombo.setEditable(True)
      self.occSetCombo.setAutoCompletion(True)
      self.occSetCombo.textChanged.connect(self.onTextChange)
      #self.occSetCombo.currentIndexChanged.connect(self.testIdx)
      

      pointIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/addPointLayer.png")
      self.download = QtGui.QPushButton(pointIcon,"")
      self.download.setMaximumSize(25, 25)
      self.download.setToolTip("optional: Load Data from search") 
      self.download.setEnabled(False)
      self.download.setAutoDefault(False)

      self.download.clicked.connect(self.downloadLayer)
      
      self.occIdLabel = QtGui.QLabel("Lifemapper species point set id")
      self.occIdLabel.setMaximumHeight(18)
      self.occIdText = QtGui.QLineEdit()
      #self.occIdText.editingFinished.connect(self.getUserOccSet)
      self.occIdText.setMaximumWidth(200)
      self.occIdText.setMinimumWidth(160)
      
      stackIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/layerStack.png")
      self.getScenBut = QtGui.QPushButton(stackIcon,"")
      self.getScenBut.setToolTip("Get environmental layer sets for this ID")
      self.getScenBut.setMaximumSize(26, 26)
      self.getScenBut.setAutoDefault(False)
      
      self.getScenBut.clicked.connect(self.getScenariosMasks)
      
      
      self.orLabel = QtGui.QLabel("or")
      self.orLabel.setMaximumWidth(30)
      self.orLabel.setMinimumWidth(30)
      self.orLabel2 = QtGui.QLabel("or")
      self.orLabel2.setMaximumWidth(30)
      self.orLabel2.setMinimumWidth(30)
      
      
      
      
      self.occSetLayout.addWidget(self.upLoadLabel,   0,0,1,1,Qt.AlignCenter)
      self.occSetLayout.addWidget(self.occSearchLabel,0,2,1,1,Qt.AlignCenter)
      self.occSetLayout.addWidget(self.occIdLabel,    0,5,1,1,Qt.AlignCenter)
      
      self.occSetLayout.addWidget(self.uploadOccBut,  1,0,1,1,Qt.AlignTop)
      self.occSetLayout.addWidget(self.orLabel,       1,1,1,1,Qt.AlignTop)
      self.occSetLayout.addWidget(self.occSetCombo,   1,2,1,1,Qt.AlignTop) 
      self.occSetLayout.addWidget(self.download,      1,3,1,1,Qt.AlignTop)         
      self.occSetLayout.addWidget(self.orLabel2,      1,4,1,1,Qt.AlignTop) 
      self.occSetLayout.addWidget(self.occIdText,     1,5,1,1,Qt.AlignTop)
      self.occSetLayout.addWidget(self.getScenBut,    1,6,1,1,Qt.AlignTop)     
      
     
      self.occGroup.setLayout(self.occSetLayout)
      
      self.points_envLayout.addWidget(self.occGroup,1,0,1,1)
      
      ############ Mask optional group ##############     
      
      self.maskGroup = QGroupBox()
      self.maskGroup.setStyle(self.style)
      self.maskGroup.setTitle('Mask (optional)')
      self.maskGroup.setCheckable(True)
      self.maskGroup.setChecked(False)
      self.maskGroup.setFocusPolicy(Qt.NoFocus)
      self.maskGroup.setFlat(True)
      self.maskGroup.setEnabled(False)
      self.maskGroup.toggled.connect(self.showMaskCombos)
      
      ly = QtGui.QGridLayout()
      ly.setMargin(0)
      
      self.hideyWidget = QWidget()
      self.hideyWidget.setMinimumHeight(100)
      self.hideyWidget.hide()
      ly.addWidget(self.hideyWidget)
      
      self.maskLayout = QtGui.QVBoxLayout(self.hideyWidget)
      
      
      
      horiz1 = QtGui.QHBoxLayout()
      horiz1.addWidget(QLabel("Use Existing Model Mask"))
      horiz1.addWidget(QLabel("Use Existing Projection Mask"))
      self.maskLayout.addLayout(horiz1)
      
      
            
      horiz2 = QtGui.QHBoxLayout()
      
      self.modelMaskCombo = QComboBox()
      self.projectionMaskCombo = QComboBox()
      horiz2.addWidget(self.modelMaskCombo)
      horiz2.addWidget(self.projectionMaskCombo)
      self.maskLayout.addLayout(horiz2)
      
      horiz3 = QtGui.QHBoxLayout()
      self.newMaskButton = QtGui.QPushButton("Upload New Mask")
      self.newMaskButton.clicked.connect(self.uploadNewMask)
      self.newMaskButton.setFocusPolicy(Qt.NoFocus)
      self.newMaskButton.setMaximumHeight(30)
      self.newMaskButton.setMaximumWidth(136)
      
      horiz3.addWidget(self.newMaskButton,alignment=Qt.AlignLeft)
      self.maskLayout.addLayout(horiz3)
      
      self.maskGroup.setLayout(ly)
      self.points_envLayout.addWidget(self.maskGroup,2,0,1,1)
      
      ############ 3rd input group SCENARIOS #######################################
      
      self.scenarioGroup = QtGui.QGroupBox()
      self.scenarioGroup.setStyle(self.style)
      self.scenarioGroup.setTitle("Environmental Layer Set")
      self.scenarioGroup.setMaximumHeight(187)
      
      
      self.scenLayout = QtGui.QGridLayout()
      self.scenLayout.setRowMinimumHeight(0,3)
      self.scenLayout.setRowMinimumHeight(1,20)
      self.scenLayout.setRowMinimumHeight(2,190)
      #self.scenLayout.setRowMinimumHeight(3,10)
      
      self.scenLayout.setColumnMinimumWidth(0,10)
      self.scenLayout.setColumnMinimumWidth(1,230)
      self.scenLayout.setColumnMinimumWidth(2,10)
      self.scenLayout.setColumnMinimumWidth(3,230)
      self.scenLayout.setColumnMinimumWidth(4,10)
      
      self.modelScenLabel = QtGui.QLabel("Layer sets for modeling (populate by clicking upper right layer icon)")
      #self.modelScenLabel.setWordWrap(True)
      self.modelScenCombo = QComboBox()
      self.modelScenCombo.currentIndexChanged.connect(self.populateProjScenCombo)
      self.modelScenCombo.setEnabled(False)
      self.projScenLabel = QtGui.QLabel("Layer sets for mapping")
      
      self.projectionScenListView = QtGui.QListView()
      #self.projectionScenListView.setMinimumHeight(80)
      self.projectionScenListView.setSelectionMode(QAbstractItemView.MultiSelection)
      self.projectionScenListView.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.projectionScenListView.clicked.connect(self.matchNew)
      self.projectionScenListView.setEnabled(False)
      
      self.scenLayout.addWidget(self.modelScenLabel,        1,1,1,1)
      self.scenLayout.addWidget(self.modelScenCombo,        2,1,1,1,Qt.AlignTop)
      self.scenLayout.addWidget(self.projScenLabel,         1,3,1,1)
      self.scenLayout.addWidget(self.projectionScenListView,2,3,1,1)#,Qt.AlignTop)
      
      self.scenarioGroup.setLayout(self.scenLayout)
      
      self.points_envLayout.addWidget(self.scenarioGroup,3,0,1,1)
      
      # second input group ALGORITHMS ##########################################
      self.algoGroup = QtGui.QGroupBox() 
      #self.algoGroup.setMinimumHeight(178)
      self.algoGroup.setStyle(self.style)
      self.algoGroup.setTitle("Algorithm")
      
      
      self.algoGrid = QtGui.QGridLayout()
      self.algoGrid.setColumnMinimumWidth(0,372)
      self.algoGrid.setColumnMinimumWidth(1,76)
      self.algoGrid.setColumnMinimumWidth(2,374)
      #self.algoGrid.setColumnMinimumWidth(2,90)
      self.algoGrid.setRowMinimumHeight(0,24)
      self.algoGrid.setRowMinimumHeight(1,20)
      self.algoGrid.setRowMinimumHeight(2,20)
      #self.algoGrid.setRowMinimumHeight(3,24)
      
      self.algorithmLabel = QtGui.QLabel("Choose Algorithm")
      self.algCodeCombo = QComboBox()
      self.algCodeCombo.currentIndexChanged.connect(self.populateAlgoDesc)
      self.algCodeCombo.setMaximumWidth(400) 
      
      self.advancedBut = QtGui.QPushButton("Advanced")
      self.advancedBut.setMaximumWidth(90)
      self.advancedBut.setAutoDefault(False)
      self.advancedBut.setEnabled(False)
      
      self.algoDesc = QtGui.QTextEdit()
      p = self.algoDesc.palette()
      color = self.palette().color(QPalette.Background)
      p.setColor(QPalette.Base, QColor(color.red(), color.green(), color.blue()))
      self.algoDesc.setPalette(p);
      self.algoDesc.setReadOnly(True)
      
      self.algoGrid.addWidget(self.algorithmLabel,0,0,1,1,Qt.AlignLeft)
      self.algoGrid.addWidget(self.algCodeCombo,  1,0,1,1,Qt.AlignLeft)
      
      self.algoGrid.addWidget(self.advancedBut,   1,1,1,1,Qt.AlignLeft)
      self.algoGrid.addWidget(self.algoDesc,      0,2,3,1)
      
      self.algoGroup.setLayout(self.algoGrid)
      ###########################################################
     
      
      
     
      self.gridLayout_input.addWidget(self.inputGroup,     0,0,1,1)
      self.gridLayout_input.addWidget(self.algoGroup,      1,0,1,1)
      
     
     
      self.outputGroup = QtGui.QGroupBox(self)
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout_output.setObjectName("gridLayout_input")
      self.gridLayout.addWidget(self.outputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
       
      self.statuslabel = QtGui.QLabel(self.outputGroup)
      self.statuslabel.setText("Working...")
      self.gridLayout_output.addWidget(self.statuslabel)
      
      self.progressbar = QtGui.QProgressBar(self.outputGroup)
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(0)
      self.progressbar.setObjectName('progressbar')
      self.gridLayout_output.addWidget(self.progressbar)
       
      self.outputGroup.hide()
      ########################################################################## 
      
       
     
      self.rejectBut = QtGui.QPushButton("Close",self)
      self.rejectBut.setAutoDefault(False)  
      self.rejectBut.clicked.connect(self.reject)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setAutoDefault(False)
      self.helpBut.setMaximumSize(30, 30)
      self.helpBut.clicked.connect(self.help)
      
      self.acceptBut = QtGui.QPushButton("Submit Exp", self)
      self.acceptBut.setAutoDefault(False)
      self.acceptBut.clicked.connect(self.accept)
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)   
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole) 
     
      
      # for add widget, integers are fromrow,fromcolumn,rowspan,columnspan
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
         
      self.retranslateUi()
      
      
      
   
      
      
      

              
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Perform a Lifemapper SDM Experiment", None, QtGui.QApplication.UnicodeUTF8))
      
   
   