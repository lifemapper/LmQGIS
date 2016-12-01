
import sys, os
import logging
import cPickle
import csv
import numpy as np
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
from lifemapperTools.tools.MultiSps.common.navigation import NavTreeView,NavTreeModel,NavTreeItem, NavigationListItem
from lifemapperTools.tools.MultiSps.User_BOOM import archive
from lifemapperTools.tools.MultiSps.MCPA import mcpa
from lifemapperTools.tools.MultiSps.layers import layers
from lifemapperTools.tools.MultiSps.common.plots import PlotWindow
from lifemapperTools.tools.MultiSps.common.localConstants import ListNav,FloderNav


class Ui_Dialog(object):
   
      def setupUi(self):
         self.resize(748, 410)   # orgin 648, 410
         self.setMinimumSize(698, 470)
         self.setMaximumSize(998, 770)
         self.setSizeGripEnabled(True)
         
         self.mainLayout = QHBoxLayout(self)
         
         
         self.setUpStackedWidgets()
         
      def setUpGridSetContentsPage(self):
         
         self.gridSetContentsPage = QWidget()
         self.contentsLayout = QHBoxLayout(self.gridSetContentsPage)
         

      def setUpGridSetpListingPage(self):
         """
         @summary: sets up listing page, will need to be searchable
         """
         self.GridSetListingPage = QWidget() # self.searchPage = QWidget()
         self.listLayout = QVBoxLayout(self.GridSetListingPage)  # VBox so we can put a search combo on the top of it
         self.listLayout.addWidget(self.searchController.projectCanvas)

      def setUpStackedWidgets(self):
         self.stackedWidget = QStackedWidget()
         self.setUpGridSetpListingPage()
         self.setUpGridSetContentsPage()
         
         self.stackedWidget.addWidget(self.GridSetListingPage)
         self.stackedWidget.addWidget(self.gridSetContentsPage)
         
         
         
         
         self.mainLayout.addWidget(self.stackedWidget)



     





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
      
      
   def drillDown(self,IconIndex):
         
         print "drill down ",IconIndex.row()
         print self.searchController.archiveModel.listData[IconIndex.row()].name
         self.stackedWidget.setCurrentWidget(self.gridSetContentsPage)
      
if __name__ == "__main__":
   
   qApp = QApplication(sys.argv)
   d = MultiSpsDialog(None)
   d.show()
   sys.exit(qApp.exec_())