import sys, os
import random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.lmHint import Hint, SpeciesSearchResult
import lifemapperTools as LM
from LmClient.lmClientLib import LMClient, OutOfDateException


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
         return self.headers[section]
      return 
   
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
      try:
         parent = node.parent
      except:
         return QModelIndex()
         
      if parent is None:
         return QModelIndex()
      
      
      grandparent = parent.parent  # attribute on item instance
      if grandparent is None:
         return QModelIndex()
      row = grandparent.rowOfChild(parent)
      
      if row != - 1:  #  
         return self.createIndex(row, 0, parent)
      else:
         return QModelIndex()
      
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
         return 
             
      if role == Qt.TextAlignmentRole:
         return int(Qt.AlignTop | Qt.AlignLeft)
      
      if role != Qt.DisplayRole:
         return 
      
              
      node = self.nodeFromIndex(index)
      #
      if index.column() == 0:
         try:
            return node.name
         except Exception, e:
            return 
      


class TreeItem(object):
   
   # --- class for tree items
   
   def __init__(self, data, name, parent=None, hit=None):
      
      self.name = name
      self.parentItem = parent
      self.itemData = data
      self.childItems = []
      self.setParent(parent)
      
      # ........
      # hit object
      if hit is not None:
         self.hit = hit
   
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
         pass
   
   def __len__(self):
      return len(self.childItems)
   
class LMTreeView(QTreeView):
   
   def __init__(self, parent):
      
      QTreeView.__init__(self,parent)
      self.header().hide()
      self.doubleClicked.connect(parent.handleEvent)
      self.dragEnabled()
      self.setDragDropMode(QAbstractItemView.DragOnly)
      self.header().setResizeMode(QHeaderView.ResizeToContents)
      
# ..............................................................      
   def startDrag(self, *args, **kwargs):
      """
      @summary: drag event calls this but only for leaves in tree
      """
      # can a I start a thread? and have it continue to drag?
      
      drag = QDrag(self)  
      mimeData = QMimeData()
      # ..............
      # row - itemIdx.row()
      # row of parent - itemIdx.parent().row()
      # parent node - self.model().nodeFromIndex(itemIdx.parent())
      # selected data - elf.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData
      sis = self.selectionModel().selectedIndexes()
      itemIdx = sis[0]
      childRowIdx = itemIdx.row()
      occSetId = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      
      # will use "text/uri-list" for dragging onto canvas
      #mimeData.setData("text/uri-list", "/home/jcavner/%s.shp" % (occSetId))
      mimeData.setData("text/uri-list","/home/jcavner/USAdminBoundaries/Lower_48_Bison_Dissolved.shp")
      drag.setMimeData(mimeData)   
      pixmap = QPixmap()
      pixmap = pixmap.grabWidget(self, self.visualRect(itemIdx))
      drag.setPixmap(pixmap)
      result = drag.start(Qt.MoveAction)
      

      
class LmEdit(QLineEdit):
   def __init__(self):
      QLineEdit.__init__(self)
      self.setAcceptDrops(True)
        
   def dropEvent(self, event):
      #print "dropped ",event.mimeData().text()
      self.setText(str(event.mimeData().urls()))  #urls() retiurns list, uri-list 
      #print "dropEvent called"
        
   def dragEnterEvent(self, event):
      #print "in enter ",event.mimeData()
      #if event.mimeData().hasFormat("text/uri-list"):
      if event.mimeData().hasFormat("text/uri-list"):
         event.accept()      
     
class Ui_Dock(object):
   
   def setupUi(self, dockWidget):
      
      self.setUpHintService()
      self.centralwidget = QWidget()
      self.centralwidget.setObjectName("centralwidget")
      
      self.verticalLayout = QVBoxLayout(self.centralwidget)
      self.verticalLayout.setObjectName("verticalLayout")
      
      self.treeView = LMTreeView(dockWidget)
      self.treeModel = BrowserTreeModel()
      self.treeView.setModel(self.treeModel)
      self.treeView.setObjectName("treeView")
      
      
      
      self.verticalLayout.addWidget(self.hint.combo)
      #self.verticalLayout.addWidget(LmEdit())
      self.verticalLayout.addWidget(self.treeView)
      
      #MainWindow.setCentralWidget(self.centralwidget)
      
      dockWidget.setWidget(self.centralwidget)
      QMetaObject.connectSlotsByName(dockWidget)
# ..............................................................    
   def setUpHintService(self):
      """
      @summary: sets up the hint service and sets hint attribute
      combo can be added as a widget using self.hint.combo, callback
      adds extra functionality in addition to combo model
      """
      self.hint = Hint(self.client, callBack=self.callBack)
