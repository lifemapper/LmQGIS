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
# 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import os, sys
from urllib2 import HTTPError
#from lifemapperTools.tools.browseOccProviders import BrowseOccProviderDock
from lifemapperTools.tools.archiveBrowser import archiveBrowserDock as BrowseOccProviderDock
from lifemapperTools.tools.signIn import SignInDialog
from lifemapperTools.tools.preferences import PreferencesDialog
from lifemapperTools.tools.listExperiments import ListExperimentDialog
from lifemapperTools.tools.listBuckets import ListBucketsDialog
from lifemapperTools.tools.listPALayers import ListPALayersDialog
from lifemapperTools.tools.uploadLayers import UploadDialog
from lifemapperTools.tools.newExperiment import NewExperimentDialog
from lifemapperTools.tools.postSDMExp import PostSDMExpDialog
from lifemapperTools.tools.addSDMLayer import UploadSDMDialog
from lifemapperTools.tools.pamSumsStats import PamSumsStatsDialog
from lifemapperTools.tools.spatialStats import SpatialStatsDialog
from lifemapperTools.tools.listSDMExperiments import  ListSDMExpDialog
from lifemapperTools.tools.ui_listBuildScenariosDialog import ListBuildScenariosDialog
from lifemapperTools.tools.ui_postEnvLayer import PostEnvLayerDialog
from lifemapperTools.tools.uploadTreeOTL import UploadTreeDialog
from lifemapperTools.tools.constructGrid import ConstructGridDialog
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.common.communicate import Communicate
from lifemapperTools.common.pluginconstants import QGISProject,\
                                          STAGELOOKUP,STAGEREVLOOKUP, \
                                         STATUSLOOKUP, STATUSREVLOOKUP, PER_PAGE
from LmCommon.common.lmconstants import JobStage, JobStatus
from LmClient.lmClientLib import LMClient


