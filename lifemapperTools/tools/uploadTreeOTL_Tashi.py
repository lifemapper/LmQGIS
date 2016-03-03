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
import csv
try: import simplejson as json
except: import json
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal,ogr
import numpy as np
import struct
from LmClient.lmClientLib import LMClient
from lifemapperTools.tools.ui_upLoadOTL import Ui_Dialog
from lifemapperTools.common.NwkToJSON import Parser
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.common.lmListModel import LmListModel
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GridConstructor
from LmCommon.common.lmconstants import OutputFormat #RASTER_EXTENSION, SHAPE_EXTENSION

# ............................................................................
class OTTSearchModel(LmListModel):
   """
   @summary: subclass of LmListModel that overrides data
   """
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
         if index.row() == 1 and self.model:
            return "build new model"
         else:
            return self.listData[index.row()].customData()
      if index.isValid() and role == Qt.UserRole:
         return self.listData[index.row()].ottId  
      else:
         return

class OTTSearchResult(object):
   """
   @summary: data structure for json search result from ott
   """
   def __init__(self,hintDict):
      try:
         self.ottId = hintDict["ot:ottId"]
         self.name = hintDict["unique_name"]
      except Exception, e:
         self.ottId = '-999'
         self.name = 'test'
      
   def customData(self):      
      """
      @summary: Creates a string representation of the TreeSearchResult 
                   object
      """
      return "%s" % (self.name) 
# .............................................................................

