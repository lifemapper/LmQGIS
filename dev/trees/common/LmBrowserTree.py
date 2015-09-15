import sys, os
import random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from dev.trees.common.lmHint import Hint, SpeciesSearchResult


class BrowserTreeModel(QAbstractItemModel):

   def __init__(self):
      QAbstractItemModel.__init__(self)
      
      self.headers = ['sps','AlgOcc','proj']
      self.columns = 3
      self.root = TreeItem("Root", "Root", parent = None)
      self.provider = TreeItem("Lifemapper","Lifemapper",self.root)
      
   
   # ----------  change data
   def emitDataChanged(self):
      # this doesn't work
      #print "emitting change"
      self.dataChanged.emit(QModelIndex(), QModelIndex())
      
   def insertRow(self, row, parent):
      return self.insertRows(row, 1, parent)


   def insertRows(self, row, count, parent):
      self.beginInsertRows(parent, row, (row + (count - 1)))
      self.endInsertRows()
      return True


   def removeRow(self, row, parentIndex):
      return self.removeRows(row, 1, parentIndex)


   def removeRows(self, row, count, parentIndex):
      
      self.beginRemoveRows(parentIndex, row, row)
      node = self.nodeFromIndex(parentIndex)
      node.removeChild(row)
      self.endRemoveRows()
   
      return True
   # ----------  end change data
   
   # ---------- new update data, Sept 14, 2015
   def updateList(self,newList):
      
      self.beginInsertRows(QModelIndex(), 0, len(newList))
      self.data = newList
      self.endInsertRows()   
      
   # -----------
   
   def headerData(self, section, orientation, role):
      if orientation == Qt.Horizontal and role == Qt.DisplayRole:
         return QVariant(self.headers[section])
      return QVariant()
   
   def flags(self, index):
      defaultFlags = QAbstractItemModel.flags(self, index)
      if not self.hasChildren(index):
         return Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable
      return defaultFlags
   
   def index(self, row, column, parentIndex):
      node = self.nodeFromIndex(parentIndex)
      return self.createIndex(row, column, node.child(row))
   
   def nodeFromIndex(self, index):
      
      return index.internalPointer() if index.isValid() else self.root
   
   def parent(self, child):
      # get parent from child index
      if not child.isValid():
         return QModelIndex()
      
      node = self.nodeFromIndex(child)
      
      if node is None:
         return QModelIndex()
      
      parent = node.parent
         
      if parent is None:
         return QModelIndex()
      
      
      grandparent = parent.parent  # attribute on item instance
      if grandparent is None:
         return QModelIndex()
      row = grandparent.rowOfChild(parent)
      
      assert row != - 1  #  is throwing intermittent error
      return self.createIndex(row, 0, parent)
      
      #if not index.isValid():
      #      return QModelIndex()
      #
      #childItem = index.internalPointer()
      #parentItem = childItem.parent()
      #
      #if parentItem == self.rootItem:
      #   return QtCore.QModelIndex()
      #
      #return self.createIndex(parentItem.row(), 0, parentItem)
   
   def columnCount(self, parent):
      return self.columns


   def rowCount(self, parent):
      node = self.nodeFromIndex(parent)
      if node is None:
         return 0
      return len(node)
   
   def data(self, index, role):
      if role == Qt.DecorationRole:
         return QVariant()
             
      if role == Qt.TextAlignmentRole:
         return QVariant(int(Qt.AlignTop | Qt.AlignLeft))
      
      if role != Qt.DisplayRole:
         return QVariant()
      
              
      node = self.nodeFromIndex(index)
      #
      if index.column() == 0:
         try:
            return QVariant(node.name)
         except:
            return QVariant('')
      


class TreeItem(object):
   
   # --- class for tree items
   
   def __init__(self, data, name, parent=None):
      
      self.name = name
      self.parentItem = parent
      self.itemData = data
      self.childItems = []
      self.setParent(parent)
   
   def setParent(self, parent):
      if parent != None:
         self.parent = parent
         self.parent.appendChild(self)
      else:
         self.parent = None
      
   def appendChild(self, item):
      self.childItems.append(item)
   
   # ---------- from, http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/itemviews/simpletreemodel/simpletreemodel.py
   def child(self, row):
      # get called from index() in model
      try:
         return self.childItems[row]
      except:
         pass
   
   def childCount(self):
      return len(self.childItems)
   
   def data(self, column):
      # not using this, doesn't need it for single data
      # attached to instance of item
      try:
         return self.itemData[column]  # not a list, but could be
      except IndexError:
         return None
   
   def getParent(self):  # changed this because "parent" was both a method and attribute
      return self.parentItem
   
   def row(self):
      if self.parentItem:
         return self.parentItem.childItems.index(self)   
      return 0
   # ---------------- end 
   
   def childAtRow(self, row):
      # !!!!!!! same as child
      return self.childItems[row]
   
   def rowOfChild(self, child):       
      for i, item in enumerate(self.childItems):
         if item == child:
               return i
      return -1
   
   def removeChild(self, row):
      try:
         value = self.childItems[row]
         self.childItems.remove(value)
      except Exception, e:
         print "row not removed ", row, " ",str(e)
   
   def __len__(self):
      return len(self.childItems)
   
