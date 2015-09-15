# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2014 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

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
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from LmClient.lmClientLib import LMClient
from lifemapperTools.tools.ui_uploadLayersDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GridConstructor
from LmCommon.common.lmconstants import OutputFormat #OutputFormat.GTIFF, OutputFormat.SHAPE

# .............................................................................

class UploadDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   #__metaclass__ = classmaker()
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, epsg=None,
                experimentname='',mapunits=None,resume=False):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi(experimentname=experimentname)
      if resume:
         iface.addProject(resume)
      cc = self.rejectBut
      bok = self.acceptBut
      self.client = client
      self.inputs = inputs  
      _Controller.__init__(self, iface, BASE_URL=GridConstructor.BASE_URL, 
                           STATUS_URL=GridConstructor.STATUS_URL, 
                           REST_URL=GridConstructor.REST_URL,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, outputfunc=None, 
                           requestfunc=None, client=client )
      
      self.expEPSG = epsg
      if mapunits is not None:
         self.mapunits = mapunits
# ..............................................................................      
   def getFields(self,filenames): 
      """
      @summary: given a list of filenames returns a list of lists containing field names
      for the shapefiles
      @param filenames: file location of shapefiles
      @return: returns a list of lists of field names of the shapefiles in filenames
      """
      hasOGR = True
      try:
         from osgeo import ogr
      except:
         hasOGR = False
      fields = []
      for file in filenames:
         choices = ['please select']
         handle = ogr.Open(str(file))
         layerObj = handle.GetLayer(0)
         layerDef = layerObj.GetLayerDefn()
         fieldCount = layerDef.GetFieldCount()
         for fieldIdx in range(0,fieldCount):
            fieldDef = layerDef.GetFieldDefn(fieldIdx)
            choices.append(fieldDef.GetName())
         fields.append(choices)
         handle.Destroy()
      return fields
   
   def checkCRS(self,record):
      match = True
      path = record[1][1]
      f, extension = os.path.splitext(record[1][1])
      if extension == OutputFormat.SHAPE:
         QgsLayer = QgsVectorLayer(path,'testCRS','ogr')
         epsg = str(QgsLayer.crs().authid()).strip('EPSG:')
      if extension == OutputFormat.GTIFF:
         QgsLayer = QgsRasterLayer(path,'testCRS')
         epsg = str(QgsLayer.crs().authid()).strip('EPSG:')
      if str(epsg) != str(self.expEPSG):
         match = False
      return match
# ..............................................................................       
   def checkNamesCRS(self):
      renameList = []
      idList = []
      crsMismatch = []
      for record in enumerate(self.table.tableView.model().data):
         crsMatch = self.checkCRS(record)
         if crsMatch:
            crsMismatch.append(True)
            name = record[1][0]
            layerList = self.client.rad.listLayers(layerName=name,epsgCode=self.expEPSG)
            if len(layerList) > 0:
               renameList.append(name)
               idList.append(layerList[0].id)
         else:
            crsMismatch.append(False)
            
      return renameList, idList, crsMismatch
# ..............................................................................   
   def addUpload(self, names, ids, record, skipUpload=False):
      if not skipUpload:  
         upload = False  
         try:
            f, extension = os.path.splitext(record[1][1])
            if extension == OutputFormat.SHAPE: 
               postresponse = self.client.rad.postVector(**{'filename':record[1][1],
                                                        'name':record[1][0],
                                                        'epsgCode':self.expEPSG,
                                                        'mapUnits':self.mapunits})
            if extension == OutputFormat.GTIFF:
               postresponse = self.client.rad.postRaster(**{'filename':record[1][1],
                                                        'name':record[1][0],
                                                        'epsgCode':self.expEPSG,
                                                        'mapUnits':self.mapunits})
         except:
            message = 'Could not upload layer '+str(record[1][0])
            QMessageBox.warning(self,"status: ", message)
         else:
            layerId = postresponse.id
            upload = True
      else:
         index = names.index(record[1][0])
         layerId = ids[index]
         upload = True
      addresponse = False   
      try:   
         inputs = {'attrPresence':record[1][2],'minPresence':record[1][3],
                   'maxPresence':record[1][4], 'percentPresence':record[1][5]}
         # this adds the expId
         inputs.update(self.inputs) 
         inputs.update({'lyrId':layerId}) 
         addresponse = self.client.rad.addPALayer(**inputs)
         
      except:
         message = 'Could not add layer '+str(record[1][0]) +" to experiment"
         QMessageBox.warning(self,"status: ", message)
         success = False
      else:
         if upload and addresponse:
            success = True
         else:
            success = False                                                  
      
      return success