class EnterTextEventHandler(QObject):
  
   def __init__(self,control,model,extraControl=None):
      super(EnterTextEventHandler, self).__init__()
      self.control = control
      self.model = model
      self.extraControl = extraControl
      
      
   def eventFilter(self,object,event):
      
      if event.type() == QEvent.FocusIn:
         self.model.updateList([])
         self.control.setCurrentIndex(0)
         if self.extraControl is not None:
            self.extraControl.setEnabled(False)

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
      self.setModels()
      self.setEventHandlers()
      self.otlNewick = None
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
   
   def onTextChange(self, text):
      
      #print text
      displayName = text
      noChars = len(displayName)
      
      if text == '':
         self.searchAuto.clear()
      if noChars >= 3:
         currentIdx = self.searchAuto.currentIndex()
         if currentIdx == -1:
            #self.searchAuto.setCurrentIndex(0)
            pass
      
      if ("(" not in text and ")" not in text):
         self.searchOTT(str(text))
     
   def otlHint(self, query):
     
      res = self.client.otl.getOTLHint(query)      
      return res
   # ................................................  
   def getOTLTreeWeb(self,ottId):
            
      res = self.client.otl.getOTLTreeWeb(ottId)    
      return res

   # ................................................  
   def searchOTT(self, searchText = ''):
      self.otlNewick = None  # maybe put this in get Tree
      try:
         #hintJSON = self.client.rad.otlHint(searchText)
         hintJSON = self.otlHint(searchText)
      except Exception, e:
         #print "no request ",str(e)
         pass
      else:
         
         hintLsDict = json.loads(str(hintJSON))
         if len(hintLsDict) > 0:
            #print hintLsDict
            items = [OTTSearchResult(hitDict) for hitDict in hintLsDict]
         else:
            items = [OTTSearchResult({"ot:ottId":'-999',"unique_name":""})]
         self.ottListModel.updateList(items)
   # ................................................      
   def setModels(self):
      self.ottListModel = OTTSearchModel([OTTSearchResult({"ot:ottId":'-999',"unique_name":""})],self)
      self.searchAuto.setModel(self.ottListModel)
   # ................................................   
   def setEventHandlers(self):
            
      # removed back space handler Sept.3, 2015
      self.userEnters = EnterTextEventHandler(self.searchAuto,self.ottListModel,
                                              extraControl=self.convertOTLTreeBut)         
      
   # ................................................
   def getOTLTree(self):
      # get the ott id from current idx
      self.searchAuto.clearFocus()
      currentIdx = self.searchAuto.currentIndex()
      ottId = str(self.ottListModel.listData[currentIdx].ottId)
      
      if (ottId != "" and ottId != "-999"):
         try:
            treejson = self.getOTLTreeWeb(ottId)
         except Exception, e:
            #print str(e)
            pass
         else:
            treeDict = json.loads(str(treejson))
            self.convertOTLTreeBut.setEnabled(True)
            if treeDict.has_key("newick"):
               self.otlNewick = treeDict["newick"]
      else:
         #print "ottId from combo model ",ottId
         pass
   # ................................................     
   def convertOTLNewick(self):
      if self.otlNewick is not None:
         # convert to D3 tree json
         # recurse to leaves and take out, this type of thing on the end
         # _ott384299
         try:
            sh = Parser.from_string(self.otlNewick)
            parser = Parser(sh)
            phyloDict,parentDicts = parser.parse()
            #self.phylo = phyloDict
         except:
            message = "Couldn't Parse Tree"
            msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok) 
         else:
            
            self.lengthOfExistingData =  len(self.table.tableView.model().data)
            self.namesInTable = []
            self.addOTLNamesToTable(phyloDict)
            self.phylo = phyloDict
            self.inputGroup.setEnabled(True)                     
         
      else:
         message = "No Newick"
         msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok)      
   
   def addOTLNamesToTable(self,clade): 
      # recurse to leaves 
      if "children" in clade:
         for child in clade["children"]:
            self.addOTLNamesToTable(child)
      else:
         nameList = clade["name"].split("_")
         nameList.pop()
         clade["name"] = '_'.join(nameList)
         #   from regular add names to table
         layername = clade["name"]
         self.table.tableView.model().insertRow(
                                                self.lengthOfExistingData,
                                                [layername,str(file),'','','','',self.lengthOfExistingData])
         self.lengthOfExistingData += 1
         self.namesInTable.append(layername)
         self.leaves[layername] = clade
   
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
               #########################              
               #self.fullNames = fullLenNames
               #nameParts = [x.split('_') for x in fullLenNames]
               #justLast = [x[len(x)-2]+'_'+x[len(x)-1] for x in nameParts]
               #self.justLast = justLast                             
            except:
               # stop the progress bar
               message = "Couldn't Parse Tree"
               msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok) 
              
            else:
               self.phylo = phyloDict
               wroteTreeLocally = self.writeTree()
               print "WROTE TREE??? ",wroteTreeLocally
               self.lengthOfExistingData =  len(self.table.tableView.model().data)
               print "starting len ",self.lengthOfExistingData
               self.namesInTable = []
               self.addNamesToTable(phyloDict)
               print "no. Tips ",self.lengthOfExistingData
               self.inputGroup.setEnabled(True)
         else:
            message = "No Newick"
            msgBox = QMessageBox.information(self,
                                               "Problem...",
                                               message,
                                               QMessageBox.Ok)  
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
      
   def getOccSet(self, occSetId, path):
      u_pwd = [('tashitso','anamza348'),('TashiNew_March','TashiNew_March'),
               ('TashiFourSpecies','TashiFourSpecies'),('TashiTestMay','TashiTestMay')]
      success = False
      for user,pwd in u_pwd:
         client = LMClient()
         client.login(user,pwd)
         
         try:
            client.sdm.getOccurrenceSetShapefile(occSetId, filename=path, overwrite=True)
         except Exception, e:
            del client
            success = False
            #print "Exception in get Occurrence Set ",str(e)
         else:
            del client
            if os.path.exists(path):
               success = True
            else:
               print "path or owner is bad ",path
               success = False
            break
      return success
   # ................................................       
   def processFolder(self,dirname):
      """
      @summary: matches tips in tree to species in folder, called when Directory dialog
      is closed and has folder name
      """
      
      # build dict from composite csv
      csvPath = "/home/jcavner/TashiCSV/composite.csv"
      lr = list(csv.reader(open(csvPath,'r')))
      #modelInfo = {l[0]:{k:v  for k,v in zip(lr[0],l) } for l in lr[1:]}
      
      #### occurrences ####  Feb 2016
      import commands
      occDirectory = "/home/jcavner/Tashi_2016_Reanalysis/FinalOcc/FinalOcc1_13_16/shps/reprojected/"
      res = commands.getoutput('ls %s*.shp' % (occDirectory))  
      occs = res.split('\n')
      #######################
      
      self.acceptBut.setEnabled(True)
      # if has a shapefile extension add it, if tif add it, no shx etc
      
      full = [os.path.join(dirname,f) for f in os.listdir(dirname)
               if os.path.isfile(os.path.join(dirname,f)) and
               (os.path.splitext(f)[1] == OutputFormat.GTIFF or
                os.path.splitext(f)[1] == OutputFormat.SHAPE) and
                os.path.splitext(os.path.basename(f))[0] in self.namesInTable]
      
      notfull = [f for f in os.listdir(dirname) if os.path.splitext(os.path.basename(f))[0] 
                 not in self.namesInTable]
      notfull.sort()
      # get just lyr names from tree/table model
               
      basenames = [os.path.splitext(os.path.basename(f))[0] for f in full]
      
      namePath = dict(zip(basenames, full))   
      #print "NAMEAPTH"
      #print namePath  
      
      
      shpList = [os.path.splitext(os.path.basename(f))[0] 
                 for f in full if os.path.splitext(f)[1] == OutputFormat.SHAPE]
            
      tblData = self.table.tableView.model().data
      shpLoc = [namePath[rec[0]] for rec in tblData if rec[0] in shpList] 
               
      fields = self.getFields(shpLoc)
      
      self.table.tableView.model().fields = fields
      
      # now match them with the tree by loop through the data model for the table
      shpIdx = 0
      recordsToRemove = []
      ###########
      #import csv
      #csvH = open('/home/jcavner/BigTree3.csv','wb')
      #newFullNames = []
      
      ############
      matchedCount = 0
      nonMatched = 0
      nonMatchedL = []
      for x, rec in enumerate(self.table.tableView.model().data):
   
         if namePath.has_key(rec[0]): # commented out on Feb 2016 #and rec[0] in modelInfo: # this is a check between tree and folder, but needs a check
            # to see if name is in modelInfo Dict
            ############
            #NotPruneIdx = self.justLast.index(rec[0])
            #newFullNames.append([self.fullNames[NotPruneIdx]])
            ############
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
            # fill in indexes 3,4,5
            # now go to csv, model dict, for occurrencesetId? matched by name? retrieve occset using id, 
            # store in temp or workspace subfolder, get it's path and send path, and shp path to getthreshold
            # and populate threshold columns
            #occSetId = modelInfo[rec[0]]['occurrencesetid']
            dwnLdBase = "/home/jcavner/TashiShpDownloadedFromTree/"
            dwnLdBase = "/home/jcavner/Tashi_2016_Reanalysis/FinalOcc/FinalOcc1_13_16/shps/reprojected/" # Feb 2016
            shpPath = os.path.join(dwnLdBase,rec[0]+"_AEAC.shp")
            #occSetSuccess = self.getOccSet(occSetId,shpPath)
            #if occSetSuccess:
            #try:
            try:
               minT,maxT = self.getThreshold(path, shpPath, 5)
               if minT == '' or maxT == '':
                  raise Exception, "Threshold blank"
               #minIndex = self.table.tableView.model().index(x,3)
               #self.table.tableView.model().setData(minIndex,minT)
               #maxIndex = self.table.tableView.model().index(x,4)
               #self.table.tableView.model().setData(maxIndex,maxT)
               
            except Exception ,e:
               print "EXCEPTION IN THRESHOLD ",str(e)
               index = self.table.tableView.model().index(x,2)
               index.model().skipComboinRow.append(x)
               self.table.tableView.selectionModel().select(index,QItemSelectionModel.Select|QItemSelectionModel.Rows)
               recordsToRemove.append(rec)
            else:
               minIndex = self.table.tableView.model().index(x,3)
               self.table.tableView.model().setData(minIndex,minT)
               maxIndex = self.table.tableView.model().index(x,4)
               self.table.tableView.model().setData(maxIndex,maxT)
               matchedCount = matchedCount + 1
            #except Exception, e: 
            #else:
            #   print "couldn't get occ ",occSetId
            #   #print "EXCEPTION IN THRESHOLD ",str(e)
            #   index = self.table.tableView.model().index(x,2)
            #   index.model().skipComboinRow.append(x)
            #   self.table.tableView.selectionModel().select(index,QItemSelectionModel.Select|QItemSelectionModel.Rows)
            #   recordsToRemove.append(rec)
         else:
            #print rec[0],"  ",namePath.has_key(rec[0])," and ",rec[0] in modelInfo
            nonMatched = nonMatched + 1
            nonMatchedL.append(rec[0])
            index = self.table.tableView.model().index(x,2)
            index.model().skipComboinRow.append(x)
            self.table.tableView.selectionModel().select(index,QItemSelectionModel.Select|QItemSelectionModel.Rows)
            recordsToRemove.append(rec)
            
      ###############
      #wr = csv.writer(csvH,dialect='excel')
      #wr.writerows(newFullNames)
      #csvH.close()
      ################
      print "MATCHED ",matchedCount 
      print "NONMATCHED ",nonMatched 
      print len(notfull)
      print len(nonMatchedL) 
      nonMatchedL.sort() 
      for x in notfull:
         print x 
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
   def getThreshold(self,tifPath,shpPath,percentile):
      """
      @summary: given a given a GeoTiff and a shapefile return min and max thresholds
      as a percentile for lower threshold, and max for upper
      @param tifPath: full path to tiff
      @param shpPath: full path to shp
      @param percentile: percentile to return (integer)
      """
      
      tiffDs=gdal.Open(tifPath) 
      tO=tiffDs.GetGeoTransform()
      rb=tiffDs.GetRasterBand(1)
   
      RXSize = tiffDs.RasterXSize
      RYSize = tiffDs.RasterYSize
      
      sphDs=ogr.Open(shpPath)
      lyr=sphDs.GetLayer()
      
      pxValues = []
      for feat in lyr:
         geom = feat.GetGeometryRef()
         
         x,y = geom.GetX(), geom.GetY()  #coord in map units
         
         #Convert from map to pixel coordinates.
         px = int((x - tO[0]) / tO[1]) #x pixel
         py = int((y - tO[3]) / tO[5]) #y pixel
         
         if px >= 0 and px <= RXSize and py >= 0 and py <= RYSize:
            structval=rb.ReadRaster(px,py,1,1,buf_type=rb.DataType) 
            val = struct.unpack('f',structval)[0] 
            if val != rb.GetNoDataValue(): 
               pxValues.append(val) 
         
       
      return np.percentile(pxValues,percentile),max(pxValues)
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
      
      #postedTree = self.postTree()
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
      
      
      
      
      
      
      
      