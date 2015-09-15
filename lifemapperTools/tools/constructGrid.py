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
import types
import sys
import zipfile
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QUrl, QDir
from qgis.core import *
from LmClient.lmClientLib import LMClient
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.tools.ui_constructGridDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GENERIC_REQUEST

# .............................................................................

class ConstructGridDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   #__metaclass__ = classmaker()
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, epsg=None,parent=None,
                mapunits=None,resume=False):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process
      @param inputs: dictionary with inputs, keys are argument names in the 
      client library
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      self.client = client
      self.iface = iface       
      if resume:
         self.iface.addProject(resume)      
      self.workspace = Workspace(self.iface,self.client)
      cc = self.rejectBut
      bok = self.acceptBut
      self.inputs = inputs
      self.epsg = epsg
      self.mapunits = mapunits
      self.parent = parent
      if self.epsg is not None:
         self.setEPSG()
      if self.mapunits is not None:
         self.setMapUnitsCombo(mapunits)
      self.selectedFeatureWKT = None
      self.expId = inputs['expId']
      _Controller.__init__(self, iface, cancel_close=cc, okayButton=bok,
                           initializeWithData=False, client=client)
# ...........................................................................
   def setEPSG(self):
      self.epsgEdit.setText(self.epsg)
      self.epsgEdit.setEnabled(False)
# ...........................................................................
   def setMapUnitsCombo(self,mapunits):
      """
      @summary: 
      @param mapunits : integer from qgis enum of mapunits,
      #Meters = 0,
      #Feet = 1,
      #Degrees = 2, decimalDegrees,DegreesMinutesSeconds,DegreesDecimalMinutes
      """
      # get the index in the combo that matches mapunits
      if type(mapunits) == int:
         unitIdx = self.selectUnits.findData(str(mapunits),
                                             role=Qt.UserRole)
      else:
         unitIdx = self.selectUnits.findData(str(mapunits),
                                             role=Qt.DisplayRole)
      self.selectUnits.setCurrentIndex(unitIdx)
      self.selectUnits.setEnabled(False)
      
# ...........................................................................
   def accept(self):
      
      valid = self.validate()  
      if valid:   
         self.inputGroup.hide()      
         self.statuslabel.setText('Running Process')
         self.progressbar.reset()
         self.outputGroup.setTitle('Outputs')
         self.outputGroup.show()
         if self.inputs is not None:
            self.keyvalues.update(self.inputs)
         self.startThread(GENERIC_REQUEST,outputfunc = self.getShapeFile, 
                          requestfunc=self.client.rad.addBucket, client=self.client,
                          inputs=self.keyvalues)
         
   def _testFloat(self,coord):
      coordFloat = True
      try:
         float(coord)
      except:
         coordFloat = False
      return coordFloat
   
   def _checkBoundingBox(self): 
      validBBox = True
      if float(self.northEdit.text()) < float(self.southEdit.text()):
         validBBox = False
      elif float(self.eastEdit.text()) < float(self.westEdit.text()):
         validBBox = False
      return validBBox
               
            
# ............................................................................. 
   def validate(self):
         """
         @summary: Validates the inputs for the dialog
         """
         valid = True
         message = ""
         self.keyvalues = {}
         if self.hexCheck.isChecked():
            self.keyvalues['cellShape'] = 'hexagon'
         elif self.squareCheck.isChecked():
            self.keyvalues['cellShape'] = 'square'          
         self.keyvalues['mapUnits'] = str(self.selectUnits.currentText())
         self.keyvalues['bbox'] = str(self.westEdit.text())+","+ \
                                   str(self.southEdit.text())+","+\
                                   str(self.eastEdit.text())+","+ \
                                   str(self.northEdit.text())
         self.keyvalues['cellSize'] = str(self.resEdit.text())
         self.keyvalues['epsgCode'] = str(self.epsgEdit.text())
         self.keyvalues['shpName'] = str(self.nameEdit.text())      
           
         if self.selectedFeatureWKT is not None:
            self.keyvalues['cutout'] = self.selectedFeatureWKT         
         if len(self.northEdit.text()) <= 0 or not self._testFloat(self.northEdit.text()):
            message = "Please supply a max y"
            valid = False
         elif len(self.southEdit.text()) <= 0 or not self._testFloat(self.southEdit.text()):
            message = "Please supply a min y"
            valid = False 
         elif len(self.eastEdit.text()) <= 0 or not self._testFloat(self.eastEdit.text()):
            message = "Please supply a max x"
            valid = False
         elif len(self.westEdit.text()) <= 0 or not self._testFloat(self.westEdit.text()):
            message = "Please supply a min x"
            valid = False
         elif not self._checkBoundingBox():
            message = "bounding box is incorrect"
            valid = False
         elif len(self.resEdit.text()) <= 0:
            message = "Please supply a cell size"
            valid = False 
         elif len(self.epsgEdit.text()) <= 0:
            message = "Please supply an epsg code"
            valid = False
         #elif len(self.outEdit.text()) <= 0:
         #   message = "Please supply output path for shapefile"
         #   valid = False
         elif len(self.nameEdit.text()) <= 0:
            message = "Please supply grid name"
            valid = False         
         
         if not valid:
            msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
         return valid 
