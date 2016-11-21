import sys, os
import logging
import cPickle
import csv
import numpy as np
from PyQt4.Qt import QVBoxLayout
try: import simplejson as json 
except: import json
from collections import Counter
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from lifemapperTools.tools.radTable import *
from lifemapperTools.common.lmListModel import LmListModel
from lifemapperTools.common.lmHint import Hint, SpeciesSearchResult
from lifemapperTools.tools.MultiSps.Grids import grid
from lifemapperTools.tools.MultiSps.common.navigation import NavTreeView,NavTreeModel,NavTreeItem
from lifemapperTools.tools.MultiSps.User_BOOM import archive
from lifemapperTools.tools.MultiSps.MCPA import mcpa
from lifemapperTools.tools.MultiSps.layers import layers
from lifemapperTools.tools.MultiSps.common.plots import PlotWindow
from lifemapperTools.common.LmQTree import TreeItem



class NavigationItem(QListWidgetItem):
   
   def __init__(self,result,parent,reds=[],blues=[],rowIdx=0,page=None):
      QListWidgetItem.__init__(self,result[0],parent,QListWidgetItem.UserType)
      
      
      self.page = result[1]
      #if self.pathId in reds:
      #   self.setBackground(Qt.red) # sets red backdround
      #   #parent.setItemDelegateForRow(rowIdx,SelectedDelegate(Qt.red))  # doesn't work right now
      #if self.pathId in blues:
      #   self.setBackground(Qt.cyan)



