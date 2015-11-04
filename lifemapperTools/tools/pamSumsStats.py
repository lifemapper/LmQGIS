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
import zipfile
import csv
import sys
import cPickle
import math
import json
from osgeo import ogr
from types import ListType
from random import randint
import numpy as np
from urllib2 import HTTPError
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from LmClient.lmClientLib import LMClient  
from lifemapperTools.tools.ui_PamSumsStatsDialog import Ui_Dialog
from lifemapperTools.tools.spatialStats import SpatialStatsDialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.tools.radTable import RADTable
from lifemapperTools.tools.treeWindow import TreeWindow
from lifemapperTools.common.colorpalette import ColorPalette
from lifemapperTools.common.matPlotLibPlotter import PlotWindow
from lifemapperTools.common.colorramps import HOTCOLD
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.common.communicate import Communicate
from lifemapperTools.common.classifyQgisLyr import Classify






class PamSumsStatsDialog(_Controller, QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, 
                parent=None, resume=False, expEPSG=None, gridName=None,
                origPamSumId = None, shpGrd = None):
      
      QDialog.__init__(self)
      self.client = client
      self.checkShowLinked = False
      self.expId = inputs['expId']
      self.bucketId = inputs['bucketId']
      self.gridName = gridName
      self.shpGrd = shpGrd
      self.setupUi()
      #self.setAttribute(Qt.WA_DeleteOnClose)
      self.interface = iface
      if resume:
         self.interface.addProject(resume)
      self.workspace = Workspace(self.interface,client)
      self.inputs = inputs
      self.statsTypes = {}
      self.buildStatsLookup()
      self.rampIndex = 0
      self.rampTypes = ['bluered','bluegreen','greenred']    
      self._availablestats = None
      self._expFolder = None
      self.StatsDialog = None
      self.expEPSG = expEPSG
      self.AddBut = None
      self.tableview = None
      self.treeDLoc = None
      self._origPamId = origPamSumId
      self.speciesOrSites = None
      self.activeLyr = None
      self.attachedNonFIDNonLyrId = False
      self.plot = None
      self.selectedFIDs = [] # running list of selected FIDs in the plot
      self.setSitesPresent()
      self.downLoadTree()
      linkedLyr = self.findLinkLyr()
      if linkedLyr:
         self.activeLyr = linkedLyr
      else:
         self.activeLyr = self.getGrid()
      _Controller.__init__(self, iface, BASE_URL=None, STATUS_URL=None, REST_URL=None,
                           ids=RADids,initializeWithData=False,
                           requestfunc=self.client.rad.listExperiments, 
                           client = client)
      
      Communicate.instance().setPamSumExist.emit(self)
   
   def showEvent(self,event):
      """fires only on show"""
      # use this to check for existence of linked layer appropriate for grid,
      # in case linked layer gets removed after a hide
      # if self.linked layer doesn't exist in contents, get again
      if self.checkShowLinked:
         if self.activeLyr:
            try:
               linkedLyr = self.activeLyr
               legend = self.interface.legendInterface()
               drawingOrderByName = [lyr.id() for lyr in legend.layers()]         
               if linkedLyr.id() in drawingOrderByName:            
                  if drawingOrderByName.index(linkedLyr.id()) != 0:               
                     mvdLyr = self.moveLyrToTop(linkedLyr)
                     self.activeLyr = mvdLyr
               else:
                  linkedLyr = self.findLinkLyr()
                  if linkedLyr:
                     self.activeLyr = linkedLyr
                  else:
                     self.activeLyr = self.getGrid()
            except Exception, e:
               linkedLyr = self.findLinkLyr()
               if linkedLyr:
                  self.activeLyr = linkedLyr
               else:
                  self.activeLyr = self.getGrid()
               
            
# ..............................................................................
   def buildStatsLookup(self):
      
      types = ['specieskeys' , 'siteskeys' , 'diversitykeys']
      statsType = {}
      for type in types:
         arguments = {}
         arguments.update(self.inputs)
         arguments.update({'pamSumId':'original'})
         arguments.update({'keys':type})
         try:
            keys = self.client.rad.getPamSumStatisticsKeys(**arguments)
         except:
            pass
         else:
            values = [type.replace('keys','') for x in range(0,len(keys))]          
            #d = {k:v for k,v in zip(keys,values)}
            d = dict(zip(keys,values))
            statsType.update(d)
      self.statsTypes.update(statsType)
       
# ..............................................................................
   def downLoadTree(self):
      """
      @summary: tries to download tree for an experiment
      """
      try:
         expId = self.expId
         treeFolder = self.workspace.getTreeFolder(expId)
         if treeFolder:
            filename = os.path.join(treeFolder,'tree.json')
            self.client.rad.getTreeForExperiment(expId,filename=filename)# filename=
         else:
            treeFolder = self.workspace.createTreeFolder(expId)
            if treeFolder:
               filename = os.path.join(treeFolder,'tree.json')
               if os.path.exists(treeFolder):                  
                  self.client.rad.getTreeForExperiment(expId,filename=filename)# filename=
               else:
                  raise Exception("invalid tree path")
            else:
               raise Exception("couln't create tree folder")
      except HTTPError,e:
         if e.code != 404:
            message = "Tree service not responding, only affects trees"
            msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok) 
      except Exception,e: 
         message = "Tree service not responding, only affects trees "+str(e)
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok) 
      else:
         self.treeDLoc = filename
         self.treeViewerBut.setEnabled(True)
         
         
         
# ..............................................................................
   def checkActiveLyrPlot(self,checked):
      """
      @deprecated: was used with manual linkage
      """
      if self.isModal():
         self.setModal(False)
      if checked:
         selectLyr = self.interface.mapCanvas().currentLayer()
         if not selectLyr:
            self.attachActiveLyr.setChecked(False)
            self.activeLyr = None
            message = "There is no active layer"
            self.msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok) 
         else:
            siteIdIdx = selectLyr.fieldNameIndex('siteid')
            if siteIdIdx == -1:
               self.attachActiveLyr.setChecked(False)
               self.activeLyr = None
               message = """The active layer does not have a siteid field, try downloading
                          a spatial view and making that layer active."""
               msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok) 
            else:
               self.activeLyr = selectLyr
               
               if self.tableview is not None:
                  if self.attachedNonFIDNonLyrId and self.speciesOrSites == 'sites':
                     # need to think about this,  what if a table exists and its from a splotch conflicting with
                     # original or swapped
                     self.scatterPlot.setEnabled(False)
                     self.buildTable()
                     self.scatterPlot.setEnabled(True) 
