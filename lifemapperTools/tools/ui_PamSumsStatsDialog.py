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
      self.setObjectName("PamSumsStatsDialog")
      # x,y
      self.resize(750, 630)
      self.setMinimumSize(500,450)
      self.setMaximumSize(1698,1548)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      self.gridLayout.setRowMinimumHeight(0,190)
      self.gridLayout.setRowMinimumHeight(1,45) 
      self.gridLayout.setRowMinimumHeight(2,710)   
      self.gridLayout.setRowMinimumHeight(3,50)
      
      self.tableLabel = QtGui.QLabel("")
      self.gridLayout.addWidget(self.tableLabel,1,0,1,1)
      
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.inputGroup.setTitle("Request Statistics")
      
      #left,top,right,bottom = self.inputGroup.getContentsMargins()
      #self.inputGroup.setContentsMargins(left, top-9, right, bottom-9)
      
      # then build a layout to set against the input group
      
      self.tableLayout = QtGui.QGridLayout()
      self.comboLayout = QtGui.QGridLayout()
      self.comboLayout.setRowMinimumHeight(0,30)
      self.comboLayout.setRowMinimumHeight(1,20)
      self.comboLayout.setRowMinimumHeight(2,20)
      self.comboLayout.setRowMinimumHeight(3,20)
      self.comboLayout.setRowMinimumHeight(4,40)
      self.comboLayout.setRowMinimumHeight(5,60)
      
      
      self.comboLayout.setColumnMinimumWidth(0,60)
      self.comboLayout.setColumnMinimumWidth(1,225)
      self.comboLayout.setColumnMinimumWidth(2,160)
      self.comboLayout.setColumnMinimumWidth(3,225)
      self.comboLayout.setColumnMinimumWidth(4,60)
      
      
      self.allRandomizedRadio = QtGui.QRadioButton("All pams")
      self.allRandomizedRadio.clicked.connect(self.checkPamSelected)
      
      self.swappedRadio = QtGui.QRadioButton("Swapped pams")
      self.swappedRadio.clicked.connect(self.checkPamSelected)
      
      self.splotchedRadio = QtGui.QRadioButton("Dye-dispersion pams")
      self.splotchedRadio.clicked.connect(self.checkPamSelected)
      
      self.sitesStatsRadio = QtGui.QRadioButton("Site based")
      self.sitesStatsRadio.toggled.connect(self.checkSitesStatsSelected)
      
      self.speciesStatsRadio = QtGui.QRadioButton("Species based")
      self.speciesStatsRadio.toggled.connect(self.checkSpeciesStatsSelected)
      
      self.betaStatsRadio = QtGui.QRadioButton("Diversity Beta's")
      self.betaStatsRadio.toggled.connect(self.checkBetaStatsSelected)
      
      
      
      self.statsRadioGroup = QtGui.QButtonGroup()
      self.statsRadioGroup.addButton(self.sitesStatsRadio)
      self.statsRadioGroup.addButton(self.speciesStatsRadio)
      self.statsRadioGroup.addButton(self.betaStatsRadio)
            
      self.pamRadioGroup = QtGui.QButtonGroup()
      self.pamRadioGroup.addButton(self.allRandomizedRadio)
      self.pamRadioGroup.addButton(self.swappedRadio)
      self.pamRadioGroup.addButton(self.splotchedRadio)
      
      # then add combo widgets and labels to inner layout
      self.pamsLabel = QtGui.QLabel("original and randomized pams")
      self.sitesLabel = QtGui.QLabel("Statistics")
      
      self.attachActiveLyr = QtGui.QCheckBox("Link Plot to Active Lyr")
      self.attachActiveLyr.setEnabled(False)
      #self.attachActiveLyr.clicked.connect(self.checkActiveLyrPlot)
      
      self.statsLblLink = QtGui.QHBoxLayout()
      self.statsLblLink.addWidget(self.sitesLabel)
      #self.statsLblLink.addWidget(self.attachActiveLyr)
      
      self.pamsumsCombo = QtGui.QComboBox()
      self.pamsumsCombo.currentIndexChanged.connect(self.checkPamSumNotAll)
      self.statsCombo = QtGui.QComboBox()
      
      
      self.comboLayout.addWidget(self.pamsLabel,        0,1,1,1)
      self.comboLayout.addLayout(self.statsLblLink,       0,3,1,1)
     
      
      self.comboLayout.addWidget(self.allRandomizedRadio,    1,1,1,1)
      self.comboLayout.addWidget(self.swappedRadio,          2,1,1,1)
      self.comboLayout.addWidget(self.splotchedRadio,        3,1,1,1)
      
      self.comboLayout.addWidget(self.sitesStatsRadio,         1,3,1,1)
      self.comboLayout.addWidget(self.speciesStatsRadio,       2,3,1,1)
      self.comboLayout.addWidget(self.betaStatsRadio,          3,3,1,1)
      
      self.HButtonBox = QtGui.QHBoxLayout()
            
      self.addtoTable = QtGui.QPushButton("View in table")
      self.addtoTable.clicked.connect(self.buildTable)
      self.addtoTable.setMaximumSize(104, 30)
      self.addtoTable.setMinimumSize(104, 30)
      
      self.scatterPlot = QtGui.QPushButton("Scatter Plot")
      self.scatterPlot.clicked.connect(self.buildScatterPlot)
      self.scatterPlot.setMaximumSize(104, 30)
      self.scatterPlot.setMinimumSize(104, 30)
      self.scatterPlot.setEnabled(False)
      
      self.exportStatsBut = QtGui.QPushButton("Export Table")
      self.exportStatsBut.clicked.connect(self.exportStats)
      self.exportStatsBut.setMaximumSize(104, 30)
      self.exportStatsBut.setMinimumSize(104, 30)
      self.exportStatsBut.setEnabled(False)
      
      self.spatiallyView = QtGui.QPushButton("Spatially View")
      self.spatiallyView.clicked.connect(self.buildSpatialView)
      self.spatiallyView.setMaximumSize(104, 30)
      self.spatiallyView.setMinimumSize(104, 30)
      self.spatiallyView.setEnabled(False)
      
      self.treeViewerBut = QtGui.QPushButton("Tree View")
      self.treeViewerBut.clicked.connect(self.openTree)
      self.treeViewerBut.setMaximumSize(104, 30)
      self.treeViewerBut.setMinimumSize(104, 30)
      self.treeViewerBut.setEnabled(False)
      
      
      self.comboLayout.addWidget(self.pamsumsCombo,      4,1,1,1,QtCore.Qt.AlignTop)
      self.comboLayout.addWidget(self.statsCombo,        4,3,1,1,QtCore.Qt.AlignTop)
      
      self.HButtonBox.addWidget(self.addtoTable)         #5,1,1,1)
      self.HButtonBox.addWidget(self.exportStatsBut)     #5,2,1,1)
      self.HButtonBox.addWidget(self.scatterPlot)        #5,3,1,1,QtCore.Qt.AlignCenter)
      self.HButtonBox.addWidget(self.spatiallyView)      #5,4,1,1,QtCore.Qt.AlignCenter)
      self.HButtonBox.addWidget(self.treeViewerBut)
      
      self.comboLayout.addLayout(self.HButtonBox, 5, 0, 1, 5)
      
      self.inputGroup.setLayout(self.comboLayout)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      self.helpBut.clicked.connect(self.help)
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      
      ############ spatial layout #####################
      #################################################
      self.outputGroup = QtGui.QGroupBox()
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      
      self.gridLayout_output = QtGui.QGridLayout()
      self.gridLayout_output.setObjectName("gridLayout_input")
      self.gridLayout_output.setColumnMinimumWidth(0,370) 
      self.gridLayout_output.setColumnMinimumWidth(1,45)  
      self.gridLayout_output.setColumnMinimumWidth(2,250)
      self.gridLayout_output.setRowMinimumHeight(0,450)
      self.gridLayout_output.setRowMinimumHeight(1,34)
      
      
      self.progressbar = QtGui.QProgressBar()
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.progressbar.hide()
      self.gridLayout_output.addWidget(self.progressbar,1,0,1,3)
      
      
      ################## left hand column ###############
      self.leftHandGrid = QtGui.QGridLayout()
      #self.leftHandGrid.setRowMinimumHeight(0,100)
      self.leftHandGrid.setRowMinimumHeight(0,20)
      self.leftHandGrid.setRowMinimumHeight(1,50)
      self.leftHandGrid.setRowMinimumHeight(2,50)
      
      self.leftHandGrid.setColumnMinimumWidth(0,210)
      self.leftHandGrid.setColumnMinimumWidth(1,150)
     
      #self.pamsCombo = QtGui.QComboBox()
      
      self.outlabel = QtGui.QLabel()
      self.outlabel.setObjectName("outlabel")   
      self.outlabel.setText("Output to Zipfile")
      self.outlabel.hide()
      
      
      self.outEdit = QtGui.QLineEdit()  
      self.outEdit.setObjectName("shapepath")
      self.outEdit.hide()
      #self.outEdit.setEnabled(False)
      
      self.fileButton = QtGui.QPushButton("Browse")
      self.fileButton.setMaximumSize(65,30)
      self.fileButton.setMinimumSize(65, 30)
      self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
      self.fileButton.hide()
      #self.fileButton.setEnabled(False)
      
      #self.downloadLabel  = QtGui.QLabel()
      #self.downloadLabel.setText('')
      #self.downloadLabel.setWordWrap(True)
      
      #self.leftHandGrid.addWidget(self.pamsCombo,    0,0,1,1)
      self.leftHandGrid.addWidget(self.outlabel,     0,0,1,1)#,QtCore.Qt.AlignBottom)
      self.leftHandGrid.addWidget(self.outEdit,      1,0,1,1)
      self.leftHandGrid.addWidget(self.fileButton,   1,1,1,1)
      #self.leftHandGrid.addWidget(self.downloadLabel,2,0,1,1)
      
      self.gridLayout_output.addLayout(self.leftHandGrid,0,0,1,1)
      #################### right hand column ########################
      
      #self.verticalLayout = QtGui.QVBoxLayout()
      self.verticalLayout = QtGui.QGridLayout()
      self.verticalLayout.setRowMinimumHeight(0,10)
      self.verticalLayout.setRowMinimumHeight(1,30)
      self.verticalLayout.setRowMinimumHeight(2,260)
      self.innerverticalLayout = QtGui.QVBoxLayout()
      
      
      self.classifyLabel = QtGui.QLabel()
      self.classifyLabel.setText('Field to classify layer on.')
      #self.classifyLabel.setWordWrap(True)
      self.classifyLabel.setMaximumHeight(78)
      
      self.speciesrichness = QtGui.QRadioButton('Species Richness')
      self.speciesrichness.setEnabled(True)
      self.speciesrichness.setChecked(True)
      
      self.meanproportionalrangesize = QtGui.QRadioButton('Mean Prop Range Size')
      self.meanproportionalrangesize.setEnabled(True)
      
      self.proportionalspeciesdiversity = QtGui.QRadioButton('Prop Species Diversity')
      self.proportionalspeciesdiversity.setEnabled(True)
      
      self.localityrangesize = QtGui.QRadioButton('Locality Range Size')
      self.localityrangesize.setEnabled(True)
      
      self.verticalLayout.addWidget(self.classifyLabel,1,0,1,1)#,QtCore.Qt.AlignTop)
      self.innerverticalLayout.addWidget(self.speciesrichness)
      self.innerverticalLayout.addWidget(self.meanproportionalrangesize)
      self.innerverticalLayout.addWidget(self.proportionalspeciesdiversity)
      self.innerverticalLayout.addWidget(self.localityrangesize)
      self.verticalLayout.addLayout(self.innerverticalLayout,2,0,1,1)#,QtCore.Qt.AlignTop)
      
      
      self.mapItBut = QtGui.QPushButton("Map it!")
      self.mapItBut.setMaximumWidth(60)
      self.mapItBut.clicked.connect(self.mapStats)
      self.gridLayout_output.addWidget(self.mapItBut,1,0,1,3,QtCore.Qt.AlignCenter)
      
      self.gridLayout_output.addLayout(self.verticalLayout,0,2,1,1)
      
      self.outputGroup.setLayout(self.gridLayout_output)
      
      self.fileButton.clicked.connect(self.showFileDialog)
      
      
      self.outputGroup.hide()   
      
      ######## end of spatial layout ####################
      
      # then add widget (input group to parent layout
      self.gridLayout.addWidget(self.inputGroup,  0,0,1,1)
      self.gridLayout.addLayout(self.tableLayout, 2,0,1,1)
      self.gridLayout.addWidget(self.outputGroup, 2,0,1,1)
      self.gridLayout.addWidget(self.buttonBox,   3,0,1,1)
      self.retranslateUi()
      
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
                            "PAM Statistics", None, QtGui.QApplication.UnicodeUTF8))      
      
      
      