class MetoolsPlugin:
   
   
   #a = pyqtSignal(str,name="activateSDMExp")
   
   def __init__(self, iface):
      #QObject.__init__(self)
      #self.communicate = Communicate()    
      self.iface = iface
      self.expRADEPSG = None
      self.expRADmapUnits = None
      self.expRADexpId = None
      self.pamSumDialog = None
      
   def initGui(self):
      self.signInDialog = None
      self.menu = QMenu()
      self.menu.setTitle(QCoreApplication.translate("lifemapperTools", "&Lifemapper" ))
      self.menu.setObjectName('lifemapper')
      
      self._initSignInOutActions()
      self._initPrefsActions()
      self._initUploadEnvLayerAction()
      self._initRADActions()
      self._initSDMActions()
      self._initChangeWSAction()
      # SDM and RAD? menus
      self.currentSDMExpAction = None
      self.sdmMenu = QMenu(QCoreApplication.translate( "lifemapperTools", "LmSDM: Species Distribution Modeling" ) )
      self.radMenu = QMenu(QCoreApplication.translate( "lifemapperTools", "LmRAD: Range and Diversity" ) )
      self.radMenu.setEnabled(False)
      self.sdmMenu.setEnabled(False)
      self.radMenu.addActions([self.newExperimentItem, self.ResumeItem])
      self.sdmMenu.addActions([self.postSDMExpItem,self.postEnvLayerSetItem,self.listSDMExpsItem]) #,probably not here, #self.browseOccSetItem
      
      
      self.menu.addActions([self.signInItem, self.signOutItem,self.changeWSAction,self.preferencesAction])
      self.menu.insertMenu(self.signOutItem,self.radMenu)
      self.menu.insertMenu(self.signOutItem, self.sdmMenu)
      self.menu.insertAction(self.signOutItem,self.uploadEnvlayerAction)
      self.menu.insertAction(self.signOutItem,self.changeWSAction)
      
      
      ###########   Browse Occ Sets #################
      self.iface.addToolBarIcon(self.browseIconAction)
      #self.occSetBrowseDock = QDockWidget("Lifemapper Occurrence Sets")
      self.occSetBrowseDock = BrowseOccProviderDock(self.iface, action = self.browseIconAction)
      #self.occSetBrowseDock.setObjectName("occDock")
      
      self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.occSetBrowseDock)
      self.occSetBrowseDock.hide()
      ###############################################
    
      menu_bar = self.iface.mainWindow().menuBar()
      actions = menu_bar.actions()
      lastAction = actions[ len( actions ) - 1 ]
      menu_bar.insertMenu( lastAction, self.menu )
      
      
      self.activeLayer = None
      
      
      Communicate.instance().activateSDMExp.connect(self.currentSDMExperiment)
      Communicate.instance().activateRADExp.connect(self.currentExperiment)
      Communicate.instance().activateGrid.connect(self.currentGrid)
      Communicate.instance().setPamSumExist.connect(self.setPamSumDialog)
      

      
   def _initChangeWSAction(self):
      self.changeWSAction = QAction( QCoreApplication.translate("lifemapperTools", "Change Workspace"),self.iface.mainWindow())
      #QObject.connect(self.changeWSAction, SIGNAL("triggered()"), self.changeWS)
      self.changeWSAction.triggered.connect(self.changeWS)
      self.changeWSAction.setEnabled(False)
      
   def _initSDMActions(self):
      
      self.postSDMExpItem = QAction( QCoreApplication.translate("lifemapperTools", "New Experiment"),self.iface.mainWindow())
      self.postEnvLayerSetItem = QAction( QCoreApplication.translate("lifemapperTools", "Build Environmental Layer Set"),self.iface.mainWindow())
      self.listSDMExpsItem = QAction( QCoreApplication.translate("lifemapperTools", "List Experiments"),self.iface.mainWindow())
      
      # connect SDM actions      
      
      self.postSDMExpItem.triggered.connect(self.postSDMExp)
      self.postEnvLayerSetItem.triggered.connect(self.postEnvLayerSet)
      self.listSDMExpsItem.triggered.connect(self.listSDMExp)
      
      # Browse Occurrence Set Action for Icon  ################333
      self.browseIconAction = QAction(QIcon(":/plugins/lifemapperTools/icons/lm_worlds.png"), \
            "Browse Lifemapper Archive", self.iface.mainWindow())
      #self.browseIconAction.triggered.connect(self.showHideBrowseDock)
      ##################################################################
      #   for the menu item for browse dock
      #   self.browseOccSetItem = QAction(QCoreApplication.translate("lifemapperTools","Browse Occurrence Providers"),self.iface.mainWindow()) 
      ##  self.browseOccSetItem.triggered.connect(self.browseOccProv)
      
   def _initUploadEnvLayerAction(self):
      self.uploadEnvlayerAction =  QAction( QCoreApplication.translate("lifemapperTools", "Upload Environment Layer"),self.iface.mainWindow()) 
      #QObject.connect(self.uploadEnvlayerAction, SIGNAL("triggered()"),self.uploadEnvLayer)
      self.uploadEnvlayerAction.triggered.connect(self.uploadEnvLayer)
      self.uploadEnvlayerAction.setEnabled(False) 
# ..............................................................................     
   def _initSignInOutActions(self):
      """
      @summary: builds and connects sign in and sign out action items
      """
      
      self.signInItem = QAction( QCoreApplication.translate("lifemapperTools", "Sign In"),self.iface.mainWindow())
      self.signOutItem = QAction( QCoreApplication.translate("lifemapperTools", "Sign Out"),self.iface.mainWindow())
      #QObject.connect(self.signInItem, SIGNAL("triggered()"), self.signIn)
      #QObject.connect(self.signOutItem, SIGNAL("triggered()"), self.signOut)
      self.signInItem.triggered.connect(self.signIn)
      self.signOutItem.triggered.connect(self.signOut)
      self.signOutItem.setEnabled(False)
# ..............................................................................        
   def _initPrefsActions(self):
      
      self.preferencesAction = QAction( QCoreApplication.translate("lifemapperTools", "Preferences"),self.iface.mainWindow())
      self.preferencesAction.setEnabled(True)
      self.preferencesAction.triggered.connect(self.preferencesDialog)
# ..............................................................................
   def _initRADActions(self):
      
      # these action go under the rad menu
      self.newExperimentItem = QAction( QCoreApplication.translate("lifemapperTools", "New Experiment"),self.iface.mainWindow())
      self.ResumeItem = QAction(QCoreApplication.translate("lifemapperTools", "List Experiments" ),self.iface.mainWindow())
      
      #QObject.connect(self.newExperimentItem, SIGNAL("triggered()"), self.newExperiment)
      #QObject.connect(self.ResumeItem, SIGNAL("triggered()"), self.resume)
      
      self.newExperimentItem.triggered.connect(self.newExperiment)
      self.ResumeItem.triggered.connect(self.resume)
      
      self.ResumeItem.setEnabled(False)    
      self.newExperimentItem.setEnabled(False)
