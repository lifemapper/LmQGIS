import sys, os
import logging
import cPickle
import csv
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




class Ui_Dialog(object):
   
      def setupUi(self):
         self.resize(698, 410)   # orgin 648, 410
         self.setMinimumSize(698, 470)
         self.setMaximumSize(998, 770)
         self.setSizeGripEnabled(True)
         
         self.mainLayout = QGridLayout(self)
         #self.gridController = grid.GridController()
         self.setUpTabs()
         
         

      def setUpTabs(self):
         self.tabWidget = QTabWidget()
         
         ### Grid ###
         self.gridPage = QWidget()
         self.gridLayout = QHBoxLayout(self.gridPage)
         self.bbox = self.gridController.bboxEdit()  # can get Ui components from controller
         self.gridLayout.addWidget(self.bbox)
         ##########
         
         
         self.tabWidget.addTab(self.gridPage, 'Grids')

         self.mainLayout.addWidget(self.tabWidget)






        
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
      
      self.setupUi()
      
      #print "check controller ",self.gridController._checkBoundingBox()  # 
      



































      
if __name__ == "__main__":
   
   qApp = QApplication(sys.argv)
   d = MultiSpsDialog(None)
   d.show()
   sys.exit(qApp.exec_())