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
import sys
import os
import zipfile
import cPickle
import csv
import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from collections import namedtuple
from lifemapperTools.common.communicate import Communicate
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.common.qProgressThread import TaskThread
from lifemapperTools.common.pluginconstants import RADStatTypes
from lifemapperTools.common.lmListModel import LmListModel, EnterTextEventHandler
from lifemapperTools.common.classifyQgisLyr import Classify
from lifemapperTools.tools.spreadsheetView import SpreadSheet
import lifemapperTools.icons.icons
try: import simplejson as json 
except: import json
import numpy as np
import math
import operator
from collections import Counter

def toUnicode(value, encoding='utf-8'):
   """
   @summary: Encodes a value for a element's text
   @param value: The object to make text
   @param encoding: (optional) The encoding of the text
   @todo: Encoding should be a constant
   """
   if isinstance(value, basestring):
      if not isinstance(value, unicode):
         value = unicode(value, encoding)
   else:
      value = unicode(str(value), encoding)
   return value
      
def fromUnicode(uItem, encoding="utf-8"):
   """
   @summary: Converts a unicode string to text for display
   @param uItem: A unicode object
   @param encoding: (optional) The encoding to use
   """
   return uItem.encode("utf-8")


class WebPage(QWebPage):
   """
   Makes it possible to use a Python logger to print javascript console messages
   """
   def __init__(self, logger=None, parent=None):
      super(WebPage, self).__init__(parent)
      if not logger:
         logger = logging
      self.logger = logger
        

   def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
      self.logger.warning("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))
        
class NodeClass(QObject):  
   """Simple class with two slots """  
   
   def __init__(self):
      QObject.__init__(self)
      
   
   def getIdsFromJSONDict(self,leaves):
      selectedIdxs = [ rec["mx"]  for rec in leaves["selected"] if "mx" in rec]
      return selectedIdxs 
      
      
   @pyqtSlot(str,str)  #QWebElement
   def showMessage(self, jsonStr, domElement):  
      """Open a message box and display the specified message."""  
      #QMessageBox.information(None, "Info", msg) 
       
      
      self.selectedNode = json.loads(str(jsonStr))
      
   @pyqtSlot(str)
   def processLeafJSON(self, selected):
      """
      @summary: takes the json selected in the tree and emits a signal
      to the plot
      """
      # turns json from the javascript into python dict
      leaves = json.loads(str(selected)) 
      
      selectedMtrxIdxs = self.getIdsFromJSONDict(leaves)
      Communicate.instance().RADSpsSelectedFromTree.emit(selectedMtrxIdxs)
      
   @pyqtSlot(str)
   def printList(self,name):
      print name
           
   @pyqtSlot(str)
   def selectSps(self, leafs):
      """
      @param leafs: json for the leaves of the tree 
      """
      
      #print leafs
      pass

   
class TreeWindow(QMainWindow):
   """
   @summary: main class for the tree window
   """
   def __init__(self, pamsumDialog, iface=None, client=None, expId=None, bucketId = None, treePath=None, 
                activeLyr=None,renderer=None,registry=None, expEPSG=None, pamLyr=None):
      super(TreeWindow, self).__init__()
      Communicate.instance().setTreeExist.emit(self)
      ##############
      self.paths = []
      self.ids = []
      ###############
      #QDialog.__init__(self)
      self.setAttribute(Qt.WA_DeleteOnClose)
      self.pamsumDialog = pamsumDialog
      self.expId = expId
      self.bucketId = bucketId
      self.expEPSG = expEPSG
      self.view = QWebView(self)
      self.view.setPage(WebPage())
      self.view.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,
                                               True)
      self.iface = iface
      self.activeLyr = activeLyr
      self.registry  = registry
      self.renderer = renderer
      pluginOS = self.getOS()  
      self.client = client
      if client is not None and expId is not None and iface is not None:
         expFolder = self.getProjDirectory(client,expId,iface)
         if not expFolder:
            expFolder = self.workspace.createProjectFolder(expId)
         self.expDir = expFolder
      else:
         self.expDir = None
      ############## temp #########################
      #self.setJSONPath(iface, client, expId) # temp, json folder, needs to be commented
      # and replaced with self.jsonPath = treePath, for release
      #############################################
      
      self.jsonPath = treePath  
      
      ######## build the tree url ##################
      pluginDir = os.path.dirname(os.path.realpath(__file__)) # gets the plugin tools directory
      url = os.path.join(pluginDir,"treeWeb.html")
      url = "file:///%s" % (url)
      ##############################################
      
      if self.jsonPath:
         searchJSON = self.jsonPath
         if pluginOS:
            self.jsonUrl = "file:///%s" % (searchJSON)
         else:
            self.jsonUrl = "file:///%s" % (os.path.normpath(searchJSON).replace("\\","/"))  #only for windows, different for Linux
      
      else:
         # only for testing outside of qgis
         if pluginOS:    
            #searchJSON = "/home/jcavner/Pooka8/Rodentia_628/tree/tree.json" # Rodentia
            #self.jsonUrl = "file:///home/jcavner/Pooka8/Rodentia_628/tree/tree.json"
            #self.jsonUrl = "file:///home/jcavner/attrTree_1011.json"
            #searchJSON = "/home/jcavner/attrTree_1011.json"
            #self.jsonUrl = "file:///home/jcavner/PhyloXM_Examples/Liebold_notEverythinginMatrix.json"
            #searchJSON = "/home/jcavner/PhyloXM_Examples/Liebold_notEverythinginMatrix.json"
            #self.jsonUrl = "/home/jcavner/Pooka8/TestPhyloNames_1798/tree/tree.json"
            #searchJSON = "//home/jcavner/Pooka8/TestPhyloNames_1798/tree/tree.json"
            self.jsonUrl = "/home/jcavner/BiogeographyMtx_Inputs/Florida/tree_2_exp1800.json_withIds.json"
            searchJSON = "/home/jcavner/BiogeographyMtx_Inputs/Florida/tree_2_exp1800.json_withIds.json"
            #filename =   "african_mammal_realDealMX.json"
            #filename  =   "mammalsWithLengthsandMX.json" 
            #filename  = 'amphibianJSONDirectTest.json'
            #filename   =  'newick_wNonAscii.json'
            #filename   = 'amphEdgeLenExponent.json'
            #filename  = 'newickFromPooka1.json'
            #filename = "Liebold.json"
            #searchJSON = "/home/jcavner/PhyloXM_Examples/" + filename
            #self.jsonUrl = "file:///home/jcavner/PhyloXM_Examples/" + filename
         else:
            print "this tree"
            searchJSON = 'C:/Users/Jeff Cavner/json/mammals.json'
            self.jsonUrl = 'file:///C:/Users/Jeff Cavner/json/mammals.json'
            
      ################ end workspace and paths #########################
      
      # connect instance of the Tree Window to signal comming from plot for species
      Communicate.instance().RADSpsSelectFromPlot.connect(self.selectSpsTree)
      
      
      ######## Data model and json load for hint service ############
      
      self.genusDict = {}
      self.comboDataModel = []
      self.pilotList = []
      self.allClades = {}
      ########  experimental ##########
      self.tips = []
      self.repeatIds = []
      ########################
      jsonStr = open(searchJSON).read()
      treeDict = json.loads(str(jsonStr))
      self.flattenTreeToTips(treeDict)
      self.calcNoDesc()
      
      #self.calculateDepth()
      #for k in self.allClades.keys():
      #   print self.allClades[k]
      self.addGeneraToHintList()
      ###################################
      
      self.view.load(QUrl(url))
      
      self.central = QWidget()
      
      self.node = NodeClass()
      self.view.page().mainFrame().addToJavaScriptWindowObject("pyObj", self.node)
      self.view.page().mainFrame().addToJavaScriptWindowObject("TreeWindowObj", self)
      self.setWindowTitle('Phylo View')
      
      self.path = None
      
      self.spreadSheetBut = QPushButton("S")
      self.spreadSheetBut.setMaximumWidth(50)
      self.spreadSheetBut.clicked.connect(self.openSpreadSheet)
      
      icon = QIcon(":/plugins/lifemapperTools/icons/clearTreeSelection.png")
      self.clearSelectionBut = QPushButton(icon,"")
      self.clearSelectionBut.setMaximumWidth(50)
      self.clearSelectionBut.setToolTip("clear selection")
      self.clearSelectionBut.clicked.connect(self.clearSelection)
      
      self.reloadButton = QPushButton("Load Tree")
      self.reloadButton.setMaximumWidth(100)
      self.reloadButton.setToolTip("Load/Reload")
      self.reloadButton.clicked.connect(self.reload)
      
      self.plotButton = QPushButton("See Leaves in Plot")
      #self.plotButton.setMaximumWidth(150)
      self.plotButton.setToolTip("When you have selected species in the tips, click this to show them in a species plot")
      self.plotButton.setMinimumWidth(150)
      self.plotButton.clicked.connect(self.selectSpsPlot)
      
      self.backToPamSumButton = QPushButton("Stats")
      self.backToPamSumButton.setMaximumWidth(50)
      self.backToPamSumButton.setToolTip("Go Back to Stats Panel")
      self.backToPamSumButton.clicked.connect(self.goBackToStats)
      
      self.findCladeCombo = QComboBox() #keyedQComboBox()     
      self.findCladeCombo.setToolTip("Start typing to find a genus or individual species, then use 'Find Species' button to select")
      self.findCladeCombo.setMinimumWidth(300)
      self.findCladeCombo.setEditable(True)
      self.findCladeCombo.setAutoCompletion(True)
      self.findCladeCombo.textChanged.connect(self.onTextChange)
      
      self.findCladeButton = QPushButton("Find Species")
      self.findCladeButton.setMaximumWidth(100)
      self.findCladeButton.setMinimumWidth(100)   
      self.findCladeButton.setToolTip("Find Species")
      self.findCladeButton.clicked.connect(self.findClade)  
      
      self.more = QPushButton("<")
      self.more.setMaximumWidth(25)
      self.more.setToolTip("show tips")
      self.more.clicked.connect(self.hideShowTips)
      
      self.helpBut = QPushButton("?")
      self.helpBut.setMinimumWidth(20)
      self.helpBut.setMaximumWidth(20)
      self.helpBut.setToolTip("Help with this dialog")
      self.helpBut.clicked.connect(self.help)
      
      ############## MNTD #################
      #self.mntdBut = QPushButton("MNTD")
      #self.mntdBut.setMinimumWidth(50)
      #self.mntdBut.clicked.connect(self.calcMNTD)
      
      self.mntdDisplay = QLineEdit()
      self.mntdDisplay.setMinimumWidth(120)
      self.mntdDisplay.setMaximumWidth(120)
      self.mntdDisplay.setReadOnly(True)
      #######################################
      
      # set models and event handlers for search against json
      self.setModels()
      self.setEventHandlers()
      ######################
     
      # dockable  # this requires a mainWindow rather than a dialog
      self.listdock = QDockWidget("Selected",self)
      #self.listdock.setFeatures # this will get rid of cancel
      self.listdock.hide()
      self.listdock.setAllowedAreas(Qt.RightDockWidgetArea)
      #self.listdock.setTitleBarWidget(self.tipTabBar)
      self.list = TreeList()
      self.list.setStyleSheet("font: 11pt;")
      self.list.itemDoubleClicked.connect(self.zoomItem)
      #self.selectedModel = SelectedListModel([],self)
      #self.list.setModel(self.selectedModel)
      
      self.listdock.setWidget(self.list)
      self.addDockWidget(Qt.RightDockWidgetArea,self.listdock)
      ####################
      
      
      layout = QVBoxLayout()
      
      layout.setMargin(0)
      layout.addWidget(self.view)
      
      ## top hlayout ##
      buttonWidget = QWidget()
      buttonWidget.setFixedHeight(42)
      self.hlayout = QHBoxLayout(buttonWidget)
      self.hlayout.setMargin(0)
      #self.hlayout.addWidget(self.helpBut)
      #self.hlayout.addWidget(self.mntdBut)
      self.hlayout.addWidget(self.mntdDisplay)
      self.hlayout.addWidget(self.plotButton)
      #self.hlayout.addWidget(self.backToPamSumButton)
      #self.hlayout.addWidget(self.clearSelectionBut)
      self.hlayout.addWidget(self.reloadButton)
      self.hlayout.addWidget(self.findCladeCombo)
      self.hlayout.addWidget(self.findCladeButton)
      self.hlayout.addWidget(self.more)
      layout.addWidget(buttonWidget)
      
      ## bottom hlayout ##
      botButWidget = QWidget()
      
      botButWidget.setFixedHeight(42)
      botGridLayout = QHBoxLayout(botButWidget) #botButWidget
      botGridLayout.setContentsMargins(4, 4, 4, 8) # left, top, right, bottom
      
      
      self.pamBut = QPushButton("PAM")
      self.pamBut.setMaximumWidth(36)
      self.pamBut.clicked.connect(self.setUpPam)
      
      
      #self.bottomRightGrid = QGridLayout(bottomRightWidget)
      #self.bottomRightGrid.setColumnMinimumWidth(0,335)
      #self.bottomRightGrid.setColumnMinimumWidth(1,323)
      
      self.bottomRighWidgetProgress = QWidget()
      self.progressHBox = QHBoxLayout(self.bottomRighWidgetProgress)
      self.progress = QProgressBar();self.progress.setMinimum(0);self.progress.setMaximum(0)
      self.progressHBox.addWidget(self.progress)
      #self.progress.hide()
      self.bottomRighWidgetProgress.hide()
      
      
      ### uncomment this for stats mapped into ranges ##
      self.fieldsCombo = QComboBox()
      self.fieldsCombo.setMinimumHeight(26)
      self.fieldsCombo.addItem('choose statistics field to map into ranges',userData='0')
      self.fieldsCombo.setToolTip("Functionality will be enabled in plugin version 3.0.0")
      self.fieldsCombo.currentIndexChanged.connect(self.changeRenderer)
      self.fieldsCombo.setEnabled(False)
      #########################################
      
      self.bottomRightWidgetCombo = QWidget()
      self.rightHoriz = QHBoxLayout(self.bottomRightWidgetCombo)
      self.rightHoriz.setContentsMargins(0, 2, 0, 10)
      # uncomment this for stats mapped into ranges
      self.rightHoriz.addWidget(self.fieldsCombo)
      
      
      
      botGridLayout.addWidget(self.pamBut)#,0,0,1,1)
      botGridLayout.addWidget(self.bottomRightWidgetCombo)#,0,1,1,1)
      botGridLayout.addWidget(self.bottomRighWidgetProgress)
      botGridLayout.addWidget(self.spreadSheetBut)
      botGridLayout.addWidget(self.clearSelectionBut)
      botGridLayout.addWidget(self.backToPamSumButton)
      botGridLayout.addWidget(self.helpBut)
      
      #############   check for pam and join and set self.pamLayer and self.join, enable combo and fields
      #pam = self.checkForPam()  # check for pam in canvas
      # uncomment for joins, two members, self.pamLayer, and pamLyr need to be resolved
      #if pam:
      #   joined,joinLayer = self.checkForJoins(pam)
      #   if joined:
      #      self.pamLayer = pam
      #      self.join = True
      #      self.joinLayer = joinLayer
      #      ### uncomment this for stats mapped into ranges ##
      #      #self.setFieldsCombo(joinLayer)
      #      #self.fieldsCombo.setEnabled(True)
      #   else:
      #      self.join = False
      #      self.joinLayer = None
      #      self.pamLayer = None
      #else:
      #   self.join = False
      #   self.joinLayer = None
      #   self.pamLayer = None
      #################################################
      # this was for selecting all species in a group of geographic sites
      #################################################
      #if activeLyr is not None and pam is not None:
      #   # connect activeLyr selection changed
      #   self.pamLyr = pam
      #   self.activeLyr.selectionChanged.connect(self.featuresSelectedInMap)
      #################################################
      
      toto = QFrame()
      toto.setFrameShape(QFrame.HLine)
      toto.setFrameShadow(QFrame.Sunken)
      
      layout.addWidget(toto)
      layout.addWidget(botButWidget)
      #layout.addLayout(botGridLayout)
      
      self.central.setLayout(layout)
      self.setCentralWidget(self.central)
      
      #layout.addWidget(rootbutton)
      self.turnAllWidgetsOff()
