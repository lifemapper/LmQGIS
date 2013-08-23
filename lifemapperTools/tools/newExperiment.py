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
import numpy as np
from collections import namedtuple
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings, Qt, SIGNAL, QUrl, QString
from qgis.core import *
from qgis.gui import *
from lifemapperTools.tools.ui_newExperimentDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.tools.listPALayers import ListPALayersDialog
from lifemapperTools.tools.constructGrid import ConstructGridDialog
from lifemapperTools.tools.uploadLayers import UploadDialog
from lifemapperTools.tools.uploadAncLayers import UploadAncillDialog
from lifemapperTools.tools.listBuckets import ListBucketsDialog
from lifemapperTools.tools.addSDMLayer import UploadSDMDialog
from lifemapperTools.common.pluginconstants import ListExperiments, GENERIC_REQUEST 
from lifemapperTools.common.pluginconstants import QGISProject
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.tools.radTable import RADTable







class NewExperimentDialog(_Controller,QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, email=None):
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.interface = iface 
      self.workspace = Workspace(self.interface,client)
      self.checkExperiments()    
      self.setupUi()     
      self.client = client
      cc = self.rejectBut
      bok = self.acceptBut
      self.expId = None
      self.mapunits = None
      self.keyvalues = {}
      if email is not None:
         self.keyvalues['email'] = email
      _Controller.__init__(self, iface, BASE_URL=ListExperiments.BASE_URL, 
                           STATUS_URL=ListExperiments.STATUS_URL, 
                           REST_URL=ListExperiments.REST_URL,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, client=client)

# ..............................................................................   
   def _checkQgisProjForKey(self):
      project = QgsProject.instance()
      filename = str(project.fileName())  
      found = False
      s = QSettings()
      for key in s.allKeys():
         if 'RADExpProj' in key:
            value = str(s.value(key).toString())
            if value == filename:
               found = True
               expId = key.split('_')[1]
               s.setValue("currentExpID", int(expId))  
      return found   

        
# ..............................................................................
      
   def checkExperiments(self):
      """
      @summary: gets the current expId, if there is one it gets the current
      project path associated with that id.  If there is a project path, it 
      triggers a save project.  If there is no path, it asks a save as, and sets 
      the project path for the id. The last thing it does is to open a new 
      qgis project
      """   
      s = QSettings()
      currentExpId  = s.value("currentExpID",QGISProject.NOEXPID).toInt()[0]
      if currentExpId != QGISProject.NOEXPID:
         currentpath = str(s.value("RADExpProj_"+str(currentExpId),
                                   QGISProject.NOPROJECT).toString())
         if currentpath != QGISProject.NOPROJECT and currentpath != '':
            self.interface.actionSaveProject().trigger()
         else:
            if len(QgsMapLayerRegistry.instance().mapLayers().items()) > 0:
               #self.interface.actionSaveProjectAs().trigger()
               self.workspace.saveQgsProjectAs(currentExpId)
               
         # now  actionNewProject
         self.interface.actionNewProject().trigger()
         s.setValue("currentExpID",QGISProject.NOEXPID)
      else: # no experiment Id
         # there is a case where a Qgis project can be opened but there is no
         # current id, like after a sign out but that Qgis project belongs to an id, in that case it needs
         # to start a new project
         if len(QgsMapLayerRegistry.instance().mapLayers().items()) == 0 or self._checkQgisProjForKey():      
            self.interface.actionNewProject().trigger()
        
            
         


# ..............................................................................      
   def accept(self):
      
     
      valid = self.validate()
      if self.expId is not None:
         self.openNewDialog()        
      elif valid and self.expId is None: 
         self.startThread(GENERIC_REQUEST,outputfunc = self.newExperimentCallBack, 
                          requestfunc=self.client.rad.postExperiment, client=self.client,
                          inputs=self.keyvalues)
      elif not valid and self.expId is None:
         pass
         
      
# ..............................................................................
   def validate(self):  
      valid = True
      message = ""
      self.keyvalues['epsgCode'] = str(self.epsgEdit.text())
      self.keyvalues['name'] = str(self.expNameEdit.text())
      self.keyvalues['description'] = str(self.description.toPlainText())
      epsg = self.epsgEdit.text()   
      experimentname = self.expNameEdit.text()
      if len(experimentname) <= 0:
         message = "Please supply a experiment name"
         valid = False
      elif len(epsg) <= 0:
         message = "Please supply an EPSG code"
         valid = False
      if not valid:
         msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
      return valid

# ..............................................................................
   def openProjSelectorSetEPSG(self):
      """
      @summary: opens the stock qgis projection selector
      and sets epsg edit field and set map units attribute
      """
      projSelector = QgsGenericProjectionSelector(self)
      dialog = projSelector.exec_()
      EpsgCode = projSelector.selectedEpsg()
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
            
            self.epsgEdit.setText(str(EpsgCode))
         else:
            # error message saying that the users chosen projection doesn't have a epsg
            self.mapunits = None
            message = "The projection you have chosen does not have an epsg code"
            msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
      else:
         print "closed dialog without choosing a projection"
         self.mapunits = None
         
         

