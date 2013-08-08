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
from lifemapperTools.tools.radTable import *
import os


class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(448, 448)
      self.setMinimumSize(788,448)
      self.setMaximumSize(788,448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       

     
      ##########################################################################
      #    table 
      ########################################################################## 
      self.data = [['','','','','']]
      self.table =  RADTable(self.data)
      self.uploadButton = QtGui.QPushButton()
      #addAncLayer signature(self, expId, lyrId, attrValue=None, calculateMethod=None, 
      #                      minPercent=None): 
      header = ['Layer Name', 'filepath', 'Value Attribute', 
                'Calculate Method', 'Minimum Percent']
      self.tableview = self.table.createTable(header,editsIndexList=[0,2,3,4,5],
                                              hiddencolumns=[1],comboIndices=[3],
                                              fields=['weightedMean','largestClass'])
      self.inputGroup = QtGui.QGroupBox(self)
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      #self.gridLayout_input = QtGui.QGridLayout(self.inputGroup)
      #self.gridLayout_input.setObjectName("gridLayout_input")
      
      # for add widget, integers are fromrow,fromcolumn,rowspan,columnspan
      self.gridLayout.addWidget(self.tableview,1,1,1,1)
      self.gridLayout.addWidget(self.inputGroup, 2,0,4,0)
      #self.gridLayout.setRowStretch(4,6)
      
     
      self.iFileLabel = QtGui.QLabel("Add Layers",self.inputGroup)
      self.iFileLabel.setGeometry(QtCore.QRect(10, 64, 80, 25))
      
      
      
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
      
      self.ColumnCombo = QComboBox(self.setAllGroup)
      self.ColumnCombo.addItems(['weightedMean','largestClass'])
      self.ColumnCombo.setGeometry(QtCore.QRect(10, 110, 80, 25))
      self.ColumnCombo.setEnabled(True)
      self.ColumnCombo.hide()
      
      self.setAllColumnButton = QtGui.QPushButton(QtGui.QIcon("file.ico"), 
                                                  "Set Column", self.setAllGroup)
      self.setAllColumnButton.setObjectName('setAllColumnButton')
      self.setAllColumnButton.setGeometry(QtCore.QRect(99, 110, 80, 25))
      self.setAllColumnButton.setEnabled(False)
      self.currentsection = None
      self.connect(self.setAllColumnButton, QtCore.SIGNAL("clicked()"), 
                                                         lambda : self.setColumn(self.currentsection))
                 
      self.gridLayout.addWidget(self.setAllGroup, 2,0,4,0)
      self.setAllGroup.hide()      
      
      self.fileButton = QtGui.QPushButton(QtGui.QIcon("file.ico"), "Browse", self.inputGroup)
      self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
      self.fileButton.setGeometry(QtCore.QRect(120,64,75,33))
      self.connect(self.fileButton, QtCore.SIGNAL("clicked()"), self.showFileDialog)
      
      #self.addButton = QtGui.QPushButton(QtGui.QIcon("file.ico"), "Add", self.inputGroup)
      #self.addButton.setGeometry(QtCore.QRect(155,94,67,30))
      
       
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
      #self.statuslabel.setText(QtGui.QApplication.translate("self", 
      #  'Running Process', None, QtGui.QApplication.UnicodeUTF8))
      
      self.progressbar = QtGui.QProgressBar(self.outputGroup)
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.gridLayout_output.addWidget(self.progressbar)
       
      self.outputGroup.hide()
       
      self.acceptBut = QtGui.QPushButton("OK",self)
      self.rejectBut = QtGui.QPushButton("Close",self)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      
      self.buttonBox.setObjectName("buttonBox")
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
      
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
         
      self.retranslateUi()
      
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept)
       
     
   
   def setColumn(self, section):
      """
      @summary: sets a column value
      """ 
      if self.currentsection is not None:
         if self.currentsection in self.table.comboIndices:
            value = str(self.ColumnCombo.currentText())
            for row, record in enumerate(self.table.tableView.model().data):
               self.table.tableView.model().setColumn(row, section, value)
         else:  
            value = str(self.ColumnSet.text())          
            for row, record in enumerate(self.table.tableView.model().data):
               self.table.tableView.model().setColumn(row, section, value)
      else:
         QMessageBox.warning(self,"Tip: ",
        "Double click on a column heading before setting value")
            
      

      # .........................................
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QtCore.QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" ).toString()
      filenames = QtGui.QFileDialog.getOpenFileNames(self, "Select GeoTIFFs or Shapefiles",dirName,"Layer Files (*.shp *.tif *.zip)")
      self.addFiles(filenames)

   def addFiles(self,filenames):
      for x, file in enumerate(filenames):
         layername = os.path.basename(os.path.splitext(str(file))[0])
         self.table.tableView.model().insertRow(x,[layername,str(file),'','','',''])
      self.inputGroup.hide()
      self.setAllGroup.show()
      # new
      header = self.tableview.horizontalHeader()
      QObject.connect(header, SIGNAL("sectionDoubleClicked(int)"), self.makeEditable)
      self.ColumnSet.setEnabled(True)
      self.setAllColumnButton.setEnabled(True) 
      
      

              
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Upload ancillary layers", None, QtGui.QApplication.UnicodeUTF8))
      
   