# .............................................................................. 
   def changeWS(self):
      if self.signInDialog.client is not None:
         username = self.signInDialog.client._cl.userId
         created = self.signInDialog.openDirectoryDialog(username, existingWorkSpace=True)
         if not created:
            self.signOut()
         
         
# .............................................................................. 
   def uploadEnvLayer(self):
      if self.signInDialog is not None:
         if self.signInDialog.client is not None:
            self.uploadEnvLayerDialog = PostEnvLayerDialog(interface=self.iface,client=self.signInDialog.client)
            self.uploadEnvLayerDialog.exec_()
      
      
   def postEnvLayerSet(self):
      
      if self.signInDialog is not None:
         if self.signInDialog.client is not None:
               self.postEnvLayersDialog = ListBuildScenariosDialog( self.iface, 
                                                     client = self.signInDialog.client)  
               self.postEnvLayersDialog.exec_()
# ..............................................................................           
#   def showHideBrowseDock(self):
#      
#      if self.occSetBrowseDock.isVisible():
#         self.occSetBrowseDock.hide()
#      else:
#         self.occSetBrowseDock.show()
      
      
# ..............................................................................
         
   def postSDMExp(self):
      if self.signInDialog is not None:
         if self.signInDialog.client is not None:
            if self.signInDialog.email is not None:
               self.postSDMExpDialog = PostSDMExpDialog( self.iface, 
                                                     client = self.signInDialog.client,
                                                     email = self.signInDialog.email)
            else:
               self.postSDMExpDialog = PostSDMExpDialog( self.iface, 
                                                     client = self.signInDialog.client)
               
      elif self.signInDialog is None:         
         cl = LMClient()
         self.postSDMExpDialog = PostSDMExpDialog( self.iface, client = cl)
      self.postSDMExpDialog.exec_()
# ..............................................................................     
   def listSDMExp(self):
      if self.signInDialog is not None:
         self.listSDMExpsDialog = ListSDMExpDialog(self.iface,
                                                   client=self.signInDialog.client)
         self.listSDMExpsDialog.exec_()
# .............................................................................
   def setPamSumDialog(self,pamsumDialog):
      
      self.pamSumDialog = pamsumDialog
# ..............................................................................        
   def currentGrid(self, expId, bucketId, stage, status, expEPSG, gridName, shpGrd):
      
      self.bucketMenu = QMenu(QCoreApplication.translate( "lifemapperTools", "Current Grid" ) )
      
      self.statsMenu = QMenu(QCoreApplication.translate( "lifemapperTools", "Statistics" ) )
      
      # actions for bucket
      
      self.plotstablesAction = QAction( QCoreApplication.translate("lifemapperTools", "Plots and Tables"),self.iface.mainWindow())
      #QObject.connect(self.plotstablesAction, SIGNAL("triggered()"), lambda :self.openStats(expId,bucketId))
      self.plotstablesAction.triggered.connect(lambda: self.openStats(expId, bucketId, expEPSG, gridName, shpGrd))
      self.statsMenu.addAction(self.plotstablesAction)
  
      
      self.viewSiteBasedAction =  QAction( QCoreApplication.translate("lifemapperTools", "Spatially View Site Based Stats"),self.iface.mainWindow())
      #QObject.connect(self.viewSiteBasedAction, SIGNAL("triggered()"), lambda :self.openSpatialStats(expId,bucketId))
      self.viewSiteBasedAction.triggered.connect(lambda: self.openSpatialStats(expId, bucketId))
      self.statsMenu.addAction(self.viewSiteBasedAction)
      
      self.bucketMenu.addMenu(self.statsMenu)
      self.radMenu.addMenu(self.bucketMenu)
      
# ..............................................................................     
   def openStats(self,expId, bucketId, expEPSG, gridName, shpGrd):
      
      if self.pamSumDialog is None:
         inputs = {'expId':expId,'bucketId':bucketId}
         if str(self.retrieveCurrentExpId()) != str(expId):
            projPath = self._retrieveRADExpProjPath(expId)
         else:
            projPath = False
         self.PamSumStats = PamSumsStatsDialog(self.iface,
                                                 inputs=inputs,
                                                 client=self.signInDialog.client,resume=projPath,
                                                 expEPSG=expEPSG, gridName=gridName, shpGrd = shpGrd)
         self.PamSumStats.exec_()
      else:
         if not self.pamSumDialog.isVisible():
            self.pamSumDialog.checkShowLinked = True
            self.pamSumDialog.show()
