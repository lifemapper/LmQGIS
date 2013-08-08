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
from qgis.core import *
from qgis.gui import *

class Ui_Dialog(object):
   
   def setupUi(self,stats):
      self.setObjectName("Dialog")
      # x,y
      self.resize(788, 698)
      self.setMinimumSize(788,698)
      self.setMaximumSize(1698,1548)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      self.gridLayout.setRowMinimumHeight(0,350) 
      self.gridLayout.setRowMinimumHeight(1,300)
      
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif")
      self.inputGroup.setStyle(self.style)
      
      
      
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout_input.setObjectName("gridLayout_input")
      self.gridLayout_input.setRowMinimumHeight(0,25)
      self.gridLayout_input.setRowMinimumHeight(1,40)
      self.gridLayout_input.setRowMinimumHeight(2,210)
      self.gridLayout_input.setRowMinimumHeight(3,25)
      self.gridLayout_input.setColumnMinimumWidth(0,280)
      self.gridLayout_input.setColumnMinimumWidth(1,300)
      
      self.statsLabel = QtGui.QLabel()
      self.statsLabel.setText("Stats Available")
      
      
      self.statsCombo = QtGui.QComboBox()
      self.statsCombo.addItems(sorted(stats))
      #self.statsCombo.setGeometry(QtCore.QRect(20, 560, 313, 25))
      
      self.statsDirLabel = QtGui.QLabel()
      self.statsDirLabel.setText("""Select a pam from the list. Add stats from the drop down to the stats panel by choosing a stat and clicking 'Get Stats', don't dismiss this dialog, you may come back to it to add more stats to the stats panel for comparison.""")
      self.statsDirLabel.setWordWrap(True)
      
     
      
      self.gridLayout_input.addWidget(self.statsLabel,1,0,1,1)
      self.gridLayout_input.addWidget(self.statsCombo,2,0,1,1,QtCore.Qt.AlignTop)
      self.gridLayout_input.addWidget(self.statsDirLabel,2,1,1,1,QtCore.Qt.AlignTop)
      
      self.inputGroup.setLayout(self.gridLayout_input)
      
      
      self.gridLayout.addWidget(self.inputGroup, 1,0,1,1)
      
      
      ###################### output group ####################################
      
      self.outputGroup = QtGui.QGroupBox()
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      
      self.gridLayout_output = QtGui.QGridLayout()
      self.gridLayout_output.setObjectName("gridLayout_input")
      self.gridLayout_output.setColumnMinimumWidth(0,320) 
      self.gridLayout_output.setColumnMinimumWidth(1,25)  
      self.gridLayout_output.setColumnMinimumWidth(2,300)
      self.gridLayout_output.setRowMinimumHeight(0,250)
      self.gridLayout_output.setRowMinimumHeight(1,50)
      
      
      self.progressbar = QtGui.QProgressBar()
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.gridLayout_output.addWidget(self.progressbar,1,0,1,2)
      
              ################## left hand column ###############
      self.leftHandGrid = QtGui.QGridLayout()
      self.leftHandGrid.setRowMinimumHeight(0,100)
      self.leftHandGrid.setRowMinimumHeight(1,20)
      self.leftHandGrid.setRowMinimumHeight(2,40)
      self.leftHandGrid.setRowMinimumHeight(3,90)
      
      self.leftHandGrid.setColumnMinimumWidth(0,210)
      self.leftHandGrid.setColumnMinimumWidth(1,150)
     
      
      
      self.outlabel = QtGui.QLabel()
      self.outlabel.setObjectName("outlabel")   
      self.outlabel.setText("Output to Zipfile, use.zip ext.")
      
      
      self.outEdit = QtGui.QLineEdit()  
      self.outEdit.setObjectName("shapepath")
      self.outEdit.setEnabled(False)
      
      self.fileButton = QtGui.QPushButton("Browse")
      self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
      self.fileButton.setEnabled(False)
      
      self.downloadLabel  = QtGui.QLabel()
      self.downloadLabel.setText('')
      self.downloadLabel.setWordWrap(True)
      
      self.leftHandGrid.addWidget(self.outlabel,     1,0,1,1)
      self.leftHandGrid.addWidget(self.outEdit,      2,0,1,1)
      self.leftHandGrid.addWidget(self.fileButton,   2,1,1,1)
      self.leftHandGrid.addWidget(self.downloadLabel,3,0,1,1)
      
      self.gridLayout_output.addLayout(self.leftHandGrid,0,0,1,1)
                #################### right hand column ########################
      
      self.verticalLayout = QtGui.QVBoxLayout()
      
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
      
      self.verticalLayout.addWidget(self.classifyLabel)
      self.verticalLayout.addWidget(self.speciesrichness)
      self.verticalLayout.addWidget(self.meanproportionalrangesize)
      self.verticalLayout.addWidget(self.proportionalspeciesdiversity)
      self.verticalLayout.addWidget(self.localityrangesize)
      
      self.gridLayout_output.addLayout(self.verticalLayout,0,2,1,1)
      
      self.outputGroup.setLayout(self.gridLayout_output)
      
      self.gridLayout.addWidget(self.outputGroup, 1,0,1,1)
      
      self.outputGroup.hide()
      ####################### End of Outputs ###############################
      
       
      self.getStatsBut = QtGui.QPushButton("Get Stats",self)
      if stats[0] == 'No Stats':
         self.getStatsBut.setEnabled(False)
     
      self.rejectBut = QtGui.QPushButton("Close",self)
      #
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      
      self.buttonBox.addButton(self.getStatsBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
         
      
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
      
      QtCore.QObject.connect(self.fileButton, QtCore.SIGNAL("clicked()"), self.showFileDialog)
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      QtCore.QObject.connect(self.getStatsBut, QtCore.SIGNAL("clicked()"), self.accept)
      
      self.retranslateUi()
    
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QtCore.QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" ).toString()
      fileDialog = QgsEncodingFileDialog( self, "Save .zip File", dirName,"Zip Files (*.zip)")
      fileDialog.setDefaultSuffix( QtCore.QString( "zip" ) )
      fileDialog.setFileMode( QtGui.QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QtGui.QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      self.addFile(filename.first())
      
   def addFile(self,filename):
      self.outEdit.setText(filename)
             
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Randomized Null Models and Original PAM", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