# ........................................................................
   def  openSpreadSheet(self):
      internalbase = "/home/jcavner/BiogeographyMtx_Inputs/Florida/outputs/"
      internal = cPickle.load(open(os.path.join(internalbase,'internal_2.pkl')))
      
      #############
      # pam #
      pambase = "/home/jcavner/BiogeographyMtx_Inputs/Florida/"
      pam = np.load(os.path.join(pambase,"fullpam_float_2.npy"))
      ########
      
      base = "/home/jcavner/BiogeographyMtx_Inputs/Florida/outputs/CSV_ForViewing/"
      
      #dataList_Str = list(csv.reader(open(os.path.join(base,"filteredJustBio_NewNodes.csv"))))
      dataList_Str = list(csv.reader(open(os.path.join(base,"BioGeo2Viewing.csv")))) #BioGeo2Viewing.csv
      dataList = [[float(value) for value in row] for row in dataList_Str]
      
      header = ["Node Number", "Apalachicola","Gulf/Atlantic","Pliocene","RsqrAdj"]
      
      numRows = len(dataList) +1 # add one because header is just a modified row
      numCols = len(dataList[0]) 
      
      csvBase = "/home/jcavner/Florida_Flora_WS/Florida_Flora_1800"
      pamCSV = os.path.join(csvBase,"pam_2532.csv")
      
      #app = QApplication(sys.argv)
      self.sheet = SpreadSheet(numRows, numCols, dataList, header, internal, pam, 
                               pamCSVPath=pamCSV, iface = self.iface)
      #sheet.setWindowIcon(QIcon(QPixmap(":/images/interview.png")))
      self.sheet.resize(640, 420)
      #sheet.show()
      #sys.exit(app.exec_()) 
      self.sheet.show()
      self.sheet.raise_() # !!!!
      self.sheet.activateWindow()    