# ..............................................................................        
   def openSpatialStats(self,expId, bucketId):  
      inputs = {'expId':expId,'bucketId':bucketId}
      if str(self.retrieveCurrentExpId()) != str(expId):
         projPath = self._retrieveRADExpProjPath(expId)
      else:
         projPath = False
      self.SpatialStatsDialog = SpatialStatsDialog(self.iface,
                                              inputs=inputs,
                                              client=self.signInDialog.client,resume=projPath)
      self.SpatialStatsDialog.exec_()
      
   def currentSDMExperiment(self,expId):
      self.currentSDMExpId = expId
      if self.currentSDMExpAction is None:
         self.currentSDMExpAction = QAction( QCoreApplication.translate("lifemapperTools", "Current Experiment"),self.iface.mainWindow())
         #QObject.connect(self.currentSDMExpAction, SIGNAL("triggered()"),self.resumeSDMExp)  
         self.currentSDMExpAction.triggered.connect(self.resumeSDMExp)
         self.sdmMenu.addAction(self.currentSDMExpAction)
      
      
      
   def resumeSDMExp(self):
      if self.signInDialog.client is not None:
         self.resumeSDMExpDialog = ListSDMExpDialog(self.iface,
                                                   client=self.signInDialog.client,
                                                   experimentId=self.currentSDMExpId) 
         self.resumeSDMExpDialog.exec_()
# ..............................................................................          
   def currentExperiment(self, expId, expEPSG, mapunits):
      
     
      
      self.bucketMenu = None
      self.experimentMenu = QMenu(QCoreApplication.translate( "lifemapperTools", "Current Experiment" ) )
       
      # actions for exp 
      
      # list grids action
      self.listBucketsAction = QAction( QCoreApplication.translate("lifemapperTools", "Access Grids"),self.iface.mainWindow()) 
      #QObject.connect(self.listBucketsAction, SIGNAL("triggered()"),lambda :self.resumeBuckets(expId, expEPSG, mapunits)) 
      self.listBucketsAction.triggered.connect(lambda :self.resumeBuckets(expId, expEPSG, mapunits))
      self.experimentMenu.addAction(self.listBucketsAction)
      
      self.constructGridAction = QAction( QCoreApplication.translate("lifemapperTools", "Construct Grid"),self.iface.mainWindow())
      self.constructGridAction.triggered.connect(lambda: self.constructGrid(expId,expEPSG,mapunits))
      self.experimentMenu.addAction(self.constructGridAction)
      
      # list presence absence layers action
      self.listPALayersAction = QAction( QCoreApplication.translate("lifemapperTools", "List Species Layers"),self.iface.mainWindow()) 
      #QObject.connect(self.listPALayersAction, SIGNAL("triggered()"),lambda :self.resumePALayers(expId, expEPSG, mapunits)) 
      self.listPALayersAction.triggered.connect(lambda :self.resumePALayers(expId, expEPSG, mapunits))
      self.experimentMenu.addAction(self.listPALayersAction)
      
      # add PA layers action 
      
      self.addPALayersAction = QAction( QCoreApplication.translate("lifemapperTools", "Add Species Layers"),self.iface.mainWindow()) 
      #QObject.connect(self.addPALayersAction, SIGNAL("triggered()"),lambda :self.addPALayers(expId, expEPSG, mapunits)) 
      self.addPALayersAction.triggered.connect(lambda :self.addPALayers(expId, expEPSG, mapunits))
      self.experimentMenu.addAction(self.addPALayersAction)
      
      # add SDM layers action 
      
      self.addSDMLayersAction = QAction( QCoreApplication.translate("lifemapperTools", "Add SDM Layers"),self.iface.mainWindow()) 
      #QObject.connect(self.addSDMLayersAction, SIGNAL("triggered()"),lambda :self.addSDMLayers(expId, expEPSG, mapunits)) 
      self.addSDMLayersAction.triggered.connect(lambda :self.addSDMLayers(expId, expEPSG, mapunits))
      self.experimentMenu.addAction(self.addSDMLayersAction)
      
      
      self.addPhyloAction = QAction( QCoreApplication.translate("lifemapperTools", "Add Phylogeny"),self.iface.mainWindow())
      self.addPhyloAction.triggered.connect(lambda: self.addPhylogeny(expId, expEPSG, mapunits))
      self.experimentMenu.addAction(self.addPhyloAction)
      
      
      
      #self.menu.insertMenu(self.newExperimentItem,self.experimentMenu)
      self.radMenu.addSeparator()
      self.radMenu.addMenu(self.experimentMenu)

