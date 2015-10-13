# -*- coding: utf-8 -*-
"""
@author: Jeff Cavner
@contact: jcavner@ku.edu

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

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import Qt, QUrl, QObject
from qgis.core import *
from qgis.gui import *
from lifemapperTools.tools.ui_postOccSetDialog import Ui_Dialog
from lifemapperTools.tools.constructGrid import ConstructGridDialog
from lifemapperTools.tools.listExperiments import ListExperimentDialog
from lifemapperTools.tools.newExperiment import NewExperimentDialog
from LmClient.lmClientLib import LMClient
from lifemapperTools.common.communicate import Communicate





class UploadOccSetDialog(QDialog, Ui_Dialog):
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, client=None):
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      self.interface = iface
      self.client = client
      self.fileName = None
      self.populateCanvasCombo()
      #self.setWhatsThis(Qt.tr("This dialog allows a user to sign in to the system."))
# ..............................................................................
   def accept(self):
      # after upload, we recieve an occurrence id
      # which we need to pass back along with everything else to the postExp Dialog
      if self.validate():
         self.uploadBut.setEnabled(False)
         try:
            response = self.client.sdm.postOccurrenceSet(self.displayName,self.fileType,
                                                         self.fileName,epsgCode=self.epsgCode)
         except Exception, e:
            msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               "Problem with the post occurrence set service",
                                               QMessageBox.Ok)
         else:
            occSetId = response.id
            #QgsProject.instance().emit( 
            #                   SIGNAL(
            #                   "PostedOccurrenceSet(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)" ),
            #                   occSetId,self.displayName,self.epsgCode)
            Communicate.instance().postedOccurrenceSet.emit(occSetId,self.displayName,self.epsgCode)
            self.close()
# ..............................................................................
   def validate(self):
      
      epsgCode = str(self.epsgCodeEdit.text())
      self.displayName = self.displayNameEdit.text()
      if self.fileName is None:
         self.fileName = self.file.text()
      self.fileType = self.getFileType(userData=False)
      self.occMapLayerName = self.canvasLayersCombo.currentText()
      valid = True
      if len(epsgCode) == 0:
         message = "Please supply an EPSG code"
         valid = False
      elif len(self.displayName) == 0:
         message = "Please supply a display name"
         valid = False 
      elif len(self.fileName) == 0:        
         if self.occMapLayerName == "":  
            message = "Please supply a filename or choose a layer from your map canvas"
            valid = False
         
      elif len(self.fileType) == 0:
         message = "Please supply a file type"
         valid = False 
         
      # this ensures that file type matches 
      
      fileName, fileExtension = os.path.splitext(self.fileName)
      fileExt = fileExtension[1:]
      extIdx = self.fileTypeCombo.findData(fileExt, role=Qt.UserRole)  
      self.fileTypeCombo.setCurrentIndex(extIdx)
      self.fileType = self.getFileType(userData=False)
         
                
      if not valid:
         msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok)
      else:
         self.epsgCode = int(epsgCode)
      return valid 
         
# ..............................................................................
   def setFileNameFromCombo(self):
      currentIndex = self.canvasLayersCombo.currentIndex()
      fileNameVariant = self.canvasLayersCombo.itemData(currentIndex,role=Qt.UserRole)
      
      tocName = str(self.canvasLayersCombo.itemData(currentIndex,role=Qt.DisplayRole))
      layers = self.interface.legendInterface().layers()
      for layer in layers:
         if layer.name() == tocName:
            if layer.isEditable() and layer.isModified():
               self.interface.setActiveLayer(layer)
               self.interface.actionToggleEditing().trigger()
               
               
      self.fileName = str(fileNameVariant)
      
# ..............................................................................
   def selectFromCanvas(self,index):     
      if index != 0:
         # clear and disable filename text
         self.file.setText('')
         self.file.setEnabled(False) # maybe
         shpIdx = self.fileTypeCombo.findData('shp', role=Qt.UserRole)  
         self.fileTypeCombo.setCurrentIndex(shpIdx)
         self.setFileNameFromCombo()
      elif index == 0:
         self.fileName = None
         

      
# ..............................................................................
   def populateCanvasCombo(self):  
      layers = QgsMapLayerRegistry.instance().mapLayers()
      self.canvasLayersCombo.addItem("",userData="select")
      for key in layers.keys():
         # probably need to think about multipoint
         if layers[key].type() == layers[key].VectorLayer:
            if layers[key].geometryType() == QGis.Point:
               source = layers[key].source() 
               name = layers[key].name()
               self.canvasLayersCombo.addItem(name,userData=source)
      
      self.canvasLayersCombo.currentIndexChanged.connect(self.selectFromCanvas)
# ..............................................................................
   def openProjSelectorSetEPSG(self):
      """
      @summary: opens the stock qgis projection selector
      and sets epsg edit field and set map units attribute
      """
      projSelector = QgsGenericProjectionSelector(self)
      dialog = projSelector.exec_()
      EpsgCode = projSelector.selectedAuthId().replace('EPSG:','')
      # some projections don't have epsg's
      if dialog != 0:
         if EpsgCode != 0:  # will be zero if projection doesn't have an epsg
            crs = QgsCoordinateReferenceSystem()
            crs.createFromOgcWmsCrs( projSelector.selectedAuthId() )
            mapunitscode = crs.mapUnits()
            if mapunitscode == 0:
               self.mapunits = 'meters'
            elif mapunitscode == 1:
               self.mapunits = 'feet'
            elif mapunitscode == 2:
               self.mapunits = 'dd' 
            self.epsgCodeEdit.setText(str(EpsgCode))
         else:
            # error message saying that the users chosen projection doesn't have a epsg
            self.mapunits = None
            message = "The projection you have chosen does not have an epsg code"
            msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
      else:
         self.mapunits = None 
# ....................................................................................
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      # get the selection for file type and set file type here
      settings = QSettings()
      self.file.setEnabled(True)
      filetype = self.getFileType()
      filetypestr = "%s files (*.%s)" % (filetype, filetype)
      dirName = settings.value( "/UI/lastShapefileDir" )
      fileDialog = QgsEncodingFileDialog( self, "Open File", dirName,filetypestr)
      fileDialog.setDefaultSuffix(  "shp"  )
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      self.addFile(filename[0])
# ..................................................................................
   def getFileType(self,userData=True):
      if userData:
         currentIndex = self.fileTypeCombo.currentIndex()
         fileVariant = self.fileTypeCombo.itemData(currentIndex,role=Qt.UserRole)
         filetype = str(fileVariant)
      else:
         filetype = str(self.fileTypeCombo.currentText())
      return filetype
# ..................................................................................
   def addFile(self,filename):
      # set/clear the canvas layers combo back to select, this
      # will fire index changed and set self.fileName to None
      self.canvasLayersCombo.setCurrentIndex(0)
      self.file.setText(filename)  
# .................................................................................         
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('signIn')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()   
