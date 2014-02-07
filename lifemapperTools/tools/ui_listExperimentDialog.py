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
      self.resize(725, 548)
      self.setMinimumSize(725,548)
      self.setMaximumSize(1695,1548)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      
      self.inputGroup = QtGui.QGroupBox(self)
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.gridLayout_input = QtGui.QGridLayout(self.inputGroup)
      self.gridLayout_input.setObjectName("gridLayout_input")
      
      # put some spacers in gridLayout_input
      
      self.gridLayout_input.setColumnMinimumWidth(0,33)
      self.gridLayout_input.setColumnMinimumWidth(1,370)
      self.gridLayout_input.setColumnMinimumWidth(2,33)
      
      
      self.gridLayout_input.setRowMinimumHeight(0,60)
      self.gridLayout_input.setRowMinimumHeight(1,305)
      self.gridLayout_input.setRowMinimumHeight(2,20)
      self.gridLayout_input.setRowMinimumHeight(3,30)
      self.gridLayout_input.setRowMinimumHeight(4,30)
      ############ end spacers ################
      #         radio Layout container
      self.gridLayout_radio1 = QtGui.QHBoxLayout()
      self.gridLayout_radio2 = QtGui.QHBoxLayout()
      self.gridLayout_input.addLayout(self.gridLayout_radio1,3,0,1,3)
      self.gridLayout_input.addLayout(self.gridLayout_radio2,4,0,1,3)
      ###########################################
      
      
      self.gridLayout.addWidget(self.inputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
      
      
      
      
      ########### output group ####################
      
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
      
      
      ################## radio buttons ################
      
      self.openProj = QtGui.QPushButton('View Experiment')
      self.openProj.setToolTip("Open any layers loaded into the project")
      self.gridLayout_radio1.addWidget(self.openProj)
      self.openProj.setDefault(True)
      #QtCore.QObject.connect(self.openProj, QtCore.SIGNAL("clicked()"), lambda: self.accept('openProj'))
      self.openProj.clicked.connect(lambda:  self.accept('openProj'))
      
      self.viewBuckets = QtGui.QPushButton('Get Grids')
      self.viewBuckets.setToolTip('Get Grids')
      #self.viewBuckets.setChecked(True)   
      self.viewBuckets.setObjectName("viewBuckets")
      self.gridLayout_radio1.addWidget(self.viewBuckets)
      #QtCore.QObject.connect(self.viewBuckets, QtCore.SIGNAL("clicked()"), lambda: self.accept('buckets'))
      self.viewBuckets.clicked.connect(lambda: self.accept('buckets'))
      
      self.viewLayers = QtGui.QPushButton('Get PA layers')
      self.viewLayers.setToolTip("Get Presence Absence Layers")
      #self.viewLayers.setChecked(True)
      self.viewLayers.setObjectName("viewLayers")
      self.gridLayout_radio1.addWidget(self.viewLayers)
      #QtCore.QObject.connect(self.viewLayers, QtCore.SIGNAL("clicked()"), lambda: self.accept('viewLyrs'))
      self.viewLayers.clicked.connect(lambda: self.accept('viewLyrs'))
      
      self.addLayer = QtGui.QPushButton('Add PA layers')
      self.addLayer.setToolTip('Add Presence Absence Layers')
      #self.addLayer.setChecked(False)
      self.addLayer.setObjectName("addlayer")
      self.gridLayout_radio1.addWidget(self.addLayer)
      #QtCore.QObject.connect(self.addLayer, QtCore.SIGNAL("clicked()"), lambda: self.accept('addLyrs'))
      self.addLayer.clicked.connect(lambda: self.accept('addLyrs'))
      
      self.addSDMLayer = QtGui.QPushButton('Add LM modeled species layer')
      self.addSDMLayer.setToolTip('Add Lifemapper modeled species distribution')
      #self.addSDMLayer.setChecked(False)
      self.addSDMLayer.setObjectName("addSDMlayer")   
      self.gridLayout_radio1.addWidget(self.addSDMLayer)
      #QtCore.QObject.connect(self.addSDMLayer, QtCore.SIGNAL("clicked()"), lambda: self.accept('addSDM'))
      self.addSDMLayer.clicked.connect(lambda: self.accept('addSDM'))
      
      
      self.rejectBut = QtGui.QPushButton("Close",self)
      #
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      
      self.helpBut.clicked.connect(self.help)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
     
         
      
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
      
      self.rejectBut.clicked.connect(self.reject)
      
      
      self.retranslateUi()
     
      
          
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Range and Diversity Experiments", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