# ........................................................................
   def turnAllWigetsOn(self):
      topRowCnt = self.hlayout.count()
      for eIdx in range(0,topRowCnt):
         if isinstance(self.hlayout.itemAt(eIdx),QWidgetItem):
            widget = self.hlayout.itemAt(eIdx).widget()
            if isinstance(widget,QPushButton):
               if not(widget.text() == 'See Leaves in Plot'):                  
                  widget.setEnabled(True)
      self.pamBut.setEnabled(True)
      self.clearSelectionBut.setEnabled(True)      
# ........................................................................
   def turnAllWidgetsOff(self):
      topRowCnt = self.hlayout.count()
      for eIdx in range(0,topRowCnt):
         if isinstance(self.hlayout.itemAt(eIdx),QWidgetItem):
            widget = self.hlayout.itemAt(eIdx).widget()
            if isinstance(widget,QPushButton):
               if not(widget.text() == 'Load Tree'):
                  widget.setEnabled(False)
      self.pamBut.setEnabled(False)
      self.clearSelectionBut.setEnabled(False)
            
         
      
# ........................................................................
   def getPam(self):
      # need filename and path
      success = False
      if self.expDir is not None:
         self.pamFilePath = os.path.join(self.expDir,'pam_%s.csv' % (str(self.bucketId)))
         if self.bucketId is not None and self.expId is not None:
            try:
               self.client.rad.getOriginalPamCsv(self.expId,self.bucketId,headers=True,filePath=self.pamFilePath) 
            except Exception, e:
               pass
            else:
               #print resp
               if os.path.exists(self.pamFilePath):
                  success = True              
      return success
   