# ..............................................................................
   def setSitesPresent(self):     
      try:
         bucketId = self.inputs['bucketId']
         expId = self.expId
         # get the workspace and project folder
         filePath = os.path.join(self.saveDirectory,'sitesPresent.pkl')
         success = self.client.rad.getBucketSitesPresent(filePath, expId, bucketId)
         if os.path.exists(filePath) and success:
            presentDict = cPickle.load(open(filePath))
            self.sitesPresent = presentDict
            try:
               self.lyrsPresent = presentDict[int(bucketId)]['layersPresent']
            except:
               self.lyrsPresent = None
      except Exception,e:
         
         self.sitesPresent = None
         self.lyrsPresent = None
         

# ..............................................................................
   def disconnectAddPlotKeys(self,modelData,lenMatch=True):
      """
      @deprecated: signals it was disconnecting from don't exist anymore
      and doesn't make a hidden FID column, header
      """
      length = len(modelData)
      ids = [tableId for tableId in range(0,length)]
      for rec,tableId in zip(modelData,ids):
         rec.insert(0,tableId)
      #self.attachedNonFIDNonLyrId = True #was used with manual linkage
      if not lenMatch:
         message = """sites in layer do not match the number of stats records, 
                     unable to attach map, plot can still be built."""
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
# ..............................................................................
   def attachFIDs(self,modelData,pam=None):
      """
      @summary: attaches the FIDs from a current Layer given sites present to the 
      model data for the sites table
      """
     
      if self.activeLyr is not None:   
         bucketId = int(self.inputs['bucketId'])
         if pam is None:            
            sitesPresent = self.sitesPresent[bucketId]['sitesPresent'] # original            
         else:
            if int(pam) in self.sitesPresent: # this means it is splotched, since only
               # splotched ids are keys
               sitesPresent = self.sitesPresent[int(pam)]['sitesPresent']
            else:               
               sitesPresent = self.sitesPresent[bucketId]['sitesPresent']               
                       
         selectLyr = self.activeLyr
         siteIdIdx = selectLyr.fieldNameIndex('siteid')
         featuresIter = selectLyr.getFeatures()
         
         try:
            listofFIDs = [f.id() for f in featuresIter if sitesPresent[f.attributes()[siteIdIdx]]]  
         except Exception, e:
            
            length = len(modelData)
            ids = [tableId for tableId in range(0,length)]
            for rec,tableId in zip(modelData,ids):
               rec.insert(0,tableId)
            self.activeLyr = None
         else:
            if len(listofFIDs) == len(modelData):
               for rec,FID in zip(modelData,listofFIDs):
                  rec.insert(0,FID)
            else:               
               length = len(modelData)
               ids = [tableId for tableId in range(0,length)]
               for rec,tableId in zip(modelData,ids):
                  rec.insert(0,tableId)                              
               self.activeLyr = None
      else:
         length = len(modelData)
         ids = [tableId for tableId in range(0,length)]
         for rec,tableId in zip(modelData,ids):
            rec.insert(0,tableId)                              
         
         
            
         
# ..............................................................................
   def attachLyrIDs(self,modelData):
      """
      @summary: attaches the lyrIDs to the model data given the lyrs present
      @param modelData: lists of lists of table model data
      """
      lyrIds = [x for x,y in sorted(self.lyrsPresent.iteritems()) if y]
      for rec,lyrId in zip(modelData,lyrIds):
         rec.insert(0,lyrId)
# ..............................................................................
   def selectSpecies(self,speciesSelected,lyrIds,ctrl):
      pass
      
   # ..............................................................................
   def layerSelectionSlot(self, *args):
      try:
         selectedFIDs = args[0]
         deselectedFIDs = args[1]
      except:
         pass
      
      #print self.selectedFIDs
      
# ..............................................................................
   def selectSites(self,sitesSelected,fids,ctrl):      
      """
      @summary: connected to signal emitted in matplotlib, deprecated? works from inside the plot now
      @param sitesSelected: a one dimensional numpy array of booleans indicating if sites
      were selected, e.g. [True, True, False,...], returned in the order matching the order
      of the values in the table.
      @param fids: list of fids originally from the table
      @deprecated: works from inside the plot
      """
      
      sitesSelectedList = list(sitesSelected)
      #selectLyr = self.interface.mapCanvas().currentLayer()
      selectLyr = self.activeLyr
      if not ctrl:
         self.selectedFIDs = [fid for fid,selected in zip(fids,sitesSelectedList) if selected]   
         selectLyr.setSelectedFeatures(self.selectedFIDs) # using just select, gives the option of 
         # not emiting selectionChanged signal, in 2.0, setSelectedFeatures sends args to slot for
         # selectionChanged
      else:
         if len(self.selectedFIDs) > 0:
            added = [fid for fid,selected in zip(fids,sitesSelectedList) if selected]
            self.selectedFIDs = list(set(added + self.selectedFIDs))
            selectLyr.setSelectedFeatures(self.selectedFIDs)
         else:
            self.selectedFIDs = [fid for fid,selected in zip(fids,sitesSelectedList) if selected]   
            selectLyr.setSelectedFeatures(self.selectedFIDs) 


# ..............................................................................
   def getRandomizedPamSums(self, randomMethod = None):
      """@summary: retrieves the randomized pams for an experiment  and a grid
      """
      
      #  1-swap, 2-splotch
      args = {'randomized':1}
      if randomMethod is not None:
         args['randomMethod'] = randomMethod      
      args.update(self.inputs)
      try:
         
         randomPSList = self.client.rad.listPamSums(**args)
      except:
         message = "There is a problem with the pam listing service"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
         return False
      else:
         return randomPSList
         
# ..............................................................................
   def checkPamSelected(self):
      """
      @summary: event clicked handler for all pam radio buttons
      """
      if self.allRandomizedRadio.isChecked():     
         randomizedPamList = self.getRandomizedPamSums()  
         self.populatePamsCombo(randomizedPamList,pamtype = 'all')
      if self.swappedRadio.isChecked():
         swappedPamList = self.getRandomizedPamSums(randomMethod=1) 
         self.populatePamsCombo(swappedPamList,pamtype = 'swapped')
      if self.splotchedRadio.isChecked():
         splotchedPamList = self.getRandomizedPamSums(randomMethod=2) 
         self.populatePamsCombo(splotchedPamList,pamtype = 'splotched')
# ..............................................................................
   def checkBetaStatsSelected(self,checked):
      """
      @summary: is called with stats are toggled
      """
      if checked:
         allBetaStats = self.getAvailableBetaStats()
         self.populateStatsCombo(allBetaStats,statstype='beta') 
# ..............................................................................
   def checkSitesStatsSelected(self,checked):
      """
      @summary: is called with stats are toggled
      """
      if checked:
         allSitesstats = self.getAvailableSitesStats()
         self.populateStatsCombo(allSitesstats,statstype='sites')
         self.spatiallyView.setEnabled(True)
         self.attachActiveLyr.setEnabled(True)
      else:
         self.attachActiveLyr.setChecked(False)
         self.attachActiveLyr.setEnabled(False)
             