# ..............................................................................
   def verifyEmail(self,email):
      valid = True 
      if '@' in email:
         atIndex = email.index('@')
         domainsubstring = email[atIndex+1:] 
         if '.' in domainsubstring:
            if domainsubstring.index('.') == 0:
               valid = False
         else:
            valid = False
      else:
         valid = False
      return valid
# ..............................................................................   
   def cleanInputGridLayout(self):
      
      """@summary:  cleans out the input grid layout"""
     
      if not(self.gridLayout_input.isEmpty()):
         for childindex in range(0,self.gridLayout_input.count()):
            item = self.gridLayout_input.takeAt(0)
            if not(type(item) is types.NoneType):
               item.widget().deleteLater()
              
         self.gridLayout_input.update()  
# ..............................................................................
   def setMapUnitsFromEPSG(self):
      crs = QgsCoordinateReferenceSystem()
      crs.createFromOgcWmsCrs( QString("EPSG:%s" % (str(self.expEPSG)) ))
      mapunitscode = crs.mapUnits()
      if mapunitscode == 0:
         self.mapunits = 'meters'
      elif mapunitscode == 1:
         self.mapunits = 'feet'
      elif mapunitscode == 2:
         self.mapunits = 'dd'
# ..............................................................................         
   def newExperimentCallBack(self, item, model):
      """
      @summary: when a new expid comes back it gets saved to settings as
      currentExpID, then calls openNewDialog
      """
      self.epsgEdit.setEnabled(False)
      self.expNameEdit.setEnabled(False)
      self.description.setEnabled(False)
      self.emptyRadio.setEnabled(False)
      self.expId = item.id
      self.expEPSG = item.epsgcode
      if self.mapunits is None:
         self.setMapUnitsFromEPSG()
      self.setNewExperiment()
      #self.interface.actionNewProject().trigger() # this way won't allow you to have a mask in the canvas prior
      QgsProject.instance().emit( SIGNAL( "ActivateExp(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)" ), self.expId,self.expEPSG,self.mapunits)
      self.openNewDialog()
# ..............................................................................
   def setNewExperiment(self):
      """
      @summary: sets the currentExpID key in settings and creates a project folder in workspace 
      and quietly save the new QGIS project to it
      """
      try:
         s = QSettings()
         s.setValue("currentExpID", self.expId)
         self.workspace.saveQgsProjectAs(self.expId)
      except:
         QMessageBox.warning(self,"status: ",
                         "Could not save expId to settings") 
      
# ..............................................................................         
   def openNewDialog(self):
      inputs = {'expId':self.expId}
      experimentname = self.keyvalues['name'] 
      if self.gridRadio.isChecked():       
         self.constructGridDialog = ConstructGridDialog( self.interface, 
                                                         inputs = inputs,
                                                         client = self.client,
                                                         epsg=self.expEPSG,
                                                         mapunits=self.mapunits)
         self.setModal(False)
         self.constructGridDialog.show()
         self.listBucketsRadio.show() 
              
      elif self.addSDMLayerRadio.isChecked():          
         SDMDialog = UploadSDMDialog(self.interface,
                                    inputs = inputs,
                                    client = self.client,
                                    epsg=self.expEPSG,
                                    experimentname = experimentname,
                                    mapunits=self.mapunits)
         self.setModal(False) 
         SDMDialog.exec_() 
         self.listPALayersRadio.show() 
                        
      elif self.addLocalSpeciesRadio.isChecked():        
         d = UploadDialog(self.interface,
                          inputs = inputs,
                          client = self.client,
                          epsg=self.expEPSG,
                          experimentname=experimentname,
                          mapunits=self.mapunits) 
         d.exec_() 
         self.listPALayersRadio.show()
         
      #elif self.envRadio.isChecked():    
      #   d = UploadAncillDialog(self.interface, inputs = inputs,
      #                    client = self.client) 
      #   d.exec_()       
      elif self.emptyRadio.isChecked():         
         pass      
      elif self.listBucketsRadio.isChecked():
         d = ListBucketsDialog(self.interface, inputs=inputs,
                                  client= self.client, epsg=self.expEPSG,
                                  mapunits=self.mapunits)
         d.exec_()         
      elif self.listPALayersRadio.isChecked():
         d = ListPALayersDialog(self.interface, inputs=inputs,
                                  client= self.client, epsg=self.expEPSG,
                                  mapunits=self.mapunits)
         d.exec_()         
      self.acceptBut.setEnabled( True )

# ..............................................................................         
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(QStringList('documents'))
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('newRADExperiment')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()
      
if __name__ == "__main__":
#  
   #client =  LMClient(userId='blank', pwd='blank')
   import sys
   qApp = QApplication(sys.argv)
   d = NewExperimentDialog(None)#,experimentId=596106
   d.show()
   sys.exit(qApp.exec_())         

      
      