class Ui_Dialog(object):
   
      def setupUi(self):
         self.resize(698, 410)   # orgin 648, 410
         self.setMinimumSize(698, 470)
         self.setMaximumSize(998, 770)
         self.setSizeGripEnabled(True)
         
         self.mainLayout = QHBoxLayout(self)
         #self.gridController = grid.GridController()
         self.setUpTabs(stackedWidget=True)
         
      def handle(self,index):
         
         #print "double index ",index
         pass
      
      def setUpStackedFolderView(self):
         
         self.folderTreeView = NavTreeView(None,dialog=self, stackedWidget= self.stackedWidget)#, parent = self.folderPage)
         self.folderTreeView.setMinimumWidth(198)
         self.folderTreeView.doubleClicked.connect(self.handle)
         #self.folderTreeView = QTreeView()
         self.folderModel = NavTreeModel(top='Multi Species Analysis') # 'Africa Mammals PAM'
         self.folderTreeView.setModel(self.folderModel)
         self.folderTreeView.setObjectName("folderTreeView")
         
         #[self.plots,self.layersPage,self.mcpaPage,self.searchPage,self.gridPage]
         MCPAFolder = NavTreeItem("MCPA","MCPA",self.folderModel.provider)
         RawMCPA = NavTreeItem("prepared inputs","prepared inputs",MCPAFolder,page=self.mcpaPage)
         
         RADFolder = NavTreeItem("RAD","RAD",self.folderModel.provider)
         RawRAD = NavTreeItem("prepared inputs","prepared inputs",RADFolder)
         
      
      def setUpStackedWidgets(self): 
         pass 
      
      def navigateToPanel(self, item):
         
         self.stackedWidget.setCurrentWidget(item.page)
      
      
      def setUpNavigation(self,folder=True):
         if not folder:
            self.navList = QListWidget()
            self.navList.setMinimumWidth(188)
            self.navList.itemClicked.connect(self.navigateToPanel)
            #[self.plots,self.layersPage,self.mcpaPage,self.searchPage,self.gridPage]
            TTips = ["Range Diveristy Plots","Search/Attach Trees to Layers","Build MCPA","Search Archive","Build Grid"]
            for res in zip(["Range Diveristy Plots","Search/Attach Trees to Layers","Build MCPA","Search Archive","Build Grid"],self.allPages,TTips):
               navItem = NavigationItem(res, self.navList, QListWidgetItem.UserType)
               navItem.setToolTip(res[2])
         else:
            self.setUpStackedFolderView()
            self.navList = self.folderTreeView
         return self.navList
         
      def setUpTabs(self, stackedWidget=False):
         
         if not stackedWidget:
            self.tabWidget = QTabWidget()
            self.tabWidget.currentChanged.connect(self.tabChanged)
            
         else:
            self.stackedWidget = QStackedWidget()
         
         ### Grid ###
         self.gridPage = QWidget()
         self.gridLayout = QHBoxLayout(self.gridPage)
         self.bbox = self.gridController.bboxEdit()  # can get Ui components from controller
         self.resolutionControls = self.gridController.resolutionVBox()
         self.gridLayout.addWidget(self.bbox)
         self.gridLayout.addWidget(self.resolutionControls)
         ##########
         ##########
         self.searchPage = QWidget()
         self.HorizSearch = QHBoxLayout(self.searchPage)
         
         self.searchLayout = QVBoxLayout()
         self.searchCombo,list = self.searchController.hintBox(parent = self.searchController.parent)
         self.searchLayout.addWidget(self.searchCombo.combo)
         self.searchLayout.addWidget(list)
         
         ### PAM listing 
         self.listLayout = QVBoxLayout()
         self.listButLayout = QHBoxLayout()
         self.listButLayout.addWidget(self.searchController.newButton(newButController=self.searchController.createNewPAM))
         two = QPushButton()
         two.setAutoDefault(False)
         three = QPushButton()
         three.setAutoDefault(False)
         self.listButLayout.addWidget(two)
         self.listButLayout.addWidget(three)
         
         self.listLayout.addLayout(self.listButLayout)
         self.listLayout.addWidget(self.searchController.projectCanvas)
         
         
         self.HorizSearch.addLayout(self.searchLayout)
         self.HorizSearch.addLayout(self.listLayout)
         ##############
         ##############
         
         # MCPA Page
         
         self.mcpaPage = QWidget()
         self.horizMCPALyOut = QHBoxLayout(self.mcpaPage)
         self.horizMCPALyOut.addWidget(self.mcpaController.inputEdits(parent=self))
         self.horizMCPALyOut.addLayout(QVBoxLayout())
         
         ############
         # PA Layers Trees?
         self.layersPage = QWidget()
         self.layersVLayout = QVBoxLayout(self.layersPage)
         addLayerControls, outPutGroup,treeGroup = self.layersController.setupUi()
         self.layersVLayout.addLayout(self.layersController.treeControls) #(self.layersController.localTreeRadio())
         self.layersVLayout.addWidget(treeGroup)
         self.layersVLayout.addWidget(addLayerControls)
         
         
         ##############
         ### plots ##
         
         self.plots = QWidget()
         self.plotLayout = QHBoxLayout(self.plots)
         
         
         X = np.random.rand(700, 1000)
         xs = np.mean(X, axis=1)
         ys = np.std(X, axis=1)
         aw = PlotWindow(xs,ys,'dfas','hh','etertera','/home/jcavner')
         
         self.plotLayout.addWidget(aw)
         ##############
         
         self.stats = QWidget()
         self.statsLaYOUT = QHBoxLayout(self.stats)
         
         
         self.allPages = [self.plots,self.layersPage,self.mcpaPage,self.searchPage,self.gridPage]
         ##############
         if not stackedWidget:         
            self.tabWidget.addTab(self.searchPage, 'Search')
            self.tabWidget.addTab(self.gridPage, 'Grids')
            self.tabWidget.addTab(self.plots,"plots")
            self.tabWidget.addTab(self.mcpaPage,"mcpa")
            self.tabWidget.addTab(self.layersPage,"layers")
            
            self.mainLayout.addWidget(self.tabWidget)
         else:
            self.stackedWidget.addWidget(self.searchPage)
            self.stackedWidget.addWidget(self.gridPage)
            self.stackedWidget.addWidget(self.plots,)
            self.stackedWidget.addWidget(self.mcpaPage)
            self.stackedWidget.addWidget(self.layersPage)
            self.mainLayout.addWidget(self.setUpNavigation())
            self.mainLayout.addWidget(self.stackedWidget)
         



      def tabChanged(self,pageIdx):
      
         print pageIdx
         
         


        
class MultiSpsDialog(QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   #__metaclass__ = classmaker()
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, inputs=None, client=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      
      self.setWindowTitle("Multi-Species")
      self.gridController = grid.GridController()  # get controller before setting up UI
      # or get it in setupUI() before setting up tabs
      
      self.searchController = archive.UserArchiveController(parent=self)
      
      self.mcpaController = mcpa.MCPA_Controller()
      
      self.layersController = layers.LayerController(None)
      
      self.setupUi()
      
      #print "check controller ",self.gridController._checkBoundingBox()  # 
      



































      
if __name__ == "__main__":
   
   qApp = QApplication(sys.argv)
   d = MultiSpsDialog(None)
   d.show()
   sys.exit(qApp.exec_())