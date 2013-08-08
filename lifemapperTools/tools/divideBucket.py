# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2011 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

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
import os
import types
import zipfile
from PyQt4.QtGui import *
from qgis.core import *
from lifemapperTools.tools.ui_constructGridDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GridConstructor
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
   def __init__(self, iface, RADids=None, inputs=None, client=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process
      @param inputs: dictionary with inputs, keys are argument names in the 
      client library
      """
      QDialog.__init__(self)
      self.setupUi()
      self.client = client
      self.iface = iface # new attribute for this dialog
      cc = self.rejectBut
      bok = self.acceptBut
      self.inputs = inputs
      self.selectedFeatureWKT = None
      self.expId = inputs['expId']
      _Controller.__init__(self, iface, BASE_URL=GridConstructor.BASE_URL, 
                           STATUS_URL=GridConstructor.STATUS_URL, 
                           REST_URL=GridConstructor.REST_URL,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, client=client)
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

   def validate(self):
         """
         @summary: Validates the inputs for the dialog
         """
         valid = True
         message = ""
         self.keyvalues = {}
         self.keyvalues['newshpName'] = str(self.epsgEdit.text())
         self.keyvalues['shpName'] = str(self.nameEdit.text())
         
         if self.selectedFeatureWKT is not None:
            self.keyvalues['cutout'] = self.selectedFeatureWKT
         if len(self.shpName.text()) <= 0:
            message = "No original shapegrid name"
            valid = False
         if len(self.newshpName.text()) <= 0:
            message = "No original shapegrid name"
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
         self.getFeatureWKT()
      
         
   # ...........................................................................
   def getFeatureWKT(self):
      layer = self.iface.activeLayer()
      if layer:
         features = layer.selectedFeatures()
         if len(features) == 1:
            # check for just one feature ?
            g = features[0].geometry()
            Qwkt = g.exportToWkt()
            self.selectedFeatureWKT = str(Qwkt)
         else:       
            self.useSelectedFeature.setChecked(False)
            
            message = "Select one feature"
            msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
      else:       
         self.useSelectedFeature.setChecked(False)
         message = "There is no active layer"
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
       
       
   # ...........................................................................
   def getShapeFile(self, bucketId, model): 
      success = self.client.rad.getShapegridData(str(self.outEdit.text()), str(self.expId),
                                             str(bucketId))
      if success:
         pathname = self.outEdit.text()
         zippath = os.path.dirname(str(pathname))                         
         z = zipfile.ZipFile(str(pathname),'r')
         for name in z.namelist():
            f,e = os.path.splitext(name)
            if e == '.shp':
               shapename = name
            z.extract(name,str(zippath))
         vectorpath = os.path.join(zippath,shapename)
         vectorLayer = QgsVectorLayer(vectorpath,shapename.replace('.shp',''),'ogr')
         #vectorLayer.loadNamedStyle()
         warningname = shapename
         
         if not vectorLayer.isValid():
            QMessageBox.warning(self.outputGroup,"status: ",
              warningname)                  
         QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
         self.close()
      else:
         message = "Could not retrieve the shapefile"
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
   # ...........................................................................        
   def setInputGroup(self, *args):
      """
      @summary: sets the inputs in the inputGroups, 
      """
      # maybe set some default params given information from the project
      # or canvas
      pass
         
   
      

      