# ..............................................................................
   def checkSpeciesStatsSelected(self,checked):
      """
      @summary: is called with stats are toggled
      """
      if checked:
         allSpeciesstats = self.getAvailableSpeciesStats()      
         self.populateStatsCombo(allSpeciesstats,statstype='species')
         
# ..............................................................................
   def populateStatsCombo(self,stats,statstype='species'):
      self.statsCombo.clear()
      if statstype == 'sites':        
         self.statsCombo.addItem("All Site-based Stats",userData="allsite")
         for o in stats:
            self.statsCombo.addItem(o,userData=o)
            
      if statstype == 'species':        
         self.statsCombo.addItem("All Species-based Stats",userData="allspecies")
         for o in stats:
            self.statsCombo.addItem(o,userData=o)
            
      if statstype == 'beta':
         self.statsCombo.addItem("All Beta Stats",userData="allbetas")
         for o in stats:
            self.statsCombo.addItem(o,userData=o)
         
# ..............................................................................
   def populatePamsCombo(self, pamlist, pamtype='all'):
      """@summary: populates the pams combos
      """
      
      self.randomizedPams = []
      self.pamsumsCombo.clear()
      # add items for All pams, swapped pams, and splotched pams
      if pamtype == 'all':
         if pamlist:
            if len(pamlist) > 0:
               self.sitesStatsRadio.setEnabled(False)
               self.speciesStatsRadio.setEnabled(True)
               self.speciesStatsRadio.setChecked(True)
               self.pamsumsCombo.addItem("All",userData="allrandom")
               origPamId = self.origPamId
               if origPamId:
                  self.pamsumsCombo.addItem("original pam: id "+str(origPamId),userData=origPamId) 
            else:
               self.sitesStatsRadio.setEnabled(True)
               self.speciesStatsRadio.setEnabled(True)
               self.sitesStatsRadio.setChecked(True)
         else:
            origPamId = self.origPamId
            if origPamId:
               self.pamsumsCombo.addItem("original pam: id "+str(origPamId),userData=origPamId)
            self.sitesStatsRadio.setEnabled(True)
            self.speciesStatsRadio.setEnabled(True)
            self.sitesStatsRadio.setChecked(True)
      elif pamtype == 'swapped':
         if pamlist:
            if len(pamlist) > 0:
               self.sitesStatsRadio.setEnabled(True)
               self.speciesStatsRadio.setEnabled(True)
               self.sitesStatsRadio.setChecked(True)
               self.pamsumsCombo.addItem("All Swapped PAMs",userData="allswapped")
            else:
               return
         else:
            return
      elif pamtype == 'splotched':
         if pamlist:
            if len(pamlist) > 0:
               self.sitesStatsRadio.setEnabled(False)
               self.speciesStatsRadio.setEnabled(True)
               self.speciesStatsRadio.setChecked(True)
               self.pamsumsCombo.addItem("All Dye Dispersion PAMs",userData="allsplotched")
            else:
               return
         else:
            return
      if pamlist:  ### IS THERE ANY WAY THAT THIS WON"T HAPPEN?
         for o in pamlist:
            self.pamsumsCombo.addItem(o.title+": id "+str(o.id),userData=o.id)
            self.randomizedPams.append(o.id)
# ..............................................................................

   def getAvailableSpeciesStats(self):
      """
      @summary: builds a list of of available species based stats
      """
      availablestats = self.availablestats
      ################################      
      #keyinputs = {}
      #keyinputs.update(self.inputs)
      #keyinputs.update({'pamSumId':'original','keys':'specieskeys'})
      #try:
      #   keys = self.client.rad.getPamSumStatisticsKeys(**keyinputs)
      #except:
      #   availablestats = False
      #
      #################################  
      availablespecies = []
      if availablestats:      
         for stat in availablestats:
            if stat in self.statsTypes.keys():
               if (self.statsTypes[stat] == 'species') and ('sigma' not in stat)  and ('covariance' not in stat):
                  availablespecies.append(stat)          
      else:
         message = "There is a problem with the statistical service"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      return availablespecies  

# ..............................................................................
   def getAvailableSitesStats(self):
      """
      @summary: builds a list of available site based stats
      """
      
      availablestats = self.availablestats
      ###############################      
      #keyinputs = {}
      #keyinputs.update(self.inputs)
      #keyinputs.update({'pamSumId':'original','keys':'siteskeys'})
      #try:
      #   keys = self.client.rad.getPamSumStatisticsKeys(**keyinputs)
      #except:
      #   availablestats = False
      #
      ################################    
      availablesites = []
      if availablestats:
         for stat in availablestats:
            if stat in self.statsTypes.keys():
               if (self.statsTypes[stat] == 'sites') and ('sigma' not in stat) and ('covariance' not in stat):
                  availablesites.append(stat)         
      else:
         message = "There is a problem with the statistical service"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      return availablesites    
# ..............................................................................
   def getAvailableBetaStats(self):
      """
      @summary: builds a list of available beta stats
      """
      
      availablestats = self.availablestats
      ###############################      
      #keyinputs = {}
      #keyinputs.update(self.inputs)
      #keyinputs.update({'pamSumId':'original','keys':'diversitykeys'})
      #try:
      #   keys = self.client.rad.getPamSumStatisticsKeys(**keyinputs)
      #except:
      #   availablestats = False
      #
      ################################              
      availablebeta = []
      if availablestats:
         for stat in availablestats:
            if stat in self.statsTypes.keys():
               if self.statsTypes[stat] == 'diversity':
                  availablebeta.append(stat)         
      else:
         message = "There is a problem with the statistical service"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      return availablebeta    
# ..............................................................................
   def setAvailableStats(self):
      statsinputs = {}
      statsinputs.update(self.inputs)
      statsinputs.update({'pamSumId':'original','stat':None})
      try:
         stats = self.client.rad.getPamSumStatistic(**statsinputs) 
      except:
         stats = False     
      self._availablestats = stats
# .............................................................................. 
   @property
   def saveDirectory(self):
      if self._expFolder is None:
         self._expFolder = self.workspace.getExpFolder(self.expId)
         if not self._expFolder:
            self._expFolder = self.workspace.createProjectFolder(self.expId) 
      return self._expFolder     
# .............................................................................. 
   @property
   def availablestats(self):
      if self._availablestats is None or self._availablestats == False:
         self.setAvailableStats()      
      return self._availablestats
   
