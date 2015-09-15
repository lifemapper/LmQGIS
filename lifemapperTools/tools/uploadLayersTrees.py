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
try: import simplejson as json
except: import json
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from LmClient.lmClientLib import LMClient
from lifemapperTools.tools.ui_uploadLyrsTrees import Ui_Dialog
from lifemapperTools.common.NwkToJSON import Parser
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GridConstructor
from LmCommon.common.lmconstants import OutputFormat #OutputFormat.GTIFF, OutputFormat.SHAPE

# .............................................................................

class UploadTreeDialog( _Controller, QDialog, Ui_Dialog):
   
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
      self.expId = inputs['expId']
      self.inputs = inputs  
      self.phylo = None
      self.leaves = {}
      self.workspace = Workspace(iface,self.client)
      self.workspaceDLoc = self.workspace.getWSforUser(self.client._cl.userId)
      _Controller.__init__(self, iface, BASE_URL=GridConstructor.BASE_URL, 
                           STATUS_URL=GridConstructor.STATUS_URL, 
                           REST_URL=GridConstructor.REST_URL,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, outputfunc=None, 
                           requestfunc=None, client=client )
      
      self.expEPSG = epsg
      if mapunits is not None:
         self.mapunits = mapunits
   # ................................................ 
   def showTreeFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" )  ### have to take this out when in QGIS
      filetypestr = "%s files (*.%s)" % ("newick", "nhx")
      fileDialog = QgsEncodingFileDialog( self, "Open File", dirName,filetypestr)
      fileDialog.setDefaultSuffix(  "nhx"  )
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
      fileDialog.setConfirmOverwrite( True )
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      self.treeLine.setText(str(filename[0]))
   # ................................................       
   def convertNewick(self):
      """
      @summary: converts a Newick file as D3 tree JSON and populates
      layers with with layer names from leaves
      """
      
      treePath = str(self.treeLine.text())
      if treePath == "":
         message = "Please supply a file name"
         msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok)  
      else:
         if os.path.exists(treePath):
            try:
               
              
               tree = open(treePath,'r').read()
               sh = Parser.from_string(tree)
               parser = Parser(sh)
               phyloDict,parentDicts = parser.parse()
               self.phylo = phyloDict
            except:
               # stop the progress bar
               pass
            else:
               
               self.lengthOfExistingData =  len(self.table.tableView.model().data)
               #print "starting len ",self.lengthOfExistingData
               self.namesInTable = []
               self.addNamesToTable(phyloDict)
               #print "no. of tips ",self.lengthOfExistingData
               self.inputGroup.setEnabled(True)
         else:
            pass
   # ................................................ 
   def setLyrPath(self,index):
      print index
   # ................................................      
   def addNamesToTable(self,clade): 
      # recurse to leaves 
      if "children" in clade:
         for child in clade["children"]:
            self.addNamesToTable(child)
      else:
         layername = clade["name"]
         self.table.tableView.model().insertRow(
                                                self.lengthOfExistingData,
                                                [layername,str(file),'','','','',self.lengthOfExistingData])
         self.lengthOfExistingData += 1
         self.namesInTable.append(layername)
         self.leaves[layername] = clade
   # ................................................   
   
   
   def addMtrxIdxToTree(self,leafname,mxidx):
      
      if self.phylo is not None:
         self.leaves[leafname]['mx'] = mxidx
      else:
         pass
   # ................................................       
   def processFolder(self,dirname):
      
      # if has a shapefile extension add it, if tif add it, no shx etc
      
      full = [os.path.join(dirname,f) for f in os.listdir(dirname)
               if os.path.isfile(os.path.join(dirname,f)) and
               (os.path.splitext(f)[1] == OutputFormat.GTIFF or
                os.path.splitext(f)[1] == OutputFormat.SHAPE) and
                os.path.splitext(os.path.basename(f))[0] in self.namesInTable]
      # get just lyr names from tree/table model
               
      basenames = [os.path.splitext(os.path.basename(f))[0] for f in full]
      
      namePath = dict(zip(basenames, full))     
      
      shpList = [os.path.splitext(os.path.basename(f))[0] 
                 for f in full if os.path.splitext(f)[1] == OutputFormat.SHAPE]
            
      tblData = self.table.tableView.model().data
      shpLoc = [namePath[rec[0]] for rec in tblData if rec[0] in shpList] 
               
      fields = self.getFields(shpLoc)
      
      self.table.tableView.model().fields = fields
      
      # now match them with the tree by loop through the data model for the table
      shpIdx = 0
      recordsToRemove = []
      for x, rec in enumerate(self.table.tableView.model().data):
         
         if namePath.has_key(rec[0]): # this check between tree and folder
            path = namePath[rec[0]]
            presenceindex = self.table.tableView.model().index(x,2)
            if os.path.splitext(os.path.basename(path))[1] == OutputFormat.SHAPE:
               self.table.tableView.model().setData(presenceindex,self.table.tableView.model().fields[shpIdx][0])
               shpIdx += 1
            else:
               index = self.table.tableView.model().index(x,2)
               index.model().skipComboinRow.append(x)
               self.table.tableView.model().setData(presenceindex,'pixel') 
            pathIndex = self.table.tableView.model().index(x,1)
            self.table.tableView.model().setData(pathIndex,path)
         else:
            index = self.table.tableView.model().index(x,2)
            index.model().skipComboinRow.append(x)
            self.table.tableView.selectionModel().select(index,QItemSelectionModel.Select|QItemSelectionModel.Rows)
            recordsToRemove.append(rec)
            
            
      self.removeRecords()
      self.tableview.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
      #print full
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
            # this is where I need to add mx key to the phylo dictionary
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
      mtrxIdx = 0
      for crs, record in zip(crsMatch,enumerate(self.table.tableView.model().data)):
         if crs:
            if record[1][0] in names: skip = True
            else: skip = False
            if self.addUpload(names, ids, record, skipUpload=skip):
               addedAndUploadedrecords.append(record)
               self.addMtrxIdxToTree(record[1][0],mtrxIdx)
               mtrxIdx += 1
               successcount += 1
         if not crs:
            wrongCrsLyrNames.append(record[1][0])
         progress +=1
         self.progressbar.setValue(progress)
      self.removeUploadedRows(addedAndUploadedrecords,layercount,successcount)            
      
      message = 'Added '+str(successcount) +" of "+ str(layercount) +" layers"
      QMessageBox.information(self,"status: ", message)
      if len(wrongCrsLyrNames) > 0:
         namesString = ''
         for layer in wrongCrsLyrNames:
            namesString = namesString + layer + '\n'
         message = """The following layers EPSG do not match the ESPG of the experiment, you will not
                      be able to upload them to this experiment.""" + namesString
         QMessageBox.warning(self, 'Layers CRS Wrong', message)
      
      postedTree = self.postTree()
      #wroteTreeLocally = self.writeTree()
            
      self.acceptBut.setEnabled(True)
      self.outputGroup.hide()
      self.inputGroup.show()   
# ..............................................................................
   def postTree(self):
      try:
         resp = self.client.rad.addTreeForExperiment(self.expId, jTree=self.phylo)
      except:
         post = False
      else:
         post = resp
# ..............................................................................
   def writeTree(self):
      treeDir = self.workspace.getTreeFolder(self.expId)
      if not treeDir:
         treeDir = self.workspace.createTreeFolder(self.expId)
      if treeDir:
         try:
            with open(os.path.join(treeDir,'tree.json'),'w') as f:
               f.write(json.dumps(self.phylo,sort_keys=True, indent=4)) 
         except:
            wrote = False
         else:
            wrote = True
      else:
         wrote = False
      return wrote
         
               
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
      helpDialog.scrollToAnchor('uploadLayersTrees')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()    
      
 

if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   d = UploadTreeDialog(None,client=client,epsg='4326',inputs={'expId':2323423423})
   #d = AdvancedAlgo()
   d.show()
   sys.exit(qApp.exec_())               
      
      
      
      
      
      
      
      