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


class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(380, 448)
      self.setMinimumSize(380,548)
      self.setMaximumSize(380,548)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
 
       
       
       
      # This is my controls Group that gets populated with input controls 
      # when the model is updated
      self.inputGroup = QtGui.QGroupBox(self)
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.gridLayout_input = QtGui.QGridLayout(self.inputGroup)
      self.gridLayout_input.setObjectName("gridLayout_input")
      self.gridLayout.addWidget(self.inputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
      
 
      
      
      # self.northEdit.setEnabled(True)                
      self.userIdlabel = QtGui.QLabel(self.inputGroup)
      self.userIdlabel.setGeometry(QtCore.QRect(10, 20, 113, 20))
      self.userIdlabel.setObjectName("userIdlabel")
      self.userIdlabel.setText("User Id")
      self.userIdEdit = QtGui.QLineEdit(self.inputGroup)
      self.userIdEdit.setGeometry(QtCore.QRect(10, 40, 213, 25))
      self.userIdEdit.setObjectName("userEdit")
       
      self.emaillabel = QtGui.QLabel(self.inputGroup)
      self.emaillabel.setGeometry(QtCore.QRect(10, 65, 213, 20))
      self.emaillabel.setObjectName("emaillabel")
      self.emaillabel.setText("Email")
      self.emailEdit = QtGui.QLineEdit(self.inputGroup)
      self.emailEdit.setGeometry(QtCore.QRect(10, 85, 213, 25))
      self.emailEdit.setObjectName("emailEdit")
      
      self.passwordlabel = QtGui.QLabel(self.inputGroup)
      self.passwordlabel.setGeometry(QtCore.QRect(10, 110, 213, 20))
      self.passwordlabel.setObjectName("passwordlabel")
      self.passwordlabel.setText("Password")
      self.passwordEdit = QtGui.QLineEdit(self.inputGroup)
      self.passwordEdit.setEchoMode(2)
      self.passwordEdit.setGeometry(QtCore.QRect(10, 130, 213, 25))
      self.passwordEdit.setObjectName("passwordEdit")
      
      self.firstnamelabel = QtGui.QLabel(self.inputGroup)
      self.firstnamelabel.setGeometry(QtCore.QRect(10, 155, 213, 20))
      self.firstnamelabel.setObjectName("firstnamelabel")
      self.firstnamelabel.setText("First Name")
      self.firstnameEdit = QtGui.QLineEdit(self.inputGroup)
      self.firstnameEdit.setGeometry(QtCore.QRect(10, 175, 213, 25))
      self.firstnameEdit.setObjectName("firstnameEdit")
      
      self.lastnamelabel = QtGui.QLabel(self.inputGroup)
      self.lastnamelabel.setGeometry(QtCore.QRect(10, 200, 213, 20))
      self.lastnamelabel.setObjectName("lastnamelabel")
      self.lastnamelabel.setText("Last Name")
      self.lastnameEdit = QtGui.QLineEdit(self.inputGroup)
      self.lastnameEdit.setGeometry(QtCore.QRect(10, 225, 213, 25))
      self.lastnameEdit.setObjectName("lastnameEdit")
      
      self.institutionlabel = QtGui.QLabel(self.inputGroup)
      self.institutionlabel.setGeometry(QtCore.QRect(10, 250, 213, 20))
      self.institutionlabel.setObjectName("institutionlabel")
      self.institutionlabel.setText("Institution")
      self.institutionEdit = QtGui.QLineEdit(self.inputGroup)
      self.institutionEdit.setGeometry(QtCore.QRect(10, 275, 213, 25))
      self.institutionEdit.setObjectName("institutionEdit")
      
      self.address1label = QtGui.QLabel(self.inputGroup)
      self.address1label.setGeometry(QtCore.QRect(10, 300, 213, 20))
      self.address1label.setObjectName("address1label")
      self.address1label.setText("Address 1")
      self.address1Edit = QtGui.QLineEdit(self.inputGroup)
      self.address1Edit.setGeometry(QtCore.QRect(10, 320, 213, 25))
      self.address1Edit.setObjectName("address1Edit")
      
      self.address2label = QtGui.QLabel(self.inputGroup)
      self.address2label.setGeometry(QtCore.QRect(10, 345, 213, 20))
      self.address2label.setObjectName("address2label")
      self.address2label.setText("Address 2")
      self.address2Edit = QtGui.QLineEdit(self.inputGroup)
      self.address2Edit.setGeometry(QtCore.QRect(10, 365, 213, 25))
      self.address2Edit.setObjectName("address2Edit")
      
      self.address3label = QtGui.QLabel(self.inputGroup)
      self.address3label.setGeometry(QtCore.QRect(10, 390, 213, 20))
      self.address3label.setObjectName("address3label")
      self.address3label.setText("Address 3")
      self.address3Edit = QtGui.QLineEdit(self.inputGroup)
      self.address3Edit.setGeometry(QtCore.QRect(10, 410, 213, 25))
      self.address3Edit.setObjectName("address3Edit")
      
      self.phonelabel = QtGui.QLabel(self.inputGroup)
      self.phonelabel.setGeometry(QtCore.QRect(10, 435, 213, 20))
      self.phonelabel.setObjectName("phonelabel")
      self.phonelabel.setText("Phone")
      self.phoneEdit = QtGui.QLineEdit(self.inputGroup)
      self.phoneEdit.setGeometry(QtCore.QRect(10, 455, 213, 25))
      self.phoneEdit.setObjectName("phoneEdit")
      
      # output group
       
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
       
      self.acceptBut = QtGui.QPushButton("OK",self)
      self.rejectBut = QtGui.QPushButton("Close",self)

      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
      self.buttonBox.setObjectName("buttonBox-2")
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
      
      
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
           
   
      self.retranslateUi()
       
  
      self.rejectBut.clicked.connect(self.reject)
      self.acceptBut.clicked.connect(self.accept)
     

   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "New user", None, QtGui.QApplication.UnicodeUTF8))
      
   