# ........................................................................

   def buildCSVLayer(self):
      # turn self.pamFilePath into URI, for all platforms
      url = QUrl.fromLocalFile(self.pamFilePath)
      url.addQueryItem('delimiter',',')
      url.addQueryItem('xField','centerX')  # probably use a constant here
      url.addQueryItem('yField','centerY')  # probably use a constant here
      
      pLayer = QgsVectorLayer(url.toString(),"pam_%s" % (str(self.bucketId)),"delimitedtext")
      if not(pLayer.isValid()):
         pLayer = False
      else:
         crs = QgsCoordinateReferenceSystem()
         crs.createFromOgcWmsCrs('EPSG:%s'% (self.expEPSG))
         pLayer.setCrs(crs)
         
         self.renderer = self.buildRuleBasedRenderer(pLayer)
         self.renderer.rootRule().children()[0].setFilterExpression('sp_0 = -999')
         pLayer.setRendererV2(self.renderer)
         self.pamLayer = pLayer
         
      return pLayer
   
# ........................................................................
   def buildCSVLayer_withJoin(self):
      # turn self.pamFilePath into URI, for all platforms
      url = QUrl.fromLocalFile(self.pamFilePath)
      url.addQueryItem('delimiter',',')
      url.addQueryItem('xField','centerX')  # probably use a constant here
      url.addQueryItem('yField','centerY')  # probably use a constant here
      
      pLayer = QgsVectorLayer(url.toString(),"pam","delimitedtext")
      if not(pLayer.isValid()):
         pLayer = False
      else:
         crs = QgsCoordinateReferenceSystem()
         crs.createFromOgcWmsCrs('EPSG:%s'% (self.expEPSG))
         pLayer.setCrs(crs)
         ##############
         #self.renderer = self.buildRenderer(pLayer)
         #pLayer.setRendererV2(self.renderer)
         jlayer = self.findRetrieveStatsLyr(os.path.join(self.expDir,'stats'))
         #self.renderer = self.buildRenderer(pLayer,joinLyr=jlayer)
         #pLayer.setRendererV2(self.renderer)
         if jlayer:
            self.join = self.addJoin(pLayer,jlayer)
            if self.join:
               self.renderer = self.buildRenderer(pLayer, joinLyr = jlayer, noClasses = 0) # this is the most recent
               pLayer.setRendererV2(self.renderer)
               self.joinLayer = jlayer
               self.pamLayer = pLayer  # as a member for refresh
            else:
               player = False
               self.pamLayer = None
               self.joinLayer = None
         else:
            self.pamLayer = None
            self.joinLayer = None
            pLayer = False
      return pLayer

# ........................................................................
   def addPamToCanvas(self,downloaded):
      
      if downloaded:
         pamLayer = self.buildCSVLayer() # builds csv and adds join
         if pamLayer: 
            QgsMapLayerRegistry.instance().addMapLayer(pamLayer, False)  
            root = QgsProject.instance().layerTreeRoot() 
            root.insertLayer(0,pamLayer)
            ### uncomment this for stats mapped into ranges ##
            #self.setFieldsCombo(self.joinLayer)
            #self.fieldsCombo.setEnabled(True) 
            
            self.pamBut.setEnabled(False)
         else:
            ### uncomment this for stats mapped into ranges ##
            #self.fieldsCombo.setEnabled(False) 
            self.pamBut.setEnabled(True)
      else:
         ### uncomment this for stats mapped into ranges ##
         #self.fieldsCombo.setEnabled(False) 
         QMessageBox.warning(self,"status: ",
                            "Problem with PAM service")     
      self.bottomRighWidgetProgress.hide()      
      self.bottomRightWidgetCombo.show()
           
# ........................................................................
   def addPamToCanvas_old(self,downloaded):
      
      if downloaded:
         pamLayer = self.buildCSVLayer()
         if pamLayer: 
            QgsMapLayerRegistry.instance().addMapLayer(pamLayer)     
      self.bottomRighWidgetProgress.hide()
      if not(downloaded):  
         ### uncomment this for stats mapped into ranges ##
         #self.fieldsCombo.setEnabled(False)
         pass # take out for mapping stats into ranges
      else: 
         if pamLayer:
            ### uncomment this for stats mapped into ranges ##
            #self.setFieldsCombo(self.pamLayer,self.joinLayer)
            #self.fieldsCombo.setEnabled(True)
            pass
         else:
            #self.fieldsCombo.setEnabled(False)
            pass
      self.bottomRightWidgetCombo.show()

# ........................................................................
   def checkForPam(self):
      """
      @summary: checks for pam by name, returns bool or pam layer
      """
      mLRi = QgsMapLayerRegistry.instance()
      pamList = mLRi.mapLayersByName('pam_%s' % (str(self.bucketId)))
      if len(pamList) > 0:
         return pamList[0]
      else:
         return False
# ........................................................................
   def checkForJoins(self, pamLyr):
      """
      @summary: checks for joins on the pam, returns bool and joinLayer
      """
      lyrs = QgsMapLayerRegistry.instance().mapLayers()
      pamJoins = pamLyr.vectorJoins()
      statsLyrs = RADStatTypes.QGISLayerNames 
      existingStatJoin = False
      joinLayer = None
      if len(pamJoins) > 0:
         for join in pamJoins:
            if lyrs[join.joinLayerId].name() in statsLyrs:
               existingStatJoin = True
               joinLayer = lyrs[join.joinLayerId]
      return existingStatJoin, joinLayer   
