# -*- coding: utf-8 -*-
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
import os, sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from trees.common.lmHint import Hint, SpeciesSearchResult
from lifemapperTools.tools.radTable import RADTableModel


class Ui_Dialog(object):
   
   
   def setupUi(self):
      
      self.resize(915, 676)

      
      #############style############
      self.style = QStyleFactory.create("motif") # try plastique too!
      ##############################
      
      self.setMinimumSize(700,600)
      self.setMaximumSize(1988,1600)
      self.setSizeGripEnabled(True)
      
      self.makeOuterGrid()
      self.makeGroupBoxes()
      self.makeForm()
      self.filterGroup.setLayout(self.formContainer)
      self.container.addWidget(self.filterGroup,0,0,1,1)
      

   def makeOuterGrid(self):
      
      self.container = QGridLayout(self)
      self.container.setRowMinimumHeight(0,200)
      self.container.setRowMinimumHeight(1,450)

   def makeGroupBoxes(self):
      
      self.filterGroup = QGroupBox()
      self.filterGroup.setStyle(self.style)
      self.filterGroup.setTitle("Search Lifemapper Archive")
      
   def makeForm(self):
      # will contain filters and such to use for search 
      #self.formContainer = QGridLayout()
      self.formContainer = QVBoxLayout()
# ............................................................
class TableModel(RADTableModel):
   
   def __init__(self,model,headers):
      
      RADTableModel.__init__(self, model,headers,[],[])
      
      
   def data(self, index, role):
      #print self.data[index.row()]
      #if not index.isValid() or \
      #   not(0 <= index.row() < len(self.data)): 
      #   return
      #else:
      if role == Qt.DisplayRole:
         if index.column() == 0:
            return self.data[index.row()].displayName
         elif index.column() == 1:
            return self.data[index.row()].numPoints
         elif index.column() == 2:
            return self.data[index.row()].occurrenceSetId
         elif index.column() == 3:
            return self.data[index.row()].numModels
         elif index.column() == 4:
            return "download"
            
   def columnCount(self, parent): 
      return 5

   
   #def mimeData(self, *args, **kwargs):
   #   return RADTableModel.mimeData(self, *args, **kwargs)
   
   
   #
   #def flags(self, index):   
   #   # this seemed to be important if not subclassing view and putting drag in view subclass?
   #   #if index.column() in self.editIndexes and index.column() not in self.controlIndexes:     
   #   #   return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable  
   #   #elif index.column() in self.controlIndexes:
   #   #   return Qt.ItemIsEnabled | Qt.ItemIsSelectable   
   #   #  
   #   return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable
# ............................................................        


      
class LMTableView(QTableView):   
   
   def __init__(self):
      
      QTableView.__init__(self)
      
      
      # could set drag settings here
      
   #def dragMoveEvent(self, *args, **kwargs):
   #   # for dragging into I think
   #   print "dragging"
   #   return QTableView.dragMoveEvent(self, *args, **kwargs)
   #
   def mousePressEvent(self, event):
      print "mousePressEvent called"
      self.startDrag(event)
   
   def startDrag(self, event):
      print event
      print "startDrag called"
      index = self.indexAt(event.pos())
      if not index.isValid():
         return
      
      print "index valid ",index.row()
      drag = QDrag(self)
      
      mimeData = QMimeData()
      mimeData.setData("text/plain", self.model().data[index.row()].displayName)
      drag.setMimeData(mimeData)
      
      pixmap = QPixmap()
      pixmap = pixmap.grabWidget(self, self.visualRect(index))
      drag.setPixmap(pixmap)
      result = drag.start(Qt.MoveAction)

# test class to drop into
class LmEdit(QLineEdit):
   def __init__(self):
      QLineEdit.__init__(self)
      self.setAcceptDrops(True)
        
   def dropEvent(self, event):
      print "dropped ",event.mimeData().text()
      self.setText(event.mimeData().text())
      print "dropEvent called"
        
   def dragEnterEvent(self, event):
      print "in enter"
      if event.mimeData().hasFormat("text/plain"):
         event.accept()
      
   
class ArchiveBrowserDialog(QDialog, Ui_Dialog):

   def __init__(self, iface=None, inputs=None, client=None, email=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      
      self.setupUi() 
      self.client = client
      self.setUpHintService()
      self.formContainer.addWidget(self.hint.combo)
      # something to drag to test
      self.formContainer.addWidget(LmEdit())
      #
      self.table = self.setUpTable()
      self.container.addWidget(self.table, 1,0,1,1)

   def setUpHintService(self):
      
      self.hint = Hint(self.client, parent=self, callBack=self.callBack)

   def callBack(self, items):
      
      model = TableModel(items, self.header)
      self.table.setModel(model)
      self.table.resizeColumnsToContents()

   def setUpTable(self):
      
      tableView = LMTableView()
      tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
      
      # drag settings 
      tableView.setDragEnabled(True) 
      tableView.setDragDropMode(QAbstractItemView.DragOnly) # does it need this and dragEnabled?
      
      
      tableView.horizontalHeader().setStretchLastSection(True)
      self.header = ['name','No. Pts','occ id','models','download']
      data = [SpeciesSearchResult('','','','')]
      self.tableModel = TableModel(data,self.header)
      tableView.setModel(self.tableModel)
      
      return tableView
      


if __name__ == "__main__":
#  
   import_path = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/lifemapperTools/"
   sys.path.append(os.path.join(import_path, 'LmShared'))
   configPath = os.path.join(import_path, 'config', 'config.ini') 
   os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
   
   from LmClient.lmClientLib import LMClient
   
   client =  LMClient()
   client.login(userId='Dermot', pwd='Dermot')
   
   qApp = QApplication(sys.argv)
   d = ArchiveBrowserDialog(None,client=client)
   d.show()
   sys.exit(qApp.exec_()) 






















