# .............................................................. 
   def callBack(self, items):
      """
      @summary: call back from hint class, where items are used to populate tree
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
            occSet     = TreeItem(sps.occurrenceSetId,"occurrence set",nameFolder,hit=sps)
            maxentFolder = TreeItem('MaxEnt','MaxEnt',nameFolder)
            rs = str(random.randint(1000, 123545))
            rs2 = str(random.randint(1000, 123545))
            someProj =  TreeItem(rs,rs,maxentFolder)
            someProj2 = TreeItem(rs2,rs2,maxentFolder)
            self.treeModel.insertRow(row, QModelIndex())
            row = row + 1
            #self.treeModel.emitDataChanged()
                     
         self.treeView.expand(self.treeModel.index(0,0,QModelIndex()))

class LmCanvas(QgsMapCanvas):
   
   def __init__(self):
      QgsMapCanvas.__init__(self)
   
   def setAcceptDrops(self, *args, **kwargs):
      return QgsMapCanvas.setAcceptDrops(self, *args, **kwargs)
     
   def acceptDrops(self, *args, **kwargs):
      return QgsMapCanvas.acceptDrops(self, *args, **kwargs)
   
   #def setDropAction(self):
   
class archiveBrowserDock(QDockWidget, Ui_Dock,):
   
   def __init__(self,iface, action=None):
      QDockWidget.__init__(self,None)
      self.iface = iface
      # ...... hard coded (CHANGE)
      self.provider = "Lifemapper"
      self.serviceRoot = True
      # ..................
      self.setTmpDir()
      self.mapCanvas = self.iface.mapCanvas()
      #self.mapCanvas.dropEvent = self.archiveDrop
      self.action = action
      self.client = None
      self.action.triggered.connect(self.showHideBrowseDock)
      self.setUpHintService()
      self.setupUi(self)
# ..............................................................     
   def archiveDrop(self,*args,**kwargs):
      print "IS IT HERE ON DROP"
      print args
      print kwargs
# ..............................................................      
   def handleEvent(self, index):
      
      if index.row() == 0:
         hit,occSetId = self.getDataFromDoubleClick(index, occSet=True)
         if hit and occSetId:
            self.downloadShpFile(hit)
      
# ..............................................................  
   def getDataFromDoubleClick(self, itemIdx, occSet=False):
      """
      @summary: gets data from tree model from selection in view
      """
      hit = False
      occSetId = False
      childRowIdx = itemIdx.row()
      occSetId = self.treeModel.nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      if occSet:
         hit = self.treeModel.nodeFromIndex(itemIdx.parent()).child(childRowIdx).hit
      
         return hit, occSetId
 # ..............................................................  
   def getDataFromSeletion(self, occSet=False):
      """
      @summary: gets data from tree model from selection in view
      """
      sis = self.treeView.selectionModel().selectedIndexes()
      itemIdx = sis[0]
      childRowIdx = itemIdx.row()
      occSetId = self.treeModel.nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      if occSet:
         hit = self.treeModel.nodeFromIndex(itemIdx.parent()).child(childRowIdx).hit
      
   
# ..............................................................     
   def showHideBrowseDock(self):
      """
      @summary: slot for icon in metools
      """
      if self.isVisible():     
         self.hide()
      else:
         if self.client == None:
            self.signIn() 
            #self.loadInstanceCombo()
            if self.client is not None:
               self.hint.client = self.client
         self.show()
# ..............................................................         
   def signIn(self):
   
      try:
         cl = LMClient()
      except OutOfDateException, e:
         message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
         QMessageBox.warning(self,"Problem...",message,QMessageBox.Ok)
      except:
         message = "No Network Connection"
         QMessageBox.warning(self,"Problem...",message,QMessageBox.Ok)
      else:
         self.client = cl
         #print "COOKIE AT TOGGLE WIDGET ",self.client._cl.cookieJar," ",self.client
         try:
            myVersion = LM.version() # test"Version 0.1.2" #
            myVersion = myVersion.strip("Version")
            myVersion = myVersion.strip()
            self.client._cl.checkVersion(clientName="lmQGIS",verStr=myVersion)
         except OutOfDateException, e:
            
            message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
            self.client.logout()
            self.client = None
            msgBox = QMessageBox.warning(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
   # ........................................

   def addToCanvas(self, vectorpath, shapename):
     
      vectorLayer = QgsVectorLayer(vectorpath,shapename,'ogr')
      warningname = shapename    
      if not vectorLayer.isValid():
         QMessageBox.warning(self,"status: ",
           "%s not valid" % (warningname))           
      else:
         
         QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
         #self.iface.zoomFull()
   # ........................................       

   def downloadShpFile(self, hit):
      
      if self.serviceRoot:
         
         try:
            tocName = '%s_%s' % (self.provider, hit.displayName)
            if self.tmpDir is not None:
               tmpDir = os.path.join(self.tmpDir,"%s.shp" % (tocName))
               try:
                  self.client.sdm.getShapefileFromOccurrencesHint(hit,tmpDir,instanceName = self.provider, overwrite=True)
               except Exception, e:
                  print str(e)
               else:
                  try:
                     self.addToCanvas(tmpDir, tocName)
                  except Exception, e:
                     message = "couldn't add shp file to canvas "+str(e)
                     QMessageBox.warning(self,"status: ", message)
                                     
            else:
               message = "No tmp directory set in Environment variable, try setting TMPDIR"
               QMessageBox.warning(self,"status: ",message) 
         except Exception, e:
               message = str(e)
               QMessageBox.warning(self,"status: ",message)     
   # .......................................

   def setTmpDir(self):  
        
      tmp = None
      try:
         tmp = QDir.tempPath()  # this on windows might be weird
         if not os.path.exists(tmp):
            raise
      except:
         tmp = None
         try:
            import tempfile
            tmp = tempfile.gettempdir()
            if not os.path.exists(tmp):
               raise
         except:
            tmp = None
      self._tmpDir = tmp

   @property
   def tmpDir(self):
      return self._tmpDir
# .......................................
   @property
   def serviceRoot(self):
      
      if self._serviceRoot is None:
         pCurrentIdx = self.providerCombo.currentIndex()
         if pCurrentIdx != 0 and pCurrentIdx != -1:
            self._serviceRoot = self.providerCombo.itemData(pCurrentIdx, role=Qt.UserRole)
      
      return self._serviceRoot
   
   @serviceRoot.setter   
   def serviceRoot(self, value):      
      self._serviceRoot = value
                
      

      

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