# ....................................................................................
   def addNewTopLyr(self, vL):
      """
      @summary: adds vL to to map registry, finds the layer tree root and inserts
      at the top
      @param vL: QgsVectorLayer, shapegrid without pam or statistics
      """
      try:
         mLRi = QgsMapLayerRegistry.instance()
         root = QgsProject.instance().layerTreeRoot()
         mLRi.addMapLayer(vL,False)
         root.insertLayer(0,vL)
         self.iface.setActiveLayer(vL)  
      except:
         return False
      else:
         return True
   
# ........................................................................
   def moveLyrToTop(self,lyr):
            
      
                 
      newLyr = QgsVectorLayer(lyr.source(),'pam'+'_'+str(self.bucketId),'delimitedtext')      
      crs = QgsCoordinateReferenceSystem()
      crs.createFromOgcWmsCrs('EPSG:%s'% (self.expEPSG))
      newLyr.setCrs(crs)         
      self.renderer = self.buildRuleBasedRenderer(newLyr)
      self.renderer.rootRule().children()[0].setFilterExpression('sp_0 = -999')
      newLyr.setRendererV2(self.renderer)
                  
      root = QgsProject.instance().layerTreeRoot() 
      lyrToDelete = root.findLayer(lyr.id()) # returns a QgsLayerTreeLayer
      root.removeChildNode(lyrToDelete)  
      
      if self.addNewTopLyr(newLyr):      
         return newLyr
      else:
         return False
# ........................................................................      
   def setUpPam(self):
      """
      @summary: check for pam, activate pam layer or retrieve
      """
      # find pam by name from registry
      #mLRi = QgsMapLayerRegistry.instance()
      #pamList = mLRi.mapLayersByName('pam')

      pam = self.checkForPam()
      if pam:
         mvdLyr = False
         legend = self.iface.legendInterface()
         drawingOrderByName = [lyr.name() for lyr in legend.layers()]
         if pam.name() in drawingOrderByName:            
            if drawingOrderByName.index(pam.name()) != 0:               
               mvdLyr = self.moveLyrToTop(pam)
         if mvdLyr:
            pam = mvdLyr
         else:
            self.iface.setActiveLayer(pam)
            self.renderer = pam.rendererV2()
         self.pamLayer = pam
         
         
      else:
         if self.bottomRighWidgetProgress.isVisible():
            self.bottomRighWidgetProgress.hide()
            self.bottomRightWidgetCombo.show()           
         else: # get the pam and show progress while it is downloading
            self.bottomRighWidgetProgress.show()
            self.bottomRightWidgetCombo.hide()
            self.pamThread = TaskThread(self.iface.mainWindow(),self.getPam)
            self.pamThread.taskFinished.connect(self.addPamToCanvas) # might need to think about what to call here
            self.pamThread.start()
                                   
                         
# .........................................................................      
      
   def setJSONPath(self,iface,client,expId):
      """
      @summary: sets self.jsonPath based on workspace and expId
      @status: only used with demo experiments inside Qgis, that still have
      json folder
      """
      ######  workspace  and paths sets json path based on expId ###################
      self.workspace = Workspace(iface,client)
      if self.workspace.client == None: 
         self.workspace = False
      if self.workspace:
         self.projDir = self.workspace.getExpFolder(expId)
         if self.projDir:
            self.jsonPath = os.path.join(self.projDir,'json','json.json')
         else:
            self.jsonPath = False
      else:
         self.jsonPath = False
            # for testing outside of Qgis this will not have QSettings therefore
            # no current user, so no workspace, no exp folder
      #################################################    
# ...............................................................   
   def getProjDirectory(self, client, expId, interface = None):
      """
      @summary: returns the project directory
      @param interface: Qgis interface
      @param client: Lm Client object
      @param expId: experiment id
      """
      workspace = Workspace(interface,client) 
      projDir = workspace.getExpFolder(expId)
      return projDir      
# ...............................................................   
   def getOS(self):
      pluginOS = True
      if sys.platform == "win32":
         pluginOS = False
      return pluginOS
# ................................................................      
   def hideShowTips(self):
      """
      @summary: toggles between tool tips on docking button
      """
      if self.listdock.isVisible():
         self.more.setText("<")
         self.more.setToolTip("show tips")
         self.listdock.hide()
      else:
         self.more.setText(">")
         self.more.setToolTip("hide tips")
         self.listdock.show()  
# ................................................................      
   @pyqtSlot(str)
   def addList(self,leafs):
      """
      @summary: adds the leaves dock leaf widget
      """  
      leaves = json.loads(str(leafs))
      self.list.clear()
      #alphaNames = sorted([leaf['name'] for leaf in leaves.values()])
      
      inner = leaves.values()
      inner.sort(key=operator.itemgetter('name')) # sorts a list of dictionaries by a specific key
      
      #items = [SelectedResult(d["name"],d["x"],d["y"],d["pathId"],d["path"],length = d["length"]) 
      #          if d.has_key("length") else SelectedResult(d["name"],d["x"],d["y"],d["pathId"],d["path"]) 
      #          for d in inner]
      items = []
      for d in inner:
         result = SelectedResult(d["name"],d["x"],d["y"],d["pathId"],d["path"])
         if d.has_key("length"):
            result.setLength(d["length"])
         if d.has_key("mx"):
            result.setMatrix(d["mx"])
         items.append(result)                               
                 
      for item in items:
         SelectedItem(item,self.list)
      self.plotButton.setEnabled(True)
      self.calcMNTD()
# ....................................................................         
   def findNearest(self,matches,pathId):
      
      #print matches," ",pathId
      if len(matches) > 1:
         # have to find the shortest one
         shortestList = []        
         for matchList in matches: # goes through each of the match lists
            compare = 0
            for matchId in matchList:
               
               if matchId > pathId:
                  
                  length = float(self.allClades[str(matchId)]["length"])
                  compare = compare + length
               else:
                  shortestList.append(compare)
                  break
         shortest = min(shortestList)                                  
               
      elif len(matches) == 1:
         shortest = 0
         for matchId in matches[0]:
            if matchId > pathId:
               length = float(self.allClades[str(matchId)]["length"])
               shortest = shortest + length
            else:
               break
      return shortest