# ..............................................................................

   def addPhylogeny(self,currentExpId, expEPSG, mapunits):
      if self.signInDialog.client is not None:
         if str(self.retrieveCurrentExpId()) != str(currentExpId):
            projPath = self._retrieveRADExpProjPath(currentExpId)
         else:
            projPath = False
         try:
            items = self.signInDialog.client.rad.getPALayers(currentExpId)
         except:
            items = None
            message = "There is a problem with the layer listing service"
            msgBox = QMessageBox.information(QWidget(),
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
         else:
            if len(items) != 0:
               message = "You already have layers in this experiment. You must begin an experiment with trees and their layers"
               msgBox = QMessageBox.information(QWidget(),
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
            else:
               self.addPhyloDialog = UploadTreeDialog(self.iface,
                                                inputs = {'expId':currentExpId},
                                                client = self.signInDialog.client, 
                                                epsg = expEPSG,experimentname=str(currentExpId),
                                                mapunits=mapunits,resume=projPath)
               self.addPhyloDialog.exec_()

# ..............................................................................    
   def addSDMLayers(self,currentExpId, expEPSG, mapunits):
      if self.signInDialog.client is not None:
         if str(self.retrieveCurrentExpId()) != str(currentExpId):
            projPath = self._retrieveRADExpProjPath(currentExpId)
         else:
            projPath = False
         self.addSDMLayersDialog = UploadSDMDialog( self.iface, 
                                    inputs = {'expId':currentExpId},
                                    client = self.signInDialog.client, 
                                    epsg = expEPSG,experimentname=str(currentExpId),
                                    mapunits=mapunits,resume=projPath) 
         self.addSDMLayersDialog.exec_()
   
# ..............................................................................     
   def addPALayers(self,currentExpId, expEPSG, mapunits):
      if self.signInDialog.client is not None:
         if str(self.retrieveCurrentExpId()) != str(currentExpId):
            projPath = self._retrieveRADExpProjPath(currentExpId)
         else:
            projPath = False
         self.addPALayersDialog = UploadDialog( self.iface, 
                                    inputs = {'expId':currentExpId},
                                    client = self.signInDialog.client, 
                                    epsg = expEPSG,
                                    experimentname=str(currentExpId),
                                    mapunits=mapunits,resume=projPath) 
         self.addPALayersDialog.exec_()
      
# .............................................................................
   def constructGrid(self, currentExpId, expEPSG, mapunits):
      if self.signInDialog.client is not None:
         if str(self.retrieveCurrentExpId()) != str(currentExpId):
            projPath = self._retrieveRADExpProjPath(currentExpId)
         else:
            projPath = False
         # need to deal with resume   
         self.constructGridDialog = ConstructGridDialog( self.iface, 
                                                         inputs = {'expId':currentExpId},
                                                         mapunits=mapunits,
                                                         epsg=expEPSG,
                                                         client = self.signInDialog.client,
                                                         resume=projPath)
         self.constructGridDialog.setModal(False)
         self.constructGridDialog.show()
# ..............................................................................        
   def resumePALayers(self,currentExpId, expEPSG, mapunits):
      if self.signInDialog.client is not None:
         if str(self.retrieveCurrentExpId()) != str(currentExpId):
            projPath = self._retrieveRADExpProjPath(currentExpId)
         else:
            projPath = False
         self.listPALayersDialog = ListPALayersDialog(self.iface,
                                              inputs={'expId':currentExpId},
                                              client=self.signInDialog.client,
                                              epsg = expEPSG, 
                                              mapunits=mapunits,resume=projPath)
         self.listPALayersDialog.exec_()
# ..............................................................................        
   def resumeBuckets(self,currentExpId,expEPSG, mapunits):
      #currentExpId = self.retrieveCurrentExpId()
      if self.signInDialog.client is not None:
         if str(self.retrieveCurrentExpId()) != str(currentExpId):
            projPath = self._retrieveRADExpProjPath(currentExpId)
         else:
            projPath = False
         gridCount = self._getRADGridCount(currentExpId)
         if not(isinstance(gridCount, HTTPError)):
            if gridCount > 0:
               self.listBuckets = ListBucketsDialog(self.iface,
                                              inputs={'expId':currentExpId},
                                              client=self.signInDialog.client,
                                              epsg=expEPSG, 
                                              mapunits=mapunits,resume=projPath)
               self.listBuckets.exec_()
            else:
               message = "There are no Grids for this experiment, use Construct Grid from the current experiment menu"
               msgBox = QMessageBox.information(QWidget(),
                                             "Info...",
                                             message,
                                             QMessageBox.Ok)
         else:
            message = "There is a problem with Grid Count"
            msgBox = QMessageBox.information(QWidget(),
                                             "Info...",
                                             message,
                                             QMessageBox.Ok)
# ..............................................................................        
   def signOut(self):
      
      s = QSettings()
      self.checkExperiments()
      user = self.signInDialog.client._cl.userId
      del self.signInDialog.client
      self.preferencesAction.setEnabled(True)
      self.signInItem.setEnabled(True)
      self.ResumeItem.setEnabled(False)
      self.newExperimentItem.setEnabled(False)
      self.radMenu.setEnabled(False)
      self.sdmMenu.setEnabled(False)
      self.uploadEnvlayerAction.setEnabled(False)
      self.changeWSAction.setEnabled(False)
      self.signOutItem.setEnabled(False)
      try:
         self.experimentMenu = None
         self.bucketMenu = None
         self.sdmMenu.removeAction(self.currentSDMExpAction)
         self.currentSDMExpAction = None
      except:
         pass
      
      #QObject.disconnect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onSaveSaveAs)
      #QObject.disconnect(self.iface,SIGNAL("projectRead()"),self.onReadProject)
      
      QgsProject.instance().writeProject.disconnect(self.onSaveSaveAs)
      self.iface.projectRead.disconnect(self.onReadProject)
      
      
      s.remove("currentExpID")
      s.remove("currentUser")
      message = "User %s is signed out of the Lifemapper system" % (user) 
      msgBox = QMessageBox(QMessageBox.NoIcon,"Signed Out",message,
                           QMessageBox.Ok) 
      pixMap = QPixmap(":/plugins/lifemapperTools/icons/owlSmall.png")
      msgBox.setIconPixmap(pixMap)
      msgBox.exec_() 

# ..............................................................................

   def onReadProject(self):
      
      project = QgsProject.instance()
      # filename that is being opened
      filename = str(project.fileName())
      currentExpId  = self.retrieveCurrentExpId() # if -999 key has been removed (singed out)
      # or no experiment has been opened yet, or a new SDM experiment dialog was opened but no
      # experiment was created, probably same for RAD experiment?
      if currentExpId != QGISProject.NOEXPID:
         # they are opening a QGIS project while there is an active LM id
         # check and see if project is the value for some id key, if so make that
         # key the active id     
         found = False
         s = QSettings()
         for key in s.allKeys():
            if 'RADExpProj' in key:
               value = str(s.value(key))
               if value == filename:
                  found = True
                  expId = key.split('_')[1]
                  s.setValue("currentExpID", int(expId))   
         if not found:
            s.remove("currentExpID")
# ..............................................................................        
   def retrieveCurrentExpId(self):
      s = QSettings()
      currentExpId  = s.value("currentExpID",QGISProject.NOEXPID,type=int)
      return currentExpId             
# .............................................................................. 
   def _retrieveRADExpProjPath(self,expId):
      s = QSettings()
      return str(s.value("RADExpProj_"+str(expId),QGISProject.NOPROJECT))

# .............................................................................. 
   def _comparePathToId(self):
      # is the current Id currentExpId = self.retrieveCurrentExpId() the key for 
      # the current QgisProject instance path?
      project = QgsProject.instance()
      filename = str(project.fileName())
      currentExpId = self.retrieveCurrentExpId()
      currentPath = self._retrieveRADExpProjPath(currentExpId)
      #hasKey = self._hasProjKey(str(currentExpId)) # ?or if the saved project in settings is in a value for a key?
      if filename != currentPath:
         return False
      else:
         return True

# ..............................................................................          
   def unload(self):
      # called when quiting Qgis, need this to set the object name and so save state 
      # on shutdown, however...
      #if self.occSetBrowseDock.isVisible():
      #   self.occSetBrowseDock.showHideBrowseDock()
         
      s = QSettings()
      currentExpId = self.retrieveCurrentExpId()
      if currentExpId != QGISProject.NOEXPID and currentExpId != '':
         project = QgsProject.instance()
         filename = project.fileName()
         if filename != '' and filename != QGISProject.NOPROJECT:
            #if self._comparePathToId(): # this may be way wrong, check on Monday
            #print "comarePathToId True in unload"
            s.setValue("RADExpProj_"+str(currentExpId), filename)
      s.remove("currentExpID")    
      
      self.iface.removeToolBarIcon(self.browseIconAction) 
      self.iface.removeDockWidget(self.occSetBrowseDock)


   def onSaveSaveAs(self,domproject):
      # called on every save or save as, after the actual save
      # on unload comes here first if dirty
      s = QSettings()
      currentExpId  = self.retrieveCurrentExpId()
      if currentExpId != QGISProject.NOEXPID and currentExpId != '':
         #if self._comparePathToId():  # this may be way wrong, check on Monday
         #print "comarePathToId True in save"
         project = QgsProject.instance()
         filename = str(project.fileName())
         if filename != '' and filename != QGISProject.NOPROJECT:
            s.setValue("RADExpProj_"+str(currentExpId), filename)
# ..............................................................................    
   def checkExperiments(self):
      # called on log out
      s = QSettings()
      currentExpId  = self.retrieveCurrentExpId()
      if currentExpId != QGISProject.NOEXPID:
         currentpath = str(s.value("RADExpProj_"+str(currentExpId),
                                   QGISProject.NOPROJECT))
         if currentpath != QGISProject.NOPROJECT and currentpath != '':
            self.iface.actionSaveProject().trigger()
         else:
            if len(QgsMapLayerRegistry.instance().mapLayers().items()) > 0:
               self.iface.actionSaveProjectAs().trigger()
               # this happens on the slot for save and save as in main plugin
               #project = QgsProject.instance()
               #filename = str(project.fileName())
               #s.setValue("RADExpProj_"+str(currentExpId), filename)
               
# .............................................................................
   def _getRADGridCount(self, expId):
      if self.signInDialog.client is not None:
         try:      
            count = self.signInDialog.client.rad.countBuckets(expId)
         except HTTPError,e :
            count = e
         return count
            
# ..............................................................................         
   def _getRADExps(self):
      if self.signInDialog.client is not None:
         try:
            items = self.signInDialog.client.rad.listExperiments(perPage=PER_PAGE)
         except:
            items = None
            message = "There is a problem with the experiment listing service"
            msgBox = QMessageBox.information(QWidget(),
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
         else:
            if len(items) == 0:  
               items = None    
               message = "There are no experiments for this user"
               msgBox = QMessageBox.information(QWidget(),
                                             "No experiments...",
                                             message,
                                             QMessageBox.Ok)
      else:
         items = None
      return items
               
# ..............................................................................        
   def resume(self):
      """
      @summary: lists RAD experiments
      """
      if self.signInDialog.client is not None:
         items = self._getRADExps()
         if items is not None:
            self.listExpDialog = ListExperimentDialog(self.iface,client=self.signInDialog.client,
                                                      items = items)
            self.listExpDialog.exec_()        
      else:
         print "no client"
# .............................................................................
   def preferencesDialog(self):
      
      preferences = PreferencesDialog()
      preferences.exec_()
      
# ..............................................................................                      
   def signIn(self):
      
      
      s = QSettings()
      s.remove("currentExpID")
      self.signInDialog = SignInDialog(self.iface,resumeItem=self.ResumeItem,
                                       newExperimentItem=self.newExperimentItem,
                                       signInItem=self.signInItem, radMenu=self.radMenu,
                                       sdmMenu=self.sdmMenu, signOutItem=self.signOutItem,
                                       uploadEnvLayerItem=self.uploadEnvlayerAction,
                                       changeWSItem=self.changeWSAction,
                                       saveSlot=self.onSaveSaveAs,openSlot=self.onReadProject,
                                       preferencesAction=self.preferencesAction)
      result = self.signInDialog.exec_()
# ..............................................................................     
   def newExperiment(self):
      if self.signInDialog.client is not None:
         if self.signInDialog.email is not None:
            d = NewExperimentDialog(self.iface,client=self.signInDialog.client,
                                    email=self.signInDialog.email)
         else:
            d = NewExperimentDialog(self.iface,client=self.signInDialog.client)
         d.exec_()
      else:
         print "no client"
         
 