# ...........................................................................
   def checkUseSelected(self):

      if self.useSelectedFeature.isChecked():         
         self.northEdit.clear()
         self.southEdit.clear()
         self.eastEdit.clear()
         self.westEdit.clear()
         self.northEdit.setEnabled(False)
         self.southEdit.setEnabled(False)
         self.eastEdit.setEnabled(False)
         self.westEdit.setEnabled(False)         
         self.enterCoords.setChecked(False)
         self.getFeatureWKT()         
      elif not self.useSelectedFeature.isChecked():
         self.useSelectedFeature.setChecked(True)
      
# ...........................................................................
   def checkEnterCoords(self):
      if self.enterCoords.isChecked():
         self.northEdit.clear()
         self.southEdit.clear()
         self.eastEdit.clear()
         self.westEdit.clear()
         
         self.northEdit.setEnabled(True)
         self.southEdit.setEnabled(True)
         self.eastEdit.setEnabled(True)
         self.westEdit.setEnabled(True)
         
         self.northEdit.setFocus(Qt.OtherFocusReason)
         
         self.useSelectedFeature.setChecked(False)
         
         self.selectedFeatureWKT = None
      elif not self.enterCoords.isChecked():
         self.northEdit.setFocus(Qt.OtherFocusReason)
         self.enterCoords.setChecked(True)
         
           
# ...........................................................................
   def getFeatureWKT(self):
      layer = self.iface.activeLayer()
      if layer:
         features = layer.selectedFeatures()
         if len(features) == 1:
            # check for just one feature ?
            g = features[0].geometry()
            bboxRect = g.boundingBox()
            minx = bboxRect.xMinimum()
            miny = bboxRect.yMinimum()
            maxx = bboxRect.xMaximum()
            maxy = bboxRect.yMaximum()
            # set bounding box inputs
            self.eastEdit.setText(str(maxx))
            self.westEdit.setText(str(minx))
            self.northEdit.setText(str(maxy))
            self.southEdit.setText(str(miny))
            Qwkt = g.exportToWkt()
            self.selectedFeatureWKT = str(Qwkt)
         else:
            self.northEdit.setEnabled(True)
            self.southEdit.setEnabled(True)
            self.eastEdit.setEnabled(True)
            self.westEdit.setEnabled(True)
   
            self.northEdit.clear()
            self.southEdit.clear()
            self.eastEdit.clear()
            self.westEdit.clear()
            
            self.northEdit.setFocus(Qt.OtherFocusReason)
            self.useSelectedFeature.setChecked(False)
            self.enterCoords.setChecked(True)
            self.selectedFeatureWKT = None           
            message = "Select one feature"
            msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
      else:
         self.northEdit.setEnabled(True)
         self.southEdit.setEnabled(True)
         self.eastEdit.setEnabled(True)
         self.westEdit.setEnabled(True)
   
         self.northEdit.clear()
         self.southEdit.clear()
         self.eastEdit.clear()
         self.westEdit.clear()
         
         self.northEdit.setFocus(Qt.OtherFocusReason)
         self.useSelectedFeature.setChecked(False)
         self.enterCoords.setChecked(True)
         self.selectedFeatureWKT = None
            
         #self.useSelectedFeature.setChecked(False)
         message = "There is no active layer"
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
       
       
# ..............................................................................
   def getShapeFile(self, bucketId, model): 
      """
      @summary: calls the client where it gets the shapefile, unzips and adds
      to canvas
      @param model: not used here but sent by the controller
      """
      if bucketId is not None:
         expFolder = self.workspace.getExpFolder(self.expId)
         if not expFolder:
            expFolder = self.workspace.createProjectFolder(self.expId)
         gridZipName = "%s_%s" % (str(self.expId),str(bucketId))
         pathname = os.path.join(expFolder,gridZipName)
         success = self.client.rad.getBucketShapegridData(pathname, str(self.expId),
                                                    str(bucketId))  
         #success = self.client.rad.getBucketShapegridData(str(self.outEdit.text()), str(self.expId),
         #                                          str(bucketId))   
         if success:
            #pathname = self.outEdit.text()
            zippath = os.path.dirname(str(pathname))                         
            z = zipfile.ZipFile(str(pathname),'r')
            for name in z.namelist():
               f,e = os.path.splitext(name)
               if e == '.shp':
                  shapename = name
               z.extract(name,str(zippath))
            vectorpath = os.path.join(zippath,shapename)
            vectorLayer = QgsVectorLayer(vectorpath,shapename.replace('.shp',''),'ogr')
            warningname = shapename         
            if not vectorLayer.isValid():
               QMessageBox.warning(self.outputGroup,"status: ",
                 warningname)             
            QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
            if self.parent is not None:
               try:
                  self.parent.refresh()
               except Exception,e:
                  print "Exception in construct refresh",str(e)
            self.close()
         else:
            message = "Could not retrieve the shapefile"
            msgBox = QMessageBox.information(self,
                                                      "Problem...",
                                                      message,
                                                      QMessageBox.Ok)
      else:
         message = "Grid may be too large, check resolution, limit is < 400,000 cells"
         msgBox = QMessageBox.information(self,
                                                      "Problem...",
                                                      message,
                                                      QMessageBox.Ok)
         
# .............................................................................         
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
      helpDialog.scrollToAnchor('constructGrid')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
      
      
if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   #d = PostScenarioDialog(match=True,scenarioId=204,client=client)
   d = ConstructGridDialog(None,client=client,inputs={'expId':4123513515})
   d.show()
   sys.exit(qApp.exec_())