# ............................................................................      
   def findLengthToId(self,path,ancId):
      
      totLen = 0
      for pathId in path:
         if pathId > ancId:
            length = float(self.allClades[str(pathId)]["length"])
            totLen = totLen + length
         else:
            break
      return totLen
            
# .............................................................................   
   def calcMNTD(self):
      
      count = self.list.count()
      if count > 1:
         pathList = []
         for x in range(0,count):
            pl = self.list.item(x).path.split(',')  # self.list is model from dockable list?
            m  = map(int,pl)  # whole list, or everything minus itself pl[1:]
            pathList.append(m) # integers
         nearestTaxonLengths = []        
         for path in pathList:
            index = pathList.index(path)
            searchIn = list(pathList) 
            searchIn.pop(index)
            matches = []
            #print path[1:]
            for pathId in path[1:]:
               
               for srchPth in searchIn:
                  if pathId in srchPth[1:]:
                     matches.append(srchPth)
               if len(matches) > 0:
                  try:
                     nearestLen = self.findNearest(matches,pathId)                 
                     lengthToPathId = self.findLengthToId(path,pathId)
                  except:
                     return
                  else:   
                     nearestTaxonLengths.append(nearestLen+lengthToPathId)
                     break
         totAllLengths = sum(nearestTaxonLengths)
         meanNearestTaxonDist = totAllLengths/float(len(nearestTaxonLengths))
         roundedMNTD = round(meanNearestTaxonDist,5)
         self.mntdDisplay.setText('MNTD: '+str(roundedMNTD))
         
# ..................................................................
   def checkQgisVersion(self):
      return QGis.QGIS_VERSION_INT
# ..................................................................   
   def getFields(self ,layer):
      
      if layer is not None:
         try:
            dp = layer.dataProvider()
            fields = []
            for i in range(0,dp.fields().count()):
               name = dp.fields().field(i).name()
               fields.append(name)
            # fieldNameIndex('some name') # returns int
            fields.remove('siteid')
            fields.remove('centerX')
            fields.remove('centerY')
         except:
            fields = None
      else:
         fields = None
      return fields
# ..................................................................   
   def setFieldsCombo(self, joinLyr):   
      fields = self.getFields(joinLyr)
      if fields is not None:
         fieldNames = list(fields)
         for stat,name in zip(fields,fieldNames):
            self.fieldsCombo.addItem(name,userData=stat)
      else:
         self.fieldsCombo.setEnabled(False)
# ..................................................................      
   def addJoin(self, pamLyr, joinLyr):
      """
      @summary: gets the joins if a stats join doesn't exist 
      creates one
      """
      
      if not(self.checkForJoins(pamLyr)[0]):
         try:
            joinIdx = joinLyr.fieldNameIndex('siteid') # stats layer
            targetIdx = pamLyr.fieldNameIndex('siteid')
            joinLyrId = joinLyr.id()        
            joinInfo = QgsVectorJoinInfo()
            joinInfo.memoryCache = True 
            joinInfo.joinField = joinIdx
            joinInfo.joinLayerId = joinLyrId
            joinInfo.targetField = targetIdx
            pamLyr.addJoin(joinInfo)
         except:
            return False
         else:
            return True
      else:
         return True
     
      
# ..........................................................................
   def findRetrieveStatsLyr(self, pathName):
      # where is the pathName going to come from?
      mLRi = QgsMapLayerRegistry.instance()
      lyrs = mLRi.mapLayers()
      statsLyrs = RADStatTypes.QGISLayerNames
      # what if it doesn't have a stats layer
      statLyrExists = False
      for lyrId in lyrs.keys():
         if lyrs[lyrId].name() in statsLyrs:
            joinLyr = lyrs[lyrId]
            #joinLyr.setLayerName(joinLyr.name().replace(' ','_'))
            #joinLyrId = lyrId
            statLyrExists = True
            break
      if not(statLyrExists):
         try:
            self.client.rad.getPamSumShapegrid(pathName,
                                               self.expId, self.bucketId, 'original')
         except:
            joinLyr = False
         else:
            # have to unzip here and give new path
            zippath = os.path.dirname(str(pathName))
            z = zipfile.ZipFile(pathName,'r')
            for name in z.namelist():
               f,e = os.path.splitext(name)
               if e == '.shp':
                  shapename = name
               z.extract(name,str(zippath))
            shpPath = os.path.join(zippath,shapename)
            statsLyr = QgsVectorLayer(shpPath,'stats','ogr')
            if statsLyr.isValid():
               mLRi.addMapLayer(statsLyr,False) # private layer
               #riId = statsLyr.id()
               joinLyr = statsLyr
            else:
               joinLyr = False
      return joinLyr
               

# ..........................................................................
   def changeRenderer(self,index):
      """
      @summary: changes the the renderer according to field chosen from combo
      """
      if index != 0:
         currentStatidx = self.fieldsCombo.currentIndex()
         stat = str(self.fieldsCombo.itemData(currentStatidx, role=Qt.UserRole))
         if stat != '0':
            if self.pamLayer is not None and self.joinLayer is not None:
               self.renderer = self.buildRenderer(self.pamLayer,joinLyr = self.joinLayer, stat = stat)
               self.pamLayer.setRendererV2(self.renderer)
# ..........................................................................
   def buildRuleBasedRenderer(self, pamLyr):
      
      cl = Classify(pamLyr)
      gT = cl.GEOMETRY_POINT
      symbol = QgsSymbolV2.defaultSymbol(gT)
      symbol.setSize(1.4)
      renderer = cl.buildRuleBasedRenderer(symbol)    
      return renderer                       
# ..........................................................................      
   def buildRenderer(self, pamLyr, joinLyr = None, joinLyrName = None, stat = None, noClasses = None):
      """
      @summary: builds a graduated symbol renderer based
      on min and max from stats field
      """
      cl = Classify(pamLyr)
      if noClasses == None:
         cl.noClasses = 8
      else:
         cl.noClasses = noClasses
      # need min amd max here from spatial stats
      ##########################################
      mR = QgsMapLayerRegistry.instance()
      if joinLyrName is not None:
         statsLyr = mR.mapLayersByName(joinLyrName)[0]
      if joinLyr is not None:
         statsLyr = joinLyr
      if stat is None:
         fieldName = 'propspecDi'
      else:
         fieldName = stat     
      fieldIndex = statsLyr.fieldNameIndex(fieldName)     
      provider = statsLyr.dataProvider()     
      minimum = float(provider.minimumValue( fieldIndex ))
      maximum = float(provider.maximumValue( fieldIndex ))
      ###################################################
      
      gT = cl.GEOMETRY_POINT
      ranges = cl.buildRanges(gT, minimum, maximum)
      renderer = cl.buildEqualIntervalRenderer(ranges)
      return renderer   