# ..............................................................................
   @property
   def origPamId(self):
      """
      @summary: gets the original pam id and sets self._origPamId
      """
      if self._origPamId == None or self._origPamId == False:
         listPSargs = {'randomized':0}
         listPSargs.update(self.inputs)
         try:
            origPamList = self.client.rad.listPamSums(**listPSargs)            
         except:
            message = "There is a problem with the pam listing service"
            msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
            self._origPamId = False
         else:
            self._origPamId = int(origPamList[0].id)
      return self._origPamId
# .............................................................................
   def moveLyrToTop(self,lyr):
            
      root = QgsProject.instance().layerTreeRoot()            
      newLyr = QgsVectorLayer(lyr.source(),'linked layer','ogr')            
      lyrToDelete = root.findLayer(lyr.id()) # returns a QgsLayerTreeLayer
      root.removeChildNode(lyrToDelete)  
      # do I need to set either lyr or lyrToDelete to None?
      if self.addPrivateLinkLyr(newLyr):      
         return newLyr
      else:
         return None
# .............................................................................
   def findShpForBucket(self, lyrList, fromLinkedLyr):
      """
      @summary: finds shapenames from previously downloaded zip archives,
      looking specifically for a shapename used as a lyr.source() (in the canvas)
      that fits the bucket
      """
      expId = self.expId
      bucketId = self.bucketId
      origPamId = str(self.origPamId)
      gridName = self.gridName
      workspace = self.saveDirectory
      pathname = False
      if not fromLinkedLyr:
         # this is for stat lyrs
         if not pathname:
            # check for old style pam (stat) (original pamsum) zip
            if os.path.isfile(os.path.join(workspace,origPamId)):
               pathname = os.path.join(workspace,origPamId)
         if not pathname:
            # check for new style pam (stat) (original pamsum) zip
            newStyleZipName = "%s_%s_%s" % (expId,bucketId,origPamId)
            if os.path.isfile(os.path.join(workspace,newStyleZipName)):
               pathname = os.path.join(workspace,newStyleZipName)
         ##########################################################
         
         if pathname:
            try: # just in case it's not a zip
               z = zipfile.ZipFile(str(pathname),'r')
               names = z.namelist()
               base = os.path.splitext(names[0])[0]
               shpName = "%s.shp" % (base)
            except:
               lyr = False
            else:
               lyr = False
               for l in lyrList:
                  src = l.source()
                  if shpName in src:
                     lyr = l
                     break                                             
         else:
            lyr = False
      else: # Grid Based 'linked layer'
         lyr = False
         for l in lyrList:
            src = l.source()
            if gridName in src:
               lyr = l
               break
      return lyr   
#..............................................................................
   def matchLnkWithShpGrd(self,lyrList):
      
      if self.shpGrd is not None:        
         
         sgminX = float(self.shpGrd.minX)
         sgminY = float(self.shpGrd.minY)
         sgmaxX = float(self.shpGrd.maxX)
         sgmaxY = float(self.shpGrd.maxY)
         
         sgExtent = (sgminX,sgmaxX,sgminY,sgmaxY)
         
         sgFc = int(self.shpGrd.featureCount)
         
         try:
            sgres = float(self.shpGrd.resolution)
         except:
            try:
               sgres = float(self.shpGrd.cellsize)
            except:
               return False
         n = float(self.shpGrd.cellsides)
         
         if n == 6:
            R = .5 * sgres  # circumRadius because resolution on a hex
            # shapgrid is vertex to vertex
            asg = .5*n*(R**2)*math.sin((2*math.pi/n))
         elif n == 4:
            asg = sgres * sgres
         
         sgT = (float("%.2f" % (asg)),sgFc,n)
         matched = False
         for lyr in lyrList:
            
            h = ogr.Open(lyr.source())
            ol = h.GetLayer(0)
            oExtent = ol.GetExtent()           
            f = ol.GetNextFeature()
            gR = f.GetGeometryRef()      
            gJson = gR.ExportToJson()   
            gJDict = json.loads(gJson)  
            numVert = len(gJDict['coordinates'][0]) - 1
            oArea = gR.Area()
            oFc = ol.GetFeatureCount()
            oT = (float("%.2f" % (oArea)),oFc,numVert)
            #if lyr.name() == 'linked layer':
            if oT == sgT:
               matched = True
               break
         if matched:
            return lyr
         else:
            return False
      else:
         return False
                   
                  
# ..............................................................................
   def changeDrawingOrder(self, layer):
      # changed this to use id rather than name
      mvdLyr = False
      legend = self.interface.legendInterface()
      drawingOrderByName = [lyr.id() for lyr in legend.layers()]         
      if layer.id() in drawingOrderByName:            
         if drawingOrderByName.index(layer.id()) != 0:               
            mvdLyr = self.moveLyrToTop(layer)
      return mvdLyr
# ..............................................................................
   def findLinkLyr(self):
      
      
      linkLyr = False
      mLRi = QgsMapLayerRegistry.instance() 
      possibleLyrs = ['linked layer','Species Richness','Mean Proportional Range Size',
                  'Proportional Species Diversity','Per-site Range Size of a Locality']
      
      statsList = []
      for lyrName in possibleLyrs:
         statLyr = mLRi.mapLayersByName(lyrName) # returns a list
         statsList.extend(statLyr) 
      if len(statsList) > 0:
            
            matchedLyr = self.matchLnkWithShpGrd(statsList)
            if matchedLyr:
               if matchedLyr.name() != 'linked layer':          
                  statSrc = matchedLyr.source()
                  linkLyr = QgsVectorLayer(statSrc,'linked layer','ogr')
                  if linkLyr.isValid():
                     if not self.addPrivateLinkLyr(linkLyr): 
                        linkLyr = False
                  else:
                     linkLyr = False 
               else:
                  
                  mvdLyr = self.changeDrawingOrder(matchedLyr)
                  if mvdLyr:
                     linkLyr = mvdLyr
                  else:
                     self.interface.setActiveLayer(matchedLyr)
                     linkLyr = matchedLyr
      return linkLyr
# ..............................................................................

# ............................................................................      
   def addPrivateLinkLyr(self, vL):
      """
      @summary: adds vL to to map registry, finds the layer tree root and inserts
      at the top
      @param vL: QgsVectorLayer, shapegrid without pam or statistics
      """
      try:
         mLRi = QgsMapLayerRegistry.instance()
         root = QgsProject.instance().layerTreeRoot()
         mLRi.addMapLayer(vL,False)
         vL.rendererV2().symbol().setAlpha(0)
         root.insertLayer(0,vL)
         self.interface.setActiveLayer(vL)  # making it active just helps with map selection
      except:
         return False
      else:
         return True

