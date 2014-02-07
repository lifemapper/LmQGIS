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
      self.setMinimumSize(380,578)
      self.setMaximumSize(380,578)
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
       
      
       
      self.methodlabel = QtGui.QLabel(self.inputGroup)
      self.methodlabel.setGeometry(QtCore.QRect(10, 140, 193, 20))
      self.methodlabel.setObjectName("methodlabel")
      self.methodlabel.setText("Randomization Method")
      
   
      
      self.swapCheck = QtGui.QRadioButton('swap',self.inputGroup)
      self.swapCheck.setChecked(True)
      self.swapCheck.setGeometry(QtCore.QRect(10, 160, 213, 25))
      self.swapCheck.setObjectName("swapCheck")

      
      self.splotchCheck = QtGui.QRadioButton('dye dispersion',self.inputGroup)
      self.splotchCheck.setChecked(False)
      self.splotchCheck.setGeometry(QtCore.QRect(120, 160, 213, 25))
      self.splotchCheck.setObjectName("splotchCheck")
 
      
          
       
      self.iterationslabel = QtGui.QLabel(self.inputGroup)
      self.iterationslabel.setGeometry(QtCore.QRect(10, 205, 183, 20))
      self.iterationslabel.setObjectName("iterationslabel")
      self.iterationslabel.setText("Number of iterations")
      self.iterationsEdit = QtGui.QLineEdit(self.inputGroup)
      self.iterationsEdit.setGeometry(QtCore.QRect(10, 225, 223, 25))
      self.iterationsEdit.setObjectName("cellsize")
      
      

       
      self.outputGroup = QtGui.QGroupBox(self)
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout_output.setObjectName("gridLayout_input")
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
      #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Close)
      self.buttonBox.setObjectName("buttonBox")
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      self.helpBut.clicked.connect(self.help)
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
     
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
       
      self.retranslateUi()
      
       
      self.swapCheck.toggled.connect(lambda : self.iterationsEdit.setEnabled(True))
      self.splotchCheck.toggled.connect(lambda : self.iterationsEdit.setEnabled(False))
      
      self.rejectBut.clicked.connect(self.reject)
      self.acceptBut.clicked.connect(self.accept)      
      


     
           
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Generate Null Model", None, QtGui.QApplication.UnicodeUTF8))
      #self.checkBoxExisting.setText(QtGui.QApplication.translate("self", 
      #   "Choose Existing Process", None, QtGui.QApplication.UnicodeUTF8))
      #self.checkBoxURL.setText(QtGui.QApplication.translate("self", 
      #   "Enter Describe Process URL", None, QtGui.QApplication.UnicodeUTF8))
      #self.btnSubmitDescribe.setText(QtGui.QApplication.translate("self",
      #   "Submit Request", None, QtGui.QApplication.UnicodeUTF8))
   
   