# ...............................................................................
   def selectRangeFromCSV(self,item):
      
      if item.mtrxIdx is not None:
         fieldName = str(int(item.mtrxIdx))  # this will have to be changed after prod update                 
         expression = 'sp_%s  =  1' % (fieldName)         
         if self.renderer is not None:
            try:               
               self.renderer.rootRule().children()[0].setFilterExpression(expression)
               try:
                  self.pamLayer.triggerRepaint()                     
               except:
                  self.iface.mapCanvas().refresh()
            except Exception, e:
               pass
# ...............................................................................               
   def selectRangeFromCSV_withJoin(self,item):
      
      if self.join:  # not sure I need this
         if item.mtrxIdx is not None:
            fieldName = str(int(item.mtrxIdx))  # this will have to be changed after prod update
            
            currentStatidx = self.fieldsCombo.currentIndex()
            stat = str(self.fieldsCombo.itemData(currentStatidx, role=Qt.UserRole))
            statName = "%s_%s" % (self.joinLayer.name(),stat)
            expression = ' "sp_%s"  *  "%s" ' % (fieldName, statName)
            
            if self.renderer is not None:
               try:
                  
                  self.renderer.setClassAttribute(expression)
                  # in 2.4 need to do a triggerRepaint() on layer
                  try:
                     self.pamLayer.triggerRepaint()                     
                  except:
                     self.iface.mapCanvas().refresh()
               except Exception, e:
                  pass
# ............................................................................      
   def zoomItem(self,item):
      
      self.selectRangeFromCSV(item)
      
      self.view.page().mainFrame().evaluateJavaScript('zoomToLeaf("%s","%s", "%s");' % (item.dx,item.dy,item.pathId))
      
   def resizeEvent(self,resizeEvent):
      #print dir(resizeEvent)
      oy  = resizeEvent.oldSize().height()
      ox  = resizeEvent.oldSize().width()
      ny  = resizeEvent.size().height()
      nx  = resizeEvent.size().width()
      
      deltay = str(ny-oy)
      deltax = str(nx-ox)
      
      try:
         self.view.page().mainFrame().evaluateJavaScript('resizeCanvas("%s","%s");' % (deltax,deltay))
      except:
         pass
   
   def clearSelection(self):
      
      self.plotButton.setEnabled(False)
      self.mntdDisplay.clear()
      self.list.clear()
      self.view.page().mainFrame().evaluateJavaScript('clearSelection();')
      
   def reload(self):
      
      self.turnAllWigetsOn()
      self.plotButton.setEnabled(False)
      self.mntdDisplay.clear()
      self.list.clear()
      self.view.page().mainFrame().evaluateJavaScript('loadTree("%s","%s");' % (self.jsonUrl,self.closeId))


   def featuresSelectedInMap(self,selected,delselected,clearAndSelect):
      
      self.clearSelection()
      pamLyr = self.pamLyr
      pamLyr.removeSelection()
      pamLyr.select(selected)
      sfl = list(pamLyr.selectedFeatures())
      ll = [f.attributes()[3:] for f in sfl]
      a = np.array(ll)
      s = a.sum(axis=0)
      mtrxIdxs = np.where(s > 0)[0]
      mtrxIdxsList = list(mtrxIdxs)
      self.selectSpsTree(justMtrxIdx=mtrxIdxsList)
      
   def selectSpsTree(self, allmtrxIdxs=None, mtrxIdxsMask=None, justMtrxIdx=[], control=False):
      """
      @summary: selects species in the tree, from signal in plot
      @param allmtrxIdxs: all matrix Idxs
      @param matrxIdxsMask: boolean mask 
      """
      if allmtrxIdxs is not None and mtrxIdxsMask is not None:
         selectedMtrxIdxs = [m for b,m in zip(mtrxIdxsMask,allmtrxIdxs)  if b] # used to be, if b and m, but if mtrxIdx is 0 evaluates to False
      if len(justMtrxIdx) > 0:
         selectedMtrxIdxs = justMtrxIdx
      
      
      if not control:
         self.paths = []
         self.ids = []
         
      for spsDict in self.pilotList:
         if "mx" in spsDict:
            if spsDict["mx"] in selectedMtrxIdxs:
               self.paths.append(spsDict["path"])
               self.ids.append(spsDict["pathId"])
      # paths is a list of the paths as strings
      # ids is a list of the tips as strings
      
      # make a comma separated string of the tips
      tipsString = ','.join(self.ids)     
      
      # make a list of lists of the tipless paths 
      llTiplessPaths = [map(int,ps.split(',')[1:]) for ps in self.paths]                  
      pathsUnionList = list(set().union(*llTiplessPaths))
      pathsUnionList.sort(reverse=True)
            
      # now convert to a string
      unionString = ','.join(map(str,pathsUnionList))
      try:        
         self.view.page().mainFrame().evaluateJavaScript('findClades("%s","%s");' % (unionString,tipsString))
      except:
         pass
      
   def findClade(self):
      """
      @summary: finds a single clade in the tree, for the hint service search
      """
      
      currentIdx = self.findCladeCombo.currentIndex()   
      pathItem = self.findCladeCombo.itemData(currentIdx, role=Qt.UserRole)  # toString() won't work in QGIS 2.0
      spsName = str(self.findCladeCombo.currentText())
      
      # in QGIS returns unicode, from eclipse returns PyQt4.QtCore.QVariant
      if type(pathItem) == QVariant: # in eclipse use toString()
         path = str(pathItem.toString())         
      else:
         path = str(pathItem) # in Qgis, just cast unicode to string  
      
      if path != "None":   
         if "_" not in spsName:
            if self.genusDict.has_key(spsName):
               tipsString = self.genusDict[spsName][1]
               
               self.view.page().mainFrame().evaluateJavaScript('findClades("%s","%s");' % (path,tipsString))
            else:
               # Genus or single name at the tip level
      
               self.view.page().mainFrame().evaluateJavaScript('findClade("%s","%s");' % (path,spsName))
         else:            
            self.view.page().mainFrame().evaluateJavaScript('findClade("%s","%s");' % (path,spsName))
   
   def addGeneraToHintList(self):
     
      for genus in self.genusDict.keys():
         pathList = list(self.genusDict[genus][0])
         pathList.sort(reverse=True)
         pathStr = ','.join(map(str,pathList))
         gd = {}
         gd['name'] = genus
         gd['path'] = pathStr
         self.pilotList.append(gd)
         
   def calcNoDesc(self):
      """
      @summary: uses Counter from collections to group, and then sorts
      ,counts the number of times a pathId is in a path
      """
      self.noIdInPaths = Counter(self.repeatIds)
      # a list of tuples sorted by the second element in each tuple
      sortedFreq = sorted(self.noIdInPaths.iteritems(), key=operator.itemgetter(1),reverse=True)
      
      self.closeId = sortedFreq[2][0]
      
   
         
   def flattenTreeToTips(self, clade):
      """
      @summary: builds leaf list, and allClades (without children) dict
      """
      if "pathId" in clade:
         self.allClades[clade["pathId"]] = dict((k,v) for k,v in clade.items() if k != "children")
         self.repeatIds.extend(clade['path'].split(','))  # map(int,clade['path'].split(','))
      if "children" in clade:  
         for child in clade["children"]:
            self.flattenTreeToTips(child)
      else:
         # this means it is a tip
         #self.comboDataModel.append(clade) 
         self.tips.append(clade["pathId"])
         self.pilotList.append(clade)
         if "_" in clade["name"]:  # want to probably think about this
            genus = clade["name"].split("_")[0]
            pl    = clade["path"].split(',')
            tip   = clade["pathId"]
            m     = map(int,pl[1:]) 
            if genus in self.genusDict:           
               self.genusDict[genus][0].update(m)
               self.genusDict[genus][1] = '%s,%s' % (self.genusDict[genus][1],tip)
            else:
               self.genusDict[genus] = [set(m),tip]
      