# ..............................................................................   
   def removeUploadedRows(self, successrecords, layercount, successcount):
      
      if layercount == successcount:
         # number of times to go through loop is layercount-1
         emptyrow = ['' for x in range(0,len(self.table.tableView.model().data[0]))]
         emptyrow[1] = 'start'
         for i in range(0,layercount-1):
            self.table.tableView.model().removeRow(successrecords[i][1])        
         self.table.tableView.model().data[0] = emptyrow  
         self.tableview.setEditTriggers(QAbstractItemView.NoEditTriggers)          
      elif successcount < layercount:
         # number of times to go through loop is everything in successrecords
         for oldrecord in successrecords:              
            self.table.tableView.model().removeRow(oldrecord[1])   
# ..............................................................................      
   def checkForEmpties(self):
      for record in self.table.tableView.model().data:
         for field in record:
            if field == '' or field == 'please select':
               return True
      return False   
# ..............................................................................       
   def accept(self):    
      empties = self.checkForEmpties()
      if empties:
         message = "There are empty fields in your data"
         QMessageBox.information(self,"error: ", message)
         return
      self.acceptBut.setEnabled(False)     
      self.statuslabel.setText('Uploading') 
      self.outputGroup.setTitle('Outputs')
      self.outputGroup.show()
      self.progressbar.reset()
      layercount = len(self.table.tableView.model().data)
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(layercount)
      names, ids, crsMatch = self.checkNamesCRS()    
      successcount = 0
      addedAndUploadedrecords = []
      progress = 0
      wrongCrsLyrNames = []
      for crs, record in zip(crsMatch,enumerate(self.table.tableView.model().data)):
         if record[1][0] not in names  and crs:
            if self.addUpload(names, ids, record, skipUpload=False):
               addedAndUploadedrecords.append(record)
               successcount += 1
         if not crs:
            wrongCrsLyrNames.append(record[1][0])
         progress +=1
         self.progressbar.setValue(progress)
      self.removeUploadedRows(addedAndUploadedrecords,layercount,successcount)            
      message = 'Uploaded and Added '+str(successcount) +" of "+ str(layercount) +" layers"
      QMessageBox.information(self,"status: ", message)
      
      if len(names) > 0:
         self.acceptBut.setEnabled(True)
         namesString = ''
         for layer in names:
            namesString = namesString + layer + '\n'
         message =  """The following layers already exist by name for this user,
                    if you wish to upload again click No on this dialog, rename 
                    the remaining layers and submit again, or click Yes to skip
                    uploading the actual data and just add the existing data for
                    these layers to the current experiment with the new parameters.""" + namesString
         
         reply = QMessageBox.question(self, 'Layers exist',
                                               message, QMessageBox.Yes | 
                                               QMessageBox.No, QMessageBox.No)
         if reply == QMessageBox.Yes:
            successcount = 0
            layercount = len(self.table.tableView.model().data)
            addedrecords = []
            self.progressbar.reset()
            self.progressbar.setMinimum(0)
            self.progressbar.setMaximum(layercount)
            for record in enumerate(self.table.tableView.model().data):
               if self.addUpload(names, ids, record, skipUpload=True):
                  addedrecords.append(record)
                  successcount += 1 
                  progress +=1
                  self.progressbar.setValue(progress)              
            self.removeUploadedRows(addedrecords,layercount,successcount)
            message = 'Added '+str(successcount) +" of "+ str(layercount) +" layers"
            QMessageBox.information(self,"status: ", message)
         if len(wrongCrsLyrNames) > 0:
            namesString = ''
            for layer in wrongCrsLyrNames:
               namesString = namesString + layer + '\n'
            message = """The following layers EPSG do not match the ESPG of the experiment, you will not
                         be able to upload them to this experiment.""" + namesString
            QMessageBox.warning(self, 'Layers CRS Wrong', message)
            
      self.acceptBut.setEnabled(True)
      self.outputGroup.hide()
      self.inputGroup.show()   
            
# ..............................................................................         
   def help(self):
      self.help = QWidget()
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('uploadLayers')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()    
      
 

if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   d = UploadDialog(None,client=client)
   #d = AdvancedAlgo()
   d.show()
   sys.exit(qApp.exec_())               
      
      
      
      
      
      
      
      