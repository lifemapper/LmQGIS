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

#from lifemapperTools.common.pluginconstants import KUNHM_GC_DESCRIBE_PROCESS_URL, \
#  STATUS_ACCEPTED, STATUS_FAILED, STATUS_SUCCEEDED, STATUS_STARTED, FIND_STATUS


class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(478, 448)
      self.setMinimumSize(478,448)
      self.setMaximumSize(478,448)
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
         
       
      self.usernamelabel = QtGui.QLabel(self.inputGroup)
      self.usernamelabel.setGeometry(QtCore.QRect(10, 105, 113, 20))
      self.usernamelabel.setObjectName("usernamelabel")
      self.usernamelabel.setText("User Name")
      self.usernameEdit = QtGui.QLineEdit(self.inputGroup)
      self.usernameEdit.setGeometry(QtCore.QRect(10, 125, 213, 25))
      self.usernameEdit.setObjectName("usernameEdit")
       
      self.passlabel = QtGui.QLabel(self.inputGroup)
      self.passlabel.setGeometry(QtCore.QRect(10, 170, 213, 20))
      self.passlabel.setObjectName("passlabel")
      self.passlabel.setText("Password")
      self.passEdit = QtGui.QLineEdit(self.inputGroup)
      self.passEdit.setEchoMode(QtGui.QLineEdit.Password)
      self.passEdit.setGeometry(QtCore.QRect(10, 190, 213, 25))
      self.passEdit.setObjectName("passEdit")
      
      
      self.emaillabel = QtGui.QLabel(self.inputGroup)
      self.emaillabel.setWordWrap(True)
      self.emaillabel.setGeometry(QtCore.QRect(10, 230, 243, 40))
      self.emaillabel.setObjectName("emaillabel")
      self.emaillabel.setText("Email (optional, job completion notify)")
      self.emailEdit = QtGui.QLineEdit(self.inputGroup)
      self.emailEdit.setGeometry(QtCore.QRect(10, 270, 213, 25))
      self.emailEdit.setObjectName("emailEdit")
      
      #self.workspaceBut = QtGui.QPushButton("WS",self)
      #self.workspaceBut.setGeometry(QtCore.QRect(20, 320, 35, 35))
      #QtCore.QObject.connect(self.workspaceBut, QtCore.SIGNAL("clicked()"), self.openDirectoryDialog)
    
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      
      self.acceptBut = QtGui.QPushButton("OK",self)
      self.acceptBut.setDefault(True)
      self.buttonBox = QtGui.QDialogButtonBox(self)
      
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut,QtGui.QDialogButtonBox.ActionRole)
     
      
      self.buttonBox.setObjectName("buttonBox")
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
           
   
      self.retranslateUi()
      
      QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept)
      
      
     
      
           
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Lifemapper Sign In", None, QtGui.QApplication.UnicodeUTF8))
      #self.checkBoxExisting.setText(QtGui.QApplication.translate("self", 
      #   "Choose Existing Process", None, QtGui.QApplication.UnicodeUTF8))
      #self.checkBoxURL.setText(QtGui.QApplication.translate("self", 
      #   "Enter Describe Process URL", None, QtGui.QApplication.UnicodeUTF8))
      #self.btnSubmitDescribe.setText(QtGui.QApplication.translate("self",
      #   "Submit Request", None, QtGui.QApplication.UnicodeUTF8))
   
   