# ..............................................................................
   def getGrid(self):
      # gets an empty grid and makes it transparent for selection
      
      expFolder = self.saveDirectory
      gridZipName = "%s_%s" % (str(self.expId),str(self.bucketId))
      pathname = os.path.join(expFolder,gridZipName)
      try:        
         success = self.client.rad.getBucketShapegridData(pathname, str(self.expId), 
                                          str(self.bucketId),intersected=False)    
      except:
         vL = None
      else:
         if success:
            try:
               ###################################
               mLRi = QgsMapLayerRegistry.instance()
               root = QgsProject.instance().layerTreeRoot()
               ####################################
               zippath = os.path.dirname(str(pathname))                         
               z = zipfile.ZipFile(str(pathname),'r')
               for name in z.namelist():
                  f,e = os.path.splitext(name)
                  if e == '.shp':
                     shapename = name
                  z.extract(name,str(zippath))
               vectorpath = os.path.join(zippath,shapename)
               vL = QgsVectorLayer(vectorpath,'linked layer','ogr')
                           
               ####################################
               if not vL.isValid():
                  raise
               else:
                  #####################################
                  if not self.addPrivateLinkLyr(vL):
                     raise                           
            except:
               vL = None
         else:
            vL = None
      return vL
           
   
# ..............................................................................
   def buildSpatialView(self):
      
      if self.isModal():
         self.setModal(False)
      if self.tableview is not None:
         self.tableview.hide()
      self.tableLabel.setText('')
      self.exportStatsBut.setEnabled(False)
      self.scatterPlot.setEnabled(False)
      self.outputGroup.show()
     
      
# ..............................................................................      
   def openFileDialog(self,defaultfilename):
      #settings = QSettings()
      #shpPath = settings.value( "/UI/lastShapefileDir" )
      #if not os.path.exists(shpPath):
      #   shpPath = settings.value("UI/lastProjectDir")     
      #dirName = shpPath +"/"+defaultfilename.replace(' ','_')
      expFolder = self.saveDirectory
      dirName = os.path.join(expFolder,defaultfilename)
      fileDialog = QgsEncodingFileDialog( self, "Save .csv File", dirName,"csv Files (*.csv)")
      fileDialog.setDefaultSuffix(  "csv"  )
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )    
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return None
      filename = fileDialog.selectedFiles() 
      return str(filename[0])
# ..............................................................................
   def exportStats(self):
      filename = self.openFileDialog('stats')
      if filename is not None:
         data = self.tableview.model().data
         with open(filename, 'wb') as csvfile:
            statwriter = csv.writer(csvfile, delimiter=',')
            header = self.tableview.model().headerdata
            fields = [x.replace(' ','') for x in header]
            statwriter.writerow(fields)
            for row in data:
               statwriter.writerow(row)
      
# ..............................................................................
   def checkPamSumNotAll(self, index):
      # if all radio or dye radio
      if self.allRandomizedRadio.isChecked() or self.splotchedRadio.isChecked():
         if index != -1: 
            if index != 0:
               self.sitesStatsRadio.setEnabled(True)
            if index == 0:
               self.speciesStatsRadio.setChecked(True)
               self.sitesStatsRadio.setEnabled(False)
         
      
# ..............................................................................
   def buildTable(self):
      """
      @summary: makes calls to specific builders for tables depending on different
      combinations of stats and pam combo inputs
      """
      if self.isModal():
         self.setModal(False)
      currentPamidx = self.pamsumsCombo.currentIndex()
      pam = str(self.pamsumsCombo.itemData(currentPamidx, role=Qt.UserRole))
      currentStatidx = self.statsCombo.currentIndex()
      stat = str(self.statsCombo.itemData(currentStatidx, role=Qt.UserRole))
      if stat == '' or pam == '' or stat == 'None' or pam == 'None':
         message = "Choose a pam and a stat from the drop down lists, after using the radio buttons to narrow the lists"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      else:
         if self.availablestats:
            self.outputGroup.hide()
            if pam == 'allrandom':
               if stat == 'allbetas':
                  self.buildDiversityBasedTable(stat)
               elif self.statsTypes.has_key(stat):
                  if self.statsTypes[stat] == 'diversity':
                     self.buildDiversityBasedTable(stat)
               else:
                  self.buildSpeciesBasedTable(stat)
            elif pam == 'allsplotched':
               if stat == 'allbetas':
                  self.buildDiversityBasedTable(stat)
               elif self.statsTypes.has_key(stat):
                  if self.statsTypes[stat] == 'diversity':
                     self.buildDiversityBasedTable(stat)
               else:
                  self.buildSpeciesBasedTable(stat)
            elif pam == 'allswapped':
               if stat == 'allsite':
                  self.buildSitesBasedTable(stat)
               elif stat == 'allspecies':
                  self.buildSpeciesBasedTable(stat)
               elif stat == 'allbetas':
                  self.buildDiversityBasedTable(stat)
               else: # individual stat
                  if stat in self.statsTypes.keys():
                     if self.statsTypes[stat] == 'species':
                        self.buildSpeciesBasedTable(stat)
                  if stat in self.statsTypes.keys():
                     if self.statsTypes[stat] == 'sites':
                        self.buildSitesBasedTable(stat)
                  if stat in self.statsTypes.keys():
                     if self.statsTypes[stat] == 'diversity':
                        self.buildDiversityBasedTable(stat)
            else: # original or individual pam with id
               if stat == 'allsite':
                  self.buildSitesBasedTable(stat, pam=pam)
               elif stat == 'allspecies':
                  
                  self.buildSpeciesBasedTable(stat, pam=pam)
               elif stat == 'allbetas':
                  self.buildDiversityBasedTable(stat, pam=pam)
               else:
                  # individual stat
                  if stat in self.statsTypes.keys():
                     if self.statsTypes[stat] == 'species':
                        self.buildSpeciesBasedTable(stat, pam=pam)
                  if stat in self.statsTypes.keys():
                     if self.statsTypes[stat] == 'sites':
                        self.buildSitesBasedTable(stat, pam=pam)
                  if stat in self.statsTypes.keys():
                     if self.statsTypes[stat] == 'diversity':
                        self.buildDiversityBasedTable(stat, pam=pam)
         
   def getData(self, pam, stat):
      """
      @summary: this returns a column (with respect to the table) for a stat for
      a pam
      """
      args = {}
      args.update(self.inputs)
      args.update({'pamSumId':pam})
      args.update({'stat':stat})
      try:
         stats = self.client.rad.getPamSumStatistic(**args)      
      except:
         return False
      else:
         return stats
# ..............................................................................
   def clearTableLayout(self):
      while self.tableLayout.count():
            item =  self.tableLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
               widget.deleteLater()
