# -*- coding: utf-8 -*-
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
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.common.pluginconstants import RetrievEML
import operator
#from lifemapperTools.common.pluginconstants import KUNHM_GC_DESCRIBE_PROCESS_URL, \
#  STATUS_ACCEPTED, STATUS_FAILED, STATUS_SUCCEEDED, STATUS_STARTED, FIND_STATUS


class Ui_Dialog(object):
   
   def setupUi(self, data):
      self.setObjectName("Dialog")
      self.resize(628, 548)
      self.setMinimumSize(628,548)
      self.setMaximumSize(628,548)
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
      
      
      self.outputGroup = QtGui.QGroupBox(self)
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout_output.setObjectName("gridLayout_output")
      self.gridLayout.addWidget(self.outputGroup, 4,0,4,0)
      #self.gridLayout.setRowStretch(4,6)
       
      self.statuslabel = QtGui.QLabel(self.outputGroup)
      self.statuslabel.setGeometry(QtCore.QRect(254, 220, 113, 20))
      self.statuslabel.setObjectName('status')
      #self.statuslabel.setGeometry(QtCore.QRect(120, 400, 213, 24))
      
      self.statuslabel.setFont(QtGui.QFont('Verdana',pointSize=12))
      #self.gridLayout_output.addWidget(self.statuslabel)
      self.statuslabel.setText(QtGui.QApplication.translate("self", 
         'EML Published', None, QtGui.QApplication.UnicodeUTF8))
      
      #self.progressbar = QtGui.QProgressBar(self.outputGroup)
      #self.progressbar.setMinimum(0)
      #self.progressbar.setMaximum(100)
      #self.progressbar.setObjectName('progressbar')
      #self.gridLayout_output.addWidget(self.progressbar)
       
      self.outputGroup.hide()
      
      
      #self.addLayer = QtGui.QRadioButton('Add layers',self.inputGroup)
      #self.addLayer.setChecked(True)
      #self.addLayer.setGeometry(QtCore.QRect(10, 460, 213, 25))
      #self.addLayer.setObjectName("cellshape")
      #
      #
      #self.retrieveStats = QtGui.QRadioButton('Retrieve Stats',self.inputGroup)
      #self.retrieveStats.setChecked(False)
      #self.retrieveStats.setGeometry(QtCore.QRect(120, 460, 213, 25))
      #self.retrieveStats.setObjectName("cellshape")
      
      #self.table =  RADTable(data)
      #self.tableview = self.table.createTable()
       
      #self.gridLayout_input.addWidget(self.tableview) 
       
      
      fo = open(RetrievEML.EML_PATH,'r')
      eml = fo.read()
      self.edit = QtGui.QTextEdit('', self.inputGroup)
      self.edit.insertPlainText(eml)
      self.edit.setGeometry(QtCore.QRect(10, 10, 613, 425))
      
      
      self.publishBut = QtGui.QPushButton("Publish",self)
      self.rejectBut = QtGui.QPushButton("Close",self)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.publishBut, QtGui.QDialogButtonBox.ActionRole)
      
      
      self.buttonBox.setObjectName("buttonBox")
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
      #self.buttonBox = QtGui.QDialogButtonBox(self)    
      #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
      #
      #self.buttonBox.setObjectName("buttonBox-2")
      #self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
      
      
      self.retranslateUi()
       
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      QtCore.QObject.connect(self.publishBut, QtCore.SIGNAL("clicked()"), self.Okay) 
      
          
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Publish EML", None, QtGui.QApplication.UnicodeUTF8))
      
