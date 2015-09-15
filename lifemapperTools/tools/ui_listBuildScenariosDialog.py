"""
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
import os.path
from collections import Counter, defaultdict
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from LmClient.lmClientLib import LMClient
from lifemapperTools.tools.ui_postScenario import PostScenarioDialog
from lifemapperTools.common.communicate import Communicate




class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(700, 400)
      self.setMinimumSize(700,400)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout_input.setRowMinimumHeight(0,30)
      self.gridLayout_input.setRowMinimumHeight(1,350)
      self.gridLayout_input.setRowMinimumHeight(2,40)
      
      
      
      ############  group SCENARIOS #######################################
      
      self.scenarioGroup = QtGui.QGroupBox()
      self.scenarioGroup.setObjectName("scenarioGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.scenarioGroup.setStyle(self.style)
      self.scenarioGroup.setTitle("Environmental Layer Set")
      
      self.scenLayout = QtGui.QGridLayout()
      self.scenLayout.setRowMinimumHeight(0,10)
      self.scenLayout.setRowMinimumHeight(1,20)
      self.scenLayout.setRowMinimumHeight(2,280)
      self.scenLayout.setRowMinimumHeight(3,10)
      self.scenLayout.setColumnMinimumWidth(0,10)
      self.scenLayout.setColumnMinimumWidth(1,230)
      self.scenLayout.setColumnMinimumWidth(2,10)
      self.scenLayout.setColumnMinimumWidth(3,230)
      self.scenLayout.setColumnMinimumWidth(4,10)
      
      self.modelScenLabel = QtGui.QLabel("layer sets to create model with")
      self.modelScenLabel.setMaximumHeight(35)
      self.modelScenCombo = QtGui.QComboBox()
      
      self.modelScenCombo.currentIndexChanged.connect(self.populateProjScenCombo)
      
      self.projScenLabel = QtGui.QLabel("matching layer sets to map on")
      self.projScenLabel.setMaximumHeight(35)
      self.projectionScenListView = QtGui.QListView()
      self.projectionScenListView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
      self.projectionScenListView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
     
      self.projectionScenListView.clicked.connect(self.matchNew)
      
      self.scenLayout.addWidget(self.modelScenLabel,1,1,1,1)
      self.scenLayout.addWidget(self.modelScenCombo,2,1,1,1,QtCore.Qt.AlignTop)
      self.scenLayout.addWidget(self.projScenLabel, 1,3,1,1)
      self.scenLayout.addWidget(self.projectionScenListView,2,3,1,1,QtCore.Qt.AlignTop)
      
      self.scenarioGroup.setLayout(self.scenLayout)
      
      self.gridLayout_input.addWidget(self.scenarioGroup,1,0,1,1)
      ##############################################################################
      
     
      self.gridLayout.addLayout(self.gridLayout_input,0,0,1,1)
      
      
      
      self.helpBut = QtGui.QPushButton("?")
      self.helpBut.setMaximumSize(30, 30)
      
      self.acceptBut = QtGui.QPushButton("OK")
      self.rejectBut = QtGui.QPushButton("Close")
      
    
      self.rejectBut.clicked.connect(self.reject)
      self.helpBut.clicked.connect(self.help)
      
      self.buttonBox = QtGui.QDialogButtonBox()
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      #self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)

      self.gridLayout.addWidget(self.buttonBox,   8,0,1,3)

      self.setWindowTitle("Upload Environmental Layer Sets")

class ListBuildScenariosDialog(QtGui.QDialog, Ui_Dialog):   
   
   def __init__(self, match=False, client=None, scenarioId=None):
      QtGui.QDialog.__init__(self)
      self.client = client
      self.setupUi()
      
      
      self.scenProjListModel = LmListModel([], self)
      self.scenModelListModel = LmListModel([],self,model=True)
      self.projDelegate = SDMDelegate()
      self.modelDelegate = SDMDelegate()
      # set models and delegates for projections
      self.projectionScenListView.setModel(self.scenProjListModel)
      self.modelScenCombo.setModel(self.scenModelListModel)
      self.projectionScenListView.setItemDelegateForRow(0,self.projDelegate)     
      self.modelScenCombo.setItemDelegate(self.modelDelegate)
      
      
      Communicate.instance().postScenarioFailed.connect(self.setModelCombo)
      Communicate.instance().postedScenario.connect(self.refreshScenarios)
      
      
      self.populateModelScenCombo() 
   
   # ......................................................................................    
   def refreshScenarios(self,postedScenId,match):  
   
      if match:
         currentModelIdx = self.modelScenCombo.currentIndex()
         self.populateProjScenCombo(currentModelIdx)
      else:     
         self.populateModelScenCombo(newScenId=int(postedScenId))
         
   def setModelCombo(self,match):
      if not match:
         self.modelScenCombo.setCurrentIndex(0) 
         
   # ..............................................................................          
    
   def populateModelScenCombo(self,newScenId=None):
      """
      @summary: populates the model scenario combo
      @param preserveCurrentIdx: idx to set combo to usually after repopulating
      """
      
      self.modelScenCombo.clear()
      #self.scenModelListModel.updateList([ScenarioSearchResult('','')])
      try:
         scenarios = self.client.sdm.listScenarios(keyword=['observed'])
      except:
         QMessageBox.warning(self,"Error: ",
              "Problem with the scenario listing service")
      else:
         
         items = []
         items.append(ScenarioSearchResult('','select'))
         items.append("<a href='www.fake.fake'>build new modeling layer set</a>")
         for scen in scenarios:
            try:
               str(scen.title)
            except:
               title = str(int(scen.id))
            else:
               title = str(scen.title)
            items.append(ScenarioSearchResult(title,int(scen.id)))
         self.scenModelListModel.updateList(items)
         if newScenId is None:
            self.modelScenCombo.setCurrentIndex(0)
         else:
            #newScenIdx = self.modelScenCombo.findData(newScenId, role=Qt.UserRole)
            # using this loop against the data model since UserRole doesn't always apply
            for idx, resultObj in enumerate(self.scenModelListModel.listData):
               try:
                  scenId = int(resultObj)
               except:
                  newScenIdx = 0
               else:
                  if scenId == newScenId:
                     newScenIdx = idx
                     break
                  else:
                     newScenIdx = 0
            self.modelScenCombo.setCurrentIndex(newScenIdx)  
      
   def populateProjScenCombo(self, index):
      """
      @summary: connected to currentIndexChanged signal on modelScen combo
      populates the QListView for projection scenarios
      @param index: current index from the model scenario combo
      """
      # get the model Scen Id using the index
      #print index
      # what happens if there are no matching scenarios?
      if index != 0 and index != 1:
            modelScenId = self.modelScenCombo.itemData(index, role=Qt.UserRole)
            try:  
               matchingScens = self.client.sdm.listScenarios(matchingScenario=modelScenId)
            except:
               QMessageBox.warning(self,"Error: ",
                 "Problem with the scenario listing service")
            else:
               items = []
               items.append("<a href='www.fake.fake'>build new matching layer set</a>")
               for scen in matchingScens:
                  items.append(ScenarioSearchResult(scen.title,int(scen.id)))
               self.scenProjListModel.updateList(items)
      elif index == 1:
            self.scenProjListModel.updateList([ScenarioSearchResult('','')])
            self.postScenarioDialog = PostScenarioDialog(client=self.client)
            self.postScenarioDialog.exec_()          
      else:
            self.scenProjListModel.updateList([ScenarioSearchResult('','')]) 
   
   def matchNew(self, index):
      """
      @summary: opens up a dialog to match a layer set using the current index from
      the modelScenCombo
      @param index: index from the projection QListView for projection layer sets
      """
      if index.row() == 0:
         # get the id of model scenario
         currindex = self.modelScenCombo.currentIndex()
         modelScenId = self.modelScenCombo.itemData(currindex, role=Qt.UserRole)
         self.postScenarioDialog = PostScenarioDialog(match=True,scenarioId=modelScenId,client=self.client)
         self.postScenarioDialog.exec_()          

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
      helpDialog.scrollToAnchor('buildEnvlayerSet')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 

# .............................................................................
class LmListModel(QAbstractListModel):
   """
   @summary: List model used by Lifemapper Qt listing widgets
   @note: Inherits from QtCore.QAbstractListModel 
   """
   # .........................................
   def __init__(self, listData, parent=None, model=False, *args):
      """
      @summary: Constructor for LmListModel
      @param listData: List of objects to insert into list
      @param parent: (optional) The parent of the LmListModel
      @param model: bool, whether or not data model is for modeling layer set
      @param args: Additional arguments to be passed
      """
      QAbstractListModel.__init__(self, parent, *args)
      self.listData = listData
      self.model = model
      
   # .........................................
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
            try: return self.listData[index.row()].customData()
            except: return self.listData[index.row()]
      if index.isValid() and role == Qt.UserRole:
         return int(self.listData[index.row()])
      else:
         return 
      
   # .........................................
   def rowCount(self, parent=QModelIndex()):
      """
      @summary: Returns the number of rows in the list
      @param parent: (optional) The parent of the object
      @return: The number of items in the list
      @rtype: Integer
      """
      return len(self.listData)
   
   # .........................................
   def updateList(self, newList):
      """
      @summary: Updates the contents of the list
      @param newList: A list of items to use for the new list
      @note: The provided list will replace the old list 
      """
      self.beginInsertRows(QModelIndex(), 0, len(newList))
      self.listData = newList
      
      self.endInsertRows()
      
class SDMDelegate(QStyledItemDelegate):
   
   def __init__(self, parent=None, *args):
      QItemDelegate.__init__(self, parent, *args)
      
      
   def paint(self, painter, option, index):
      
      text = index.model().listData[index.row()]
      
      if not(isinstance(text,ScenarioSearchResult)):
         painter.save()
         document = QTextDocument()
         document.setDefaultFont(option.font)      
         document.setHtml(text)
         painter.translate(option.rect.x(), option.rect.y()-3)
         document.drawContents(painter)
         painter.restore()
     
      else:
         QStyledItemDelegate.paint(self, painter, option, index)
         
class ScenarioSearchResult(object):
   """
   @summary: Data structure for ScenarioSearchResult
   """
   # .........................................
   def __init__(self, title, id):
      """
      @summary: Constructor for ScenarioSearchResult object
      @param title: The display name for scenario
      @param id: The Lifemapper scenario id
      """
      self.scenId = id
      self.scenTitle = title
      
   def customData(self):
      """
      @summary: Creates a string representation of the ScenarioSearchResult 
                   object
      """
      return "%s" % (self.scenTitle)
   
   def __int__(self):
      
      return self.scenId







if __name__ == "__main__":
#  
   client =  LMClient(userId='', pwd='')
   qApp = QtGui.QApplication(sys.argv)
   #d = testDialog(match=True,scenarioId=112,client=client)
   d = ListBuildScenariosDialog(client=client)
   d.show()
   sys.exit(qApp.exec_())