# ..............................................................................
            
   def buildDiversityBasedTable(self, statistic, pam=None):
      self.tableLabel.setText("Beta-Diversity stats table: each row is a diversity index, each column a pam")
      self.speciesOrSites = 'beta'
      if pam is not None: # build a table for one pam   
         header = ['Beta Stat']
         data = []
         if statistic == 'allbetas':
            for stat in self.getAvailableBetaStats():
               header.append("pam "+str(pam))
               v = [stat,self.getData(pam,stat)]
               if not v:
                  v = [stat,'']
               data.append(v)
            modelData = data
         else: # individual stat
            header.append("pam "+str(pam))
            v = [statistic,self.getData(pam,statistic)]
            if not v:
               v = [statistic,'']
            data.append(v)
            modelData = data
         
      else: # build a table for all pams in self.randomizedPams + original
         header = ['Beta Stat']
         data = []
         allPams = list(self.randomizedPams) # makes a copy
         allPams.insert(0,self.origPamId)
         #allPams.insert(0,'original')
         if statistic == 'allbetas': 
            for stat in self.getAvailableBetaStats():
               v = [stat]
               for pam in allPams:
                  header.append("pam "+str(pam))
                  d = self.getData(pam,stat)
                  if not d:
                     d = ''
                  v.append(d)                 
               data.append(v)
            modelData = data
         else: # individual stat
            v = [statistic]
            for pam in allPams:
               header.append("pam "+str(pam))
               d = self.getData(pam,statistic)
               if not d:
                  d = ''
               v.append(d)
            data.append(v)
            modelData = data
            
      if self.tableview is not None:
         self.tableview.clearSelection()
         self.clearTableLayout()
         #self.gridLayout.removeWidget(self.tableview)
      try:
         a = np.array(modelData)
         if len(a.shape) != 2:
            modelData = [['Not All Pams have been randomized']]
         self.table =  RADTable(modelData)
         self.tableview = self.table.createTable(header)
         self.tableview.setSelectionBehavior(QAbstractItemView.SelectColumns)# ? 
         self.tableLayout.addWidget(self.tableview)
         self.exportStatsBut.setEnabled(True)
         self.scatterPlot.setEnabled(True)           
      except:
         pass    
      
   #def appendNewStats(self, header, reversedata):
   #   from csv import reader
   #   basePath = '/home/jcavner/AfricaCovarianceTest'
   #   ss_td_mntd_reader = reader(open(os.path.join(basePath,'ss_td_mntd_pearson.csv')),delimiter=',')
   #   rad_reader = reader(open(os.path.join(basePath,'rad.csv')),delimiter=',')
   #   ss_tdLL = list(ss_td_mntd_reader)[1:] 
   #   radLL = list(rad_reader)[1:]
   #   temprad = list(radLL)
   #   idxToRemove = [i for i,site in enumerate(temprad) if site[3] == '']   
   #   tempss = list(ss_tdLL)  
   #   ss_tdLL = [site for site in tempss if tempss.index(site) not in idxToRemove]
   #   tempArray = np.array(ss_tdLL)
   #   mntdCol = tempArray[:,2]
   #   ss_td_pCol = tempArray[:,3]
   #   mntdA = map(float,map(lambda x: x.replace(' ',''),mntdCol)) 
   #   ss_td_pA = map(float,map(lambda x: x.replace(' ',''),ss_td_pCol))
   #   mntd = mntdA
   #   ss_td_p = ss_td_pA
   #   reversedata.append(mntd)
   #   reversedata.append(ss_td_p)
   #   header.append('mntd')
   #   header.append('ss_td_p')
                  
# ..............................................................................
   def buildSitesBasedTable(self, statistic, pam=None):
      
      self.tableLabel.setText("Sites-Based stats table: each row is a geographic site in the pam, each column is a pam's stat")
      self.speciesOrSites = 'sites'
      if pam is not None: # build a table for one pam   
         header = []
         reversedata = []
         if statistic == 'allsite':
            for stat in self.getAvailableSitesStats():
               header.append('  %s id %s  ' % (stat,pam))
               v = self.getData(pam,stat)
               if not v:
                  v = ['']
               reversedata.append(v)
            
            #if int(self.expId) == 501:
            #   self.appendNewStats(header,reversedata)
            
            reverseArray = np.array(reversedata)
            transposeArray = reverseArray.transpose()
            modelData = transposeArray.tolist()
            
         else: # individual stat
            header.append('  %s id %s  ' % (statistic,pam))
            v = self.getData(pam,statistic)
            if not v:
               v = ['']
            reversedata.append(v)
            reverseArray = np.array(reversedata)
            transposeArray = reverseArray.transpose()
            modelData = transposeArray.tolist()
         
      else: # build a table for all pams in self.randomizedPams + original
         header = []
         reversedata = []
         allPams = list(self.randomizedPams)
         allPams.insert(0,self.origPamId)
         #allPams.insert(0,'original')
         if statistic == 'allsite': 
            for stat in self.getAvailableSitesStats():
               for pam in allPams:
                  header.append('  %s id %s  ' % (stat,pam))
                  v = self.getData(pam,stat)
                  if not v:
                     v = ['']
                  elif type(v) is not ListType:
                     v = [v]
                  reversedata.append(v)
            reverseArray = np.array(reversedata)
            transposeArray = reverseArray.transpose()
            modelData = transposeArray.tolist()
         else: # individual stat
            for pam in allPams:
               header.append('  %s id %s  ' % (statistic,pam))
               v = self.getData(pam,statistic)
               if not v:
                  v = ['']
               elif type(v) is not ListType:
                  v = [v]
               reversedata.append(v)
            reverseArray = np.array(reversedata)
            transposeArray = reverseArray.transpose()
            modelData = transposeArray.tolist()
            
      if self.sitesPresent is not None:         
         self.attachFIDs(modelData,pam=pam)
         header.insert(0,'FID')   
         hiddenColumns = [0]            
      else:  
         length = len(modelData)
         ids = [tableId for tableId in range(0,length)]
         for rec,tableId in zip(modelData,ids):
            rec.insert(0,tableId)
         header.insert(0,'FID')   
         hiddenColumns = [0]
         
      if self.tableview is not None:
         
         self.tableview.clearSelection()
         self.clearTableLayout()
         
      try:         
         a = np.array(modelData)         
         if len(a.shape) != 2:
            modelData = [['Not All Pams have been randomized']]
         self.table =  RADTable(modelData)         
         self.tableview = self.table.createTable(header,hiddencolumns=hiddenColumns)         
         self.tableview.setSelectionBehavior(QAbstractItemView.SelectColumns)# ?          
         self.tableLayout.addWidget(self.tableview)         
         self.exportStatsBut.setEnabled(True)
         self.scatterPlot.setEnabled(True)         
      except Exception, e:
         pass
   
   def buildSpeciesBasedTable(self, statistic, pam=None):
      self.tableLabel.setText("Species-Based stats table: each row is a species in the pam, each column is a pam's stat")
      self.speciesOrSites = 'species'
      if pam is not None: # build a table for one pam   
         header = []
         reversedata = []
         if statistic == 'allspecies':
            for stat in self.getAvailableSpeciesStats():
               header.append('  %s id %s  ' % (stat,pam))
               v = self.getData(pam,stat)
               if not v:
                  v = ['']
               elif type(v) is not ListType:
                  v = [v]
               reversedata.append(v)
         else: # individual stat
            header.append('  %s id %s  ' % (statistic,pam))
            v = self.getData(pam,statistic)
            if not v:
               v = ['']
            elif type(v) is not ListType:
               v = [v]
            reversedata.append(v)
         reverseArray = np.array(reversedata)
         transposeArray = reverseArray.transpose()
         modelData = transposeArray.tolist()        
      else: # build a table for all pams in self.randomizedPams + original
         header = []
         reversedata = []
         allPams = list(self.randomizedPams)
         allPams.insert(0,self.origPamId)
         if statistic == 'allspecies':           
            for stat in self.getAvailableSpeciesStats():
               for pam in allPams:
                  header.append('  %s id %s  ' % (stat,pam))
                  v = self.getData(pam,stat)
                  if not v:
                     v = ['']
                  elif type(v) is not ListType:
                     v = [v]
                  reversedata.append(v)
         else: # individual stat
            for pam in allPams:
               header.append('  %s id %s  ' % (statistic,pam))
               v = self.getData(pam,statistic)
               if not v:
                  v = ['']
               elif type(v) is not ListType:
                  v = [v]
               reversedata.append(v)
         reverseArray = np.array(reversedata)
         transposeArray = reverseArray.transpose()
         modelData = transposeArray.tolist()
      if self.lyrsPresent is not None:
         self.attachLyrIDs(modelData)
         header.insert(0,'FID')   
         hiddenColumns = [0]   
      else:
         length = len(modelData)
         ids = [tableId for tableId in range(0,length)]
         for rec,tableId in zip(modelData,ids):
            rec.insert(0,tableId)
         header.insert(0,'FID')   
         hiddenColumns = [0]        
      if self.tableview is not None:
         self.tableview.clearSelection()
         #self.gridLayout.removeWidget(self.tableview)
         self.clearTableLayout()
      try:
         a = np.array(modelData)
         if len(a.shape) != 2:
            modelData = [['Not All Pams have been randomized']]
         self.table =  RADTable(modelData)
         self.tableview = self.table.createTable(header,hiddencolumns=hiddenColumns)
         self.tableview.setSelectionBehavior(QAbstractItemView.SelectColumns)# ? 
         self.tableLayout.addWidget(self.tableview)
         self.exportStatsBut.setEnabled(True)
         self.scatterPlot.setEnabled(True)
      except:
         pass
         
   def buildScatterPlot(self):
      #self.setModal(False)
      try:
         selectedcolumns = self.tableview.selectionModel().selectedColumns()
         if len(selectedcolumns)!= 2:
            
            QMessageBox.warning(self,"status: ",
                            "Please select two columns from the table to plot")
            return
         
         if self.speciesOrSites == 'sites':
            self.createSitesPlot()
         elif self.speciesOrSites == 'species':
            self.createSpeciesPlot()
         elif self.speciesOrSites == 'beta':
            QMessageBox.warning(self,"status: ",
                            "scatter plots is only enabled for site or species based data")
      except Exception, e:
         
         QMessageBox.warning(self,"status: ",
                            "no data to plot "+str(e))
      
   def createSitesPlot(self):
      
      selectedcolumns = self.tableview.selectionModel().selectedColumns()
      if len(selectedcolumns)!= 2:
         
         QMessageBox.warning(self,"status: ",
                         "Please select two columns from the sites table") 
     
      else:    
         
         # check to make sure activeLyr is still at top of the draw list
         if self.activeLyr:
            mvdLyr = self.changeDrawingOrder(self.activeLyr)
            if mvdLyr:
               self.activeLyr = mvdLyr
            
            
         selectedcolindex0 = selectedcolumns[0].column()
         selectedcolindex1 = selectedcolumns[1].column()
         xLegend = self.tableview.model().headerdata[selectedcolindex0]
         yLegend = self.tableview.model().headerdata[selectedcolindex1]
         
         yvector = [float(row[selectedcolindex1]) for row in self.tableview.model().data]
         xvector = [float(row[selectedcolindex0]) for row in self.tableview.model().data]
         #if self.sitesPresent is not None and self.activeLyr is not None:
         fids = [int(row[0]) for row in self.tableview.model().data]
         activeLyr = self.activeLyr
         #else:
         #   fids = []
         #   activeLyr = self.activeLyr
         xs = np.array(xvector) 
         ys = np.array(yvector) 
         self.plot = PlotWindow(xs,ys,xLegend,yLegend,'Similarity of Sites',self.saveDirectory,
                                ids=fids,activeLyr=activeLyr,typePlot='Sites')
         self.plot.show()  
         self.plot.raise_()
         self.plot.activateWindow()    
           
