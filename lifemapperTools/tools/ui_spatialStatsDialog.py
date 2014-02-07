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
   
   def setupUi(self,stats=None):
      self.setObjectName("Dialog")
      # x,y
      self.resize(788, 498)
      self.setMinimumSize(788,498)
      self.setMaximumSize(1698,1548)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      
      ###################### output group ####################################
      
      self.outputGroup = QtGui.QGroupBox()
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      
      self.gridLayout_output = QtGui.QGridLayout()
      self.gridLayout_output.setObjectName("gridLayout_input")
      self.gridLayout_output.setColumnMinimumWidth(0,370) 
      self.gridLayout_output.setColumnMinimumWidth(1,25)  
      self.gridLayout_output.setColumnMinimumWidth(2,300)
      self.gridLayout_output.setRowMinimumHeight(0,450)
      self.gridLayout_output.setRowMinimumHeight(1,50)
      
      
      self.progressbar = QtGui.QProgressBar()
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.progressbar.hide()
      self.gridLayout_output.addWidget(self.progressbar,1,0,1,3)
      
      
      ################## left hand column ###############
      self.leftHandGrid = QtGui.QGridLayout()
      self.leftHandGrid.setRowMinimumHeight(0,100)
      self.leftHandGrid.setRowMinimumHeight(1,20)
      self.leftHandGrid.setRowMinimumHeight(2,50)
      self.leftHandGrid.setRowMinimumHeight(3,50)
      
      self.leftHandGrid.setColumnMinimumWidth(0,210)
      self.leftHandGrid.setColumnMinimumWidth(1,150)
     
      self.pamsCombo = QtGui.QComboBox()
      
      self.outlabel = QtGui.QLabel()
      self.outlabel.setObjectName("outlabel")   
      self.outlabel.setText("Output to Zipfile")
      self.outlabel.hide()
      
      self.outEdit = QtGui.QLineEdit()  
      self.outEdit.setObjectName("shapepath")
      #self.outEdit.setEnabled(False)
      self.outEdit.hide()
      
      self.fileButton = QtGui.QPushButton("Browse")
      self.fileButton.setMaximumSize(65,30)
      self.fileButton.setMinimumSize(65, 30)
      self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
      #self.fileButton.setEnabled(False)
      self.fileButton.hide()
      
      self.downloadLabel  = QtGui.QLabel()
      self.downloadLabel.setText('')
      self.downloadLabel.setWordWrap(True)
      
      self.leftHandGrid.addWidget(self.pamsCombo,    0,0,1,1)
      self.leftHandGrid.addWidget(self.outlabel,     1,0,1,1,QtCore.Qt.AlignBottom)
      self.leftHandGrid.addWidget(self.outEdit,      2,0,1,1)
      self.leftHandGrid.addWidget(self.fileButton,   2,1,1,1)
      self.leftHandGrid.addWidget(self.downloadLabel,3,0,1,1)
      
      self.gridLayout_output.addLayout(self.leftHandGrid,0,0,1,1)
      #################### right hand column ########################
      
      #self.verticalLayout = QtGui.QVBoxLayout()
      self.verticalLayout = QtGui.QGridLayout()
      self.verticalLayout.setRowMinimumHeight(0,100)
      self.verticalLayout.setRowMinimumHeight(0,80)
      self.verticalLayout.setRowMinimumHeight(0,300)
      self.innerverticalLayout = QtGui.QVBoxLayout()
      
      
      self.classifyLabel = QtGui.QLabel()
      self.classifyLabel.setText('The following site based stats will be attached to your shapefile.  You can choose which stat to classify your map on download.')
      self.classifyLabel.setWordWrap(True)
      
      self.speciesrichness = QtGui.QRadioButton('Species Richness')
      self.speciesrichness.setEnabled(True)
      self.speciesrichness.setChecked(True)
      
      self.meanproportionalrangesize = QtGui.QRadioButton('Mean Prop Range Size')
      self.meanproportionalrangesize.setEnabled(True)
      
      self.proportionalspeciesdiversity = QtGui.QRadioButton('Prop Species Diversity')
      self.proportionalspeciesdiversity.setEnabled(True)
      
      self.localityrangesize = QtGui.QRadioButton('Locality Range Size')
      self.localityrangesize.setEnabled(True)
      
      self.verticalLayout.addWidget(self.classifyLabel,1,0,1,1,QtCore.Qt.AlignTop)
      self.innerverticalLayout.addWidget(self.speciesrichness)
      self.innerverticalLayout.addWidget(self.meanproportionalrangesize)
      self.innerverticalLayout.addWidget(self.proportionalspeciesdiversity)
      self.innerverticalLayout.addWidget(self.localityrangesize)
      self.verticalLayout.addLayout(self.innerverticalLayout,2,0,1,1,QtCore.Qt.AlignTop)
      
      self.gridLayout_output.addLayout(self.verticalLayout,0,2,1,1)
      
      self.outputGroup.setLayout(self.gridLayout_output)
      
      self.gridLayout.addWidget(self.outputGroup, 0,0,1,2)
      
      #self.outputGroup.hide()
      ####################### End of Outputs ###############################
      
       
      self.getStatsBut = QtGui.QPushButton("Get Stats")
      #if stats[0] == 'No Stats':
      #   self.getStatsBut.setEnabled(False)
     
      self.rejectBut = QtGui.QPushButton("Close",self)
      #
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      self.helpBut.clicked.connect(self.help)
      
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.getStatsBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
         
      
      self.gridLayout.addWidget(self.buttonBox, 1, 1 ,1, 1)
      
      self.rejectBut.clicked.connect(self.reject)
      self.getStatsBut.clicked.connect(self.accept)
      
      self.retranslateUi()
    
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QtCore.QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" )
      fileDialog = QgsEncodingFileDialog( self, "Save .zip File", dirName,"Zip Files (*.zip)")
      fileDialog.setDefaultSuffix("zip"  )
      fileDialog.setFileMode( QtGui.QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QtGui.QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      self.addFile(filename[0])
      
   def addFile(self,filename):
      self.outEdit.setText(filename)
             
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Spatial Site Based Statistics", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