class LMTreeView(QTreeView):
   
   def __init__(self, parent):
      
      QTreeView.__init__(self,parent)
      self.header().hide()
      self.dragEnabled()
      self.setDragDropMode(QAbstractItemView.DragOnly)
      self.header().setResizeMode(QHeaderView.ResizeToContents)
      
   
   def startDrag(self, *args, **kwargs):
     
      # can a I start a thread? and have it continue to drag?
       
      drag = QDrag(self)  
      mimeData = QMimeData()
      sis = self.selectionModel().selectedIndexes()
      itemIdx = sis[0]
      #print "row of child ",itemIdx.row()
      childRowIdx = itemIdx.row()
      #print "row of parent ",itemIdx.parent().row() #row of parent
      #print "parent node ",self.model().nodeFromIndex(itemIdx.parent()) # actual parent node
      #print "data of child at 0 idx of parent ", self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData # 
      occSetId = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      
      # will use "text/uri-list" for dragging onto canvas
      mimeData.setData("text/uri-list", "/home/jcavner/%s.shp" % (occSetId))
      drag.setMimeData(mimeData)   
      pixmap = QPixmap()
      pixmap = pixmap.grabWidget(self, self.visualRect(itemIdx))
      drag.setPixmap(pixmap)
      result = drag.start(Qt.MoveAction)
      #return QTreeView.startDrag(self, *args, **kwargs)
      
class LmEdit(QLineEdit):
   def __init__(self):
      QLineEdit.__init__(self)
      self.setAcceptDrops(True)
        
   def dropEvent(self, event):
      #print "dropped ",event.mimeData().text()
      print dir(event.mimeData())
      self.setText(str(event.mimeData().urls()))  #urls() retiurns list, uri-list 
      #print "dropEvent called"
        
   def dragEnterEvent(self, event):
      #print "in enter ",event.mimeData()
      #if event.mimeData().hasFormat("text/uri-list"):
      if event.mimeData().hasFormat("text/uri-list"):
         event.accept()      
     
class Ui_MainWindow(object):
   
   def setupUi(self, MainWindow, client):
      
      MainWindow.setObjectName("MainWindow")
      MainWindow.resize(600, 400)
      self.client = client
      self.setUpHintService()
      self.centralwidget = QWidget(MainWindow)
      self.centralwidget.setObjectName("centralwidget")
      
      self.horizontalLayout = QVBoxLayout(self.centralwidget)
      self.horizontalLayout.setObjectName("horizontalLayout")
      
      self.treeView = LMTreeView(self.centralwidget)
      self.treeModel = BrowserTreeModel()
      self.treeView.setModel(self.treeModel)
      self.treeView.setObjectName("treeView")
      
      
      
      self.horizontalLayout.addWidget(self.hint.combo)
      self.horizontalLayout.addWidget(LmEdit())
      self.horizontalLayout.addWidget(self.treeView)
      
      MainWindow.setCentralWidget(self.centralwidget)
      
      
      
      self.retranslateUi(MainWindow)
      QMetaObject.connectSlotsByName(MainWindow)
   
   
   def callBack(self, items):
      """
      @summary: call back from hint class
      @param items: list of hit items
      """
      if items[0].displayName == '':
         
         #print "count ",self.treeModel.provider.childCount()
         self.treeModel.beginRemoveRows(self.treeModel.index(0,0,QModelIndex()), 0, self.treeModel.provider.childCount()-1)
         self.treeModel.provider.childItems = []
         self.treeModel.endRemoveRows()
   
      else:
         row = 0
         self.treeModel.provider.childItems = []
         for sps in items:
            #print "making an item"
            nameFolder = TreeItem(sps.displayName,sps.displayName,self.treeModel.provider)
            occSet     = TreeItem(sps.occurrenceSetId,"occurrence set",nameFolder)
            maxentFolder = TreeItem('MaxEnt','MaxEnt',nameFolder)
            rs = str(random.randint(1000, 123545))
            rs2 = str(random.randint(1000, 123545))
            someProj =  TreeItem(rs,rs,maxentFolder)
            someProj2 = TreeItem(rs2,rs2,maxentFolder)
            self.treeModel.insertRow(row, QModelIndex())
            row = row + 1
            #self.treeModel.emitDataChanged()
                     
         self.treeView.expand(self.treeModel.index(0,0,QModelIndex()))
        
      
   def setUpHintService(self):
      
      #self.callBack = None
      self.hint = Hint(self.client, callBack=self.callBack)
      
   
   def retranslateUi(self, MainWindow):
      MainWindow.setWindowTitle(QApplication.translate("MainWindow", 
                                                       "MainWindow", None, QApplication.UnicodeUTF8))


if __name__ == "__main__":
   
   # -----  client
   import_path = "/home/jcavner/ghWorkspace/LmQGIS.git/lifemapperTools/"
   sys.path.append(os.path.join(import_path, 'LmShared'))
   configPath = os.path.join(import_path, 'config', 'config.ini') 
   os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath
   from LmClient.lmClientLib import LMClient
   # -------
   
   client =  LMClient()
   client.login(userId='Dermot', pwd='Dermot')
   
   
   app = QApplication(sys.argv)
   MainWindow = QMainWindow()
   ui = Ui_MainWindow()
   ui.setupUi(MainWindow, client)
   MainWindow.show()
   sys.exit(app.exec_())