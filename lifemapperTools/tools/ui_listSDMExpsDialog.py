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
      self.setMinimumSize(418,248)
      self.setMaximumSize(1818,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      self.gridLayout.setColumnMinimumWidth(0,500)
      self.gridLayout.setColumnMinimumWidth(1,150)
      
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      
      self.tableGrid = QtGui.QGridLayout()
      self.tableGrid.setRowMinimumHeight(0,20)
      self.tableGrid.setRowMinimumHeight(1,130)
      self.tableGrid.setRowMinimumHeight(2,50)
      self.tableGrid.setColumnMinimumWidth(0,20)
      self.tableGrid.setColumnMinimumWidth(1,500)
      self.tableGrid.setColumnMinimumWidth(2,20)
      
      ########### view OccSet Metadata
      self.viewOccSetGroup = QtGui.QGroupBox()
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.viewOccSetGroup.setStyle(self.style)
      
      self.viewOccInnerGrid = QtGui.QGridLayout()
      self.viewOccInnerGrid.setColumnMinimumWidth(0,150)
      self.viewOccInnerGrid.setColumnMinimumWidth(1,500)
      self.viewOccInnerGrid.setColumnMinimumWidth(2,150)
      
 
      self.occMetaCol = QtGui.QVBoxLayout()
      
      #self.viewOccInnerGrid.addLayout(self.occLabelCol,0,1,2,1)
      #self.viewOccInnerGrid.addLayout(self.occValueCol,0,2,2,1)
      self.viewOccInnerGrid.addLayout(self.occMetaCol,0,1,1,1,alignment=Qt.AlignHCenter)
      self.viewOccSetGroup.setLayout(self.viewOccInnerGrid)
      
      
      self.viewOccSetGroup.hide()
      
      ########### view Exp Grid ###############
      
      self.viewExpGroup = QtGui.QGroupBox()
      self.viewExpGroup.setObjectName("viewExpGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.viewExpGroup.setStyle(self.style)
      
      self.viewExpGrid = QtGui.QGridLayout()
      self.viewExpGrid.setRowMinimumHeight(0,17)
      self.viewExpGrid.setRowMinimumHeight(1,17)
      self.viewExpGrid.setRowMinimumHeight(2,17)
      self.viewExpGrid.setRowMinimumHeight(3,17)
      self.viewExpGrid.setRowMinimumHeight(4,17)
      self.viewExpGrid.setRowMinimumHeight(5,90)
      self.viewExpGrid.setRowMinimumHeight(6,17)
      
      self.viewExpGrid.setColumnMinimumWidth(0,260)
      self.viewExpGrid.setColumnMinimumWidth(1,80)
      self.viewExpGrid.setColumnMinimumWidth(2,100)
      self.viewExpGrid.setColumnMinimumWidth(3,260)
      
      self.displayNameLabel = QtGui.QLabel("Display Name:")
      self.displayName      = QtGui.QLabel('')
      self.occSetLabel      = QtGui.QLabel('Species Points:')
      self.occSetLink       = QtGui.QLabel('<a href="www.fake.com">Details</a>')
      self.statusLabel      = QtGui.QLabel('Status:')
      self.status           = QtGui.QLabel('')
      self.algoCodeLabel    = QtGui.QLabel('Algorithm Code:')
      self.algoCode         = QtGui.QLabel('')
      self.projectionsLabel = QtGui.QLabel('Projections:')
      self.projectionsLink      = QtGui.QLabel('<a href="www.fake.com">Details</a>')
      self.backLink         = QtGui.QLabel('<a href="www.fake.com">Back to experiments</a>')
      
     
      self.backLink.linkActivated.connect(self.switchtoExpTableFromDetails)
      self.projectionsLink.linkActivated.connect(self.showProjTable)
      self.occSetLink.linkActivated.connect(self.processOccSet)
      
      self.viewExpGrid.addWidget(self.displayNameLabel,0,1,1,1)
      self.viewExpGrid.addWidget(self.displayName,     0,2,1,2)
      self.viewExpGrid.addWidget(self.occSetLabel,     1,1,1,1)
      self.viewExpGrid.addWidget(self.occSetLink,      1,2,1,1)
      self.viewExpGrid.addWidget(self.statusLabel,     2,1,1,1)
      self.viewExpGrid.addWidget(self.status,          2,2,1,1)
      self.viewExpGrid.addWidget(self.algoCodeLabel,   3,1,1,1)
      self.viewExpGrid.addWidget(self.algoCode,        3,2,1,1)
      self.viewExpGrid.addWidget(self.projectionsLabel,4,1,1,1)
      self.viewExpGrid.addWidget(self.projectionsLink,     4,2,1,1)
      self.viewExpGrid.addWidget(self.backLink,        6,1,1,2)
      
      self.viewExpGroup.setLayout(self.viewExpGrid)
      self.viewExpGroup.hide()
      #######################################################################
      
         
      #self.acceptBut = QtGui.QPushButton("OK")
      self.rejectBut = QtGui.QPushButton("Close")
      self.rejectBut.setAutoDefault(False)
      
      self.buttonBox = QtGui.QDialogButtonBox()
      self.helpBut = QtGui.QPushButton("?")
      self.helpBut.setAutoDefault(False)
      self.helpBut.setMaximumSize(30, 30)
      
     
      self.helpBut.clicked.connect(self.help)
      self.rejectBut.clicked.connect(self.reject)
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      
      self.gridLayout.addLayout(self.tableGrid,      0,0,1,2)
      self.gridLayout.addWidget(self.viewExpGroup,   0,0,1,2)
      self.gridLayout.addWidget(self.viewOccSetGroup,0,0,1,2)
      self.gridLayout.addWidget(self.buttonBox,      8,1,1,1)
       
     
      
      self.retranslateUi()
       
      
      #QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept) 
      

                
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Species Distribution Modeling Experiments", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
