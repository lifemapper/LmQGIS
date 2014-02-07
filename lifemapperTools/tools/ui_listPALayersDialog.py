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
      self.resize(818, 448)
      self.setMinimumSize(818,448)
      self.setMaximumSize(1818,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      
      self.inputGroup = QtGui.QGroupBox(self)
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      #self.gridLayout_input = QtGui.QGridLayout(self.inputGroup)
      #self.gridLayout_input.setObjectName("gridLayout_input")
      self.holderGroup = QtGui.QGroupBox(self)
      self.holderGroup.setObjectName('holderGroup')
      self.holderGroup.setMinimumSize(300, 180)
      self.loadTabelLabel = QtGui.QLabel("Loading Layers",self.holderGroup)
      self.loadTabelLabel.setGeometry(QtCore.QRect(100, 10, 140, 45))
   
      # for add widget, integers are fromrow,fromcolumn,rowspan,columnspan
      self.gridLayout.addWidget(self.holderGroup, 1,1,1,1)
      self.gridLayout.addWidget(self.inputGroup, 2,0,4,0)          
      
      self.setAllGroup = QtGui.QGroupBox(self)
      self.setAllGroup.setObjectName("setAllGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.setAllGroup.setStyle(self.style)
      
      
      self.setAllDirectionsLabel = QtGui.QLabel("Doubleclick on the column header to edit, enter value and then Set Column",
                                                self.setAllGroup)
      self.setAllDirectionsLabel.setWordWrap(True)
      self.setAllDirectionsLabel.setGeometry(QtCore.QRect(10, 30, 250,70))
      self.ColumnSet = QtGui.QLineEdit(self.setAllGroup)
      self.ColumnSet.setObjectName("ColumnSet")
      self.ColumnSet.setGeometry(QtCore.QRect(10, 110, 80, 25))
      self.ColumnSet.setEnabled(False)
      self.setAllColumnButton = QtGui.QPushButton(QtGui.QIcon("file.ico"), 
                                                  "Set Column", self.setAllGroup)
      self.setAllColumnButton.setObjectName('setAllColumnButton')
      self.setAllColumnButton.setGeometry(QtCore.QRect(99, 110, 80, 25))
      self.setAllColumnButton.setEnabled(False)
      self.currentsection = None
      #self.connect(self.setAllColumnButton, QtCore.SIGNAL("clicked()"), 
      #                                                   lambda : self.setColumn(self.currentsection))
      self.setAllColumnButton.clicked.connect(lambda : self.setColumn(self.currentsection))
      
      
      
      self.gridLayout.addWidget(self.setAllGroup, 2,0,4,0)
      
      
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

         
      self.intersectBut = QtGui.QPushButton("Intersect with Grids",self)
      self.rejectBut = QtGui.QPushButton("Close",self)
      self.setParamsBut = QtGui.QPushButton("Set Params",self)
      
      self.intersectBut.setEnabled(False)
      self.setParamsBut.setEnabled(False)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      
      
      self.helpBut.clicked.connect(self.help)
      
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.setParamsBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.intersectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
      
      
      self.buttonBox.setObjectName("buttonBox")
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
      #self.buttonBox = QtGui.QDialogButtonBox(self)    
      #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
      #
      #self.buttonBox.setObjectName("buttonBox-2")
      #self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
      
      
      self.retranslateUi()
          
      self.rejectBut.clicked.connect(self.reject)
      self.intersectBut.clicked.connect(self.intersectPAM)
      self.setParamsBut.clicked.connect(self.setParams)
      
   def setColumn(self, section):
      """
      @summary: sets a column value
      """ 
      if self.currentsection is not None:    
         value = str(self.ColumnSet.text())          
         for row, record in enumerate(self.table.tableView.model().data):
            self.table.tableView.model().setColumn(row, section, value)
      else:
         QMessageBox.warning(self,"Tip: ",
        "Double click on a column heading before setting value")
      
                
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Presence Absence Layers", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
