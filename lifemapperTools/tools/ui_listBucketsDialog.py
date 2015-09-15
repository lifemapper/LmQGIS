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
import lifemapperTools.icons.icons
class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(778, 500)
      self.setMinimumSize(778,500)
      self.setMaximumSize(1688,1448)
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
      #self.gridLayout.addWidget(self.inputGroup, 0,0,4,4)
      self.gridLayout.setRowStretch(4,6)
      
      
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
         'Sending request..', None, QtGui.QApplication.UnicodeUTF8))
      
      self.progressbar = QtGui.QProgressBar();self.progressbar.setMinimum(0);self.progressbar.setMaximum(0)
      #self.progressWidget = QtGui.QWidget()
      #self.progressWidget.hide()
      #self.progressHzLayout = QtGui.QHBoxLayout(self.progressbar)
      self.progressbar.hide()
      self.gridLayout_input.addWidget( self.progressbar,4,0,1,4)
      #self.progressbar = QtGui.QProgressBar(self.outputGroup)
      #self.progressbar.setMinimum(0)
      #self.progressbar.setMaximum(100)
      #self.progressbar.setTextVisible(False)
      #self.progressbar.setObjectName('progressbar')
      #self.gridLayout_output.addWidget(self.progressbar)
      
      
           
       
      self.outputGroup.hide()
      
      icon = QtGui.QIcon(":/plugins/lifemapperTools/icons/refresh.png")
      self.refreshBut = QtGui.QPushButton(icon,"")
      self.refreshBut.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
      self.refreshBut.setMinimumSize(35,35)
      self.refreshBut.setMaximumSize(34,35)
      self.gridLayout_input.addWidget(self.refreshBut,1,1,1,1)
      
      self.gridLayout_input.setColumnMinimumWidth(0,57)
      self.gridLayout_input.setColumnMinimumWidth(1,57)
      self.gridLayout_input.setColumnMinimumWidth(2,458)
      self.gridLayout_input.setColumnMinimumWidth(3,115)
      
      self.gridLayout_input.setRowMinimumHeight(0,64)
      self.gridLayout_input.setRowMinimumHeight(1,235)
      self.gridLayout_input.setRowMinimumHeight(2,89)
      self.gridLayout_input.setRowMinimumHeight(3,89)
      self.gridLayout_input.setRowMinimumHeight(4,89)
      
      
      self.hideButtonsWidget = QtGui.QWidget()
      self.buttonHzLayout = QtGui.QHBoxLayout(self.hideButtonsWidget)
      #self.gridLayout_input.addLayout( self.buttonHzLayout,4,0,1,4)
      self.gridLayout_input.addWidget( self.hideButtonsWidget,4,0,1,4)
      
      self.getStatsBut = QtGui.QPushButton("Get Statistics",self)
      self.buttonHzLayout.addWidget(self.getStatsBut)
     
      self.intersectBut = QtGui.QPushButton("Intersect && Calculate",self)
      self.buttonHzLayout.addWidget(self.intersectBut)
     
      self.addBucketBut = QtGui.QPushButton("Add Grid",self)
      self.buttonHzLayout.addWidget(self.addBucketBut)
      
      self.randomizeBut = QtGui.QPushButton("Randomize PAM",self)
      self.buttonHzLayout.addWidget(self.randomizeBut)
      
      self.rejectBut = QtGui.QPushButton("Close",self)
      self.rejectBut.setEnabled(True)
       
      #self.splitBucketBut.setEnabled(True)
      self.getStatsBut.setEnabled(False)
      self.intersectBut.setEnabled(False) 
      self.addBucketBut.setEnabled(False)
      self.randomizeBut.setEnabled(False)
      
      
      self.refreshBut.setEnabled(True)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      #self.buttonBox.addButton(self.splitBucketBut, QtGui.QDialogButtonBox.ActionRole)
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      self.helpBut.setEnabled(True)
      
      
      self.helpBut.clicked.connect(self.help)
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut,    QtGui.QDialogButtonBox.RejectRole)
      
      
      self.buttonBox.setObjectName("buttonBox")
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
     
      
      self.retranslateUi()
      
      
      
      self.getStatsBut.clicked.connect(self.listPamSums)
      self.randomizeBut.clicked.connect(self.randomizeBucket)
      self.rejectBut.clicked.connect(self.reject)
      self.intersectBut.clicked.connect(self.intersectPAM)
      self.addBucketBut.clicked.connect(self.addBucket)
      self.refreshBut.clicked.connect(self.refresh)
      
      
      
      
             
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Experiment Grids", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