# ..............................................................................
   def createSpeciesPlot(self):
      
      selectedcolumns = self.tableview.selectionModel().selectedColumns()
      if len(selectedcolumns)!= 2:
         
         QMessageBox.warning(self,"status: ",
                         "Please select two columns from the species table") 
     
      else:    
         selectedcolindex0 = selectedcolumns[0].column()
         selectedcolindex1 = selectedcolumns[1].column()
         xLegend = self.tableview.model().headerdata[selectedcolindex0]
         yLegend = self.tableview.model().headerdata[selectedcolindex1]                 
         yvector = [float(row[selectedcolindex1]) for row in self.tableview.model().data]
         xvector = [float(row[selectedcolindex0]) for row in self.tableview.model().data] 
         #if self.lyrsPresent is not None:
         lyrIds = [int(row[0]) for row in self.tableview.model().data]
         #else:
         #   lyrIds = []         
         xs = np.array(xvector) 
         ys = np.array(yvector)          
         self.plot = PlotWindow(xs,ys,xLegend,yLegend,'Species Association',self.saveDirectory,ids=lyrIds,activeLyr=self.activeLyr,typePlot='Species')
         self.plot.show()  
         self.plot.raise_()
         self.plot.activateWindow()
          
   
   def mapStats(self):
      currentPamidx = self.pamsumsCombo.currentIndex()
      pamsumid = str(self.pamsumsCombo.itemData(currentPamidx, role=Qt.UserRole))
      if pamsumid == 'allrandom' or pamsumid == 'allswapped' or pamsumid == 'allsplotched' or pamsumid == '' or pamsumid == 'None':
         message = "Please select a specific pam from the drop down list, using the radio button options to filter"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      
      else:       
         self.progressbar.setValue(0)    
         bucketid = self.inputs['bucketId']
         expid = self.expId
         self.addtoCanvas(pamsumid, bucketid, expid)
         self.progressbar.hide()
         self.mapItBut.show()
         #self.outEdit.clear()
         
   # .............................................................................
   def buildSetRenderer(self,lyr, fieldName, noClasses = None):
      
      cl = Classify(lyr)
      if noClasses == None:
         cl.noClasses = 8
      else:
         cl.noClasses = noClasses
      fieldIndex = lyr.fieldNameIndex(fieldName)     
      provider = lyr.dataProvider()     
      minimum = float(provider.minimumValue( fieldIndex ))
      maximum = float(provider.maximumValue( fieldIndex ))
      gT = cl.GEOMETRY_POLY
      ranges = cl.buildRanges(gT,minimum,maximum)
      renderer = cl.buildEqualIntervalRenderer(ranges,fieldName=fieldName)
      
      lyr.setRendererV2(renderer)
      
      return lyr
      
      
      
   # .............................................................................
   def classify(self, layer, fieldName):
      """
      @summary: auto classification for pamsum layers in map canvas using both old 
      and new renderers
      """
      # new style renderer
      numberOfClasses = 5
      if self.rampIndex >= len(self.rampTypes):
            self.rampIndex = 0
      colorramp = ColorPalette(ptype=self.rampTypes[self.rampIndex],n=numberOfClasses-1)
      self.rampIndex += 1
      #if layer.isUsingRendererV2():         
         # Get the field index based on the field name
      fieldIndex = layer.fieldNameIndex(fieldName)
      provider = layer.dataProvider()
      minimum = float(provider.minimumValue( fieldIndex ))
      maximum = float(provider.maximumValue( fieldIndex ))
      ranges = []       
      for i in range(0,numberOfClasses):
         red = colorramp[i][1] 
         green = colorramp[i][2]
         blue = colorramp[i][3]      
         color = QColor(red,green,blue)
         
         symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
         symbol.setColor(color)
         lower = ('%.*f' % (2, minimum + ( maximum - minimum ) / numberOfClasses * i ) )
         upper = ('%.*f' % (2, minimum + ( maximum - minimum ) / numberOfClasses * ( i + 1 ) ) )
         label = "%s - %s" % (lower, upper)
         newrange = QgsRendererRangeV2(
                                    float(lower),
                                    float(upper),
                                    symbol,
                                    label)
         ranges.append(newrange)
      renderer = QgsGraduatedSymbolRendererV2('',ranges)
      renderer.setMode(
              QgsGraduatedSymbolRendererV2.EqualInterval)
      renderer.setClassAttribute(fieldName)
      
      layer.setRendererV2(renderer)
      
      return layer
   # .......................................................................................      
   def addtoCanvas(self, pamsumid, bucketid, expid):
      """
      @summary: adds statistics to map canvas
      """
      if self.isModal():
         self.setModal(False)
      #if len(self.outEdit.text()) > 0:
      self.mapItBut.hide()
      self.progressbar.show()
      if self.speciesrichness.isChecked():
         fieldName = 'specrich'
         tocName = 'Species Richness'
      elif self.meanproportionalrangesize.isChecked():
         fieldName =  'avgpropRaS'  
         tocName = 'Mean Proportional Range Size'                                    
      elif self.proportionalspeciesdiversity.isChecked():        
         fieldName =  'propspecDi' 
         tocName = 'Proportional Species Diversity'                         
      elif self.localityrangesize.isChecked():
         fieldName =  'RaSLoc'   
         tocName = "Per-site Range Size of a Locality"          
      
      expFolder = self.saveDirectory
      zipName = "%s_%s_%s" % (expid,bucketid,pamsumid)
      #zipName = str(pamsumid)
      pathname = os.path.join(expFolder,zipName)
      try:
         success = self.client.rad.getPamSumShapegrid(pathname,
                                                   expid, bucketid, pamsumid)
      except:
         success = False
      if success:
         self.progressbar.setValue(100)
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
         else: 
            try:
               lyrs = QgsMapLayerRegistry.instance().mapLayers()
               for id in lyrs.keys():
                  if str(lyrs[id].name()) == shapename.replace('.shp',''):
                     QgsMapLayerRegistry.instance().removeMapLayer(id) 
               #classedLayer = self.classify(vectorLayer, fieldName)
               classedLayer = self.buildSetRenderer(vectorLayer, fieldName)
               classedLayer.setLayerName(tocName)               
               QgsMapLayerRegistry.instance().addMapLayer(classedLayer)
            except Exception, e:
               message = str(e)
               msgBox = QMessageBox.information(self,
                                          "Problem...",
                                          message,
                                          QMessageBox.Ok)
                          
               
 
      else:
         message = "Could not retrieve the shapefile"
         msgBox = QMessageBox.information(self,
                                          "Problem...",
                                          message,
                                          QMessageBox.Ok)
            
      
  # ............................................................................         
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" )
      fileDialog = QgsEncodingFileDialog( self, "Save .zip File", dirName,"Zip Files (*.zip)")
      fileDialog.setDefaultSuffix(  "zip"  )
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      self.addFile(filename[0])
      
   def addFile(self,filename):
      self.outEdit.setText(filename)   
   

   
   def openTree(self,path=None):
      """
      @summary: opens up the tree visualization dialog
      """  
      
      if self.isModal():
         self.setModal(False)
      #################################
      #mLRi = QgsMapLayerRegistry.instance()
      #pamList = mLRi.mapLayersByName('pam')
      #pam = pamList[0]
      ################################
      bucketId = int(self.inputs['bucketId'])
      self.treeWindow = TreeWindow(self,iface=self.interface,client=self.client,
                                   expId=self.expId, bucketId = bucketId,
                                   treePath=self.treeDLoc, expEPSG=self.expEPSG,
                                   activeLyr=self.activeLyr)
      #activeLyr=self.activeLyr,pamLyr=pam)
      
      
      self.treeWindow.show()
      self.treeWindow.raise_() # !!!!
      self.treeWindow.activateWindow() # !!!!
      
            
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
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('statistics')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()       
      
if __name__ == "__main__":
#  


   #import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
   #sys.path.append(os.path.join(import_path, 'LmShared'))
   ##
   #configPath = os.path.join(import_path, 'config', 'config.ini')
   ##
   #os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
   #from LmClient.lmClientLib import LMClient
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   d = PamSumsStatsDialog(None, inputs={'expId':501,'bucketId':512}, client=client)
   d.show()
   sys.exit(qApp.exec_())

      
      