# .......................................................................      
   def setModels(self):
      
      self.leafHintModel = CladeSearchListModel([], self)
      self.findCladeCombo.setModel(self.leafHintModel)
# ........................................................................      
   def setEventHandlers(self):
      
      # uninstalled backspace event handler Sept. 3, 2015      
      self.userEnters = EnterTextEventHandler(self.findCladeCombo,self.leafHintModel)
      
   def searchJSON(self,text):
      
      matchingDicts =  [v for i,v in enumerate(self.pilotList) if v['name'].startswith(text)]
      if len(matchingDicts) > 0:
         self.searchItems = [TreeSearchResult(d['name'],'','',d["path"]) for d in matchingDicts]
      else:
         self.searchItems = [TreeSearchResult('','','','')]
      self.leafHintModel.updateList(self.searchItems)


   def getIdxFromSearchItems(self,currentText):
      
      idx = 0
      # sO search result Object
      for sH in self.searchItems:
         if sH.name == currentText:
            break
         idx += 1
      return idx 
   
   def onTextChange(self, text):
      """
      @summary: connected to combobox
      @param text: str from combobox
      """
      noChars = len(text)
      if text == '':
         self.findCladeCombo.clear()
      if noChars >= 3:
         if "_" in text or " " in text:
            currText = self.findCladeCombo.currentText() # new on June 17 2015
            #currentIdx = self.findCladeCombo.currentIndex()
            #if currentIdx == -1:
            idx = self.getIdxFromSearchItems(currText)
            self.findCladeCombo.setCurrentIndex(idx)
            currentIdx = self.findCladeCombo.currentIndex()
            try:
               self.path = self.leafHintModel.listData[currentIdx].path # might want the path here, instead
            except:
               pass
            else:
               return
      else:
         self.searchJSON(text)
         

      
   def selectSpsPlot(self):
      """
      @summary: selects species in plot
      """
      #self.view.page().mainFrame().evaluateJavaScript('svg.selectAll("circle").style("fill", "#fff");') # for flare.html
      self.view.page().mainFrame().evaluateJavaScript('reportLeafs();') # for collapse
      
   
   def goBackToStats(self):
      if self.pamsumDialog is not None:
         self.pamsumDialog.show()
         
         
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
      helpDialog.scrollToAnchor('tree')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()   


class CladeSearchListModel(LmListModel):
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
         return self.listData[index.row()].path  
      else:
         return
          
 
      
      
# ................................................
class TreeList(QListWidget): #QListWidget #QListView
   def sizeHint(self):
      return QSize(155, 275)
# .................................................    
     
class SelectedResult(object):
   """
   @summary: Data structure for data model in dockable list
   """
   # .........................................   
   def __init__(self, name, x, y, pathId, path):
      """
      @summary: Constructor for SpeciesSearchResult object     
      """
      self.name = name
      self.dx = x
      self.dy = y
      self.pathId = pathId
      self.path = path
      self.length = None
      self.mtrxIdx = None
      
   def setMatrix(self,mtrxIdx):
      self.mtrxIdx = mtrxIdx
      
   def setLength(self,length):
      self.length = length
   # .........................................   
   def __str__(self):
      """
      @summary: Creates a string representation of the SelectedResult 
                   object
      """
      return "%s" % (self.name)         

class SelectedItem(QListWidgetItem):
   
   def __init__(self,result,parent):
      QListWidgetItem.__init__(self,result.name,parent,QListWidgetItem.UserType)
      self.dx = result.dx
      self.dy = result.dy
      self.path = result.path
      self.pathId = result.pathId
      self.length = result.length
      self.mtrxIdx = result.mtrxIdx

class TreeSearchResult(object):
   """
   @summary: Data structure for species search results in the tree json
   """
   # .........................................
   def __init__(self, name, mtrxId, treeId, path):
      """
      @summary: Constructor for SpeciesSearchResult object
      
      """
      self.name = name
      self.mtrxId = mtrxId
      self.treeId = treeId
      self.path = path  
      
      # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the TreeSearchResult 
                   object
      """
      return "%s" % (self.name)   
   

def main():
   app = QApplication(sys.argv)
   window = TreeWindow(None)
   
   window.show()
  
   
   sys.exit(app.exec_())
   
      
if __name__ == "__main__":
   
   main()
   
      