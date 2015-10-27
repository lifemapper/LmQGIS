import sys, os
import random
import platform
import tempfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.lmHint import Hint
import lifemapperTools as LM
from LmClient.lmClientLib import LMClient, OutOfDateException
from lifemapperTools.common.lmListModel import LmListModel
from lifemapperTools.common.pluginconstants import ARCHIVE_DWL_TYPE
from LmCommon.common.localconstants import  WEBSERVICES_ROOT

# ..........................

PROVIDER = "Lifemapper"
# ..........................

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

class BrowserTreeModel(QAbstractItemModel):

   def __init__(self):
      QAbstractItemModel.__init__(self)
      self.headers = ['','','']
      self.columns = 3
      self.root = TreeItem("Root", "Root", parent = None)
      self.provider = TreeItem("Lifemapper","Lifemapper",self.root)
      
   
   # ----------  change data
   def emitDataChanged(self):
      # deprecated
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
   def updateList(self,newList): #deprecated
      
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
         #return Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable
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
         print "Returning 0 in rowCount in Tree model"
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
            # might just want to return an empty sting here
            return 
      


class TreeItem(object):
   
   # --- class for tree items
   
   def __init__(self, data, name, parent=None, hit=None, type=None):
      
      self.name = name
      self.parentItem = parent
      self.itemData = data  # this usually means an id
      self.type = type
      self.childItems = []
      self.setParent(parent)
      self.hit = hit
   # ..........................................   
   def setParent(self, parent):
      if parent != None:
         self.parent = parent
         self.parent.appendChild(self)
      else:
         self.parent = None
   # ..........................................   
   def appendChild(self, item):
      self.childItems.append(item)
   
   # ---------- from, http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/itemviews/simpletreemodel/simpletreemodel.py
   def child(self, row):
      # get called from index() in model
      try:
         return self.childItems[row]
      except Exception, e:
         #print "exception in child in TreeItem ",str(e)
         pass
   # ..........................................
   def childCount(self):
      return len(self.childItems)
   
   def data(self, column):
      # not using this, doesn't need it for single data
      # attached to instance of item
      try:
         return self.itemData[column]  # not a list, but could be
      #except IndexError:
      except Exception, e:
         print "returning None from data in TreeItem ",str(e)
         return None
   
   def getParent(self):  # changed this because "parent" was both a method and attribute
      return self.parentItem
   
   def row(self):
      if self.parentItem:
         return self.parentItem.childItems.index(self)   
      print "returning zero from row in TreeItem"
      return 0
   # ---------------- end 
   
   def childAtRow(self, row):
      # !!!!!!! same as child
      return self.childItems[row]
   
   def rowOfChild(self, child):       
      for i, item in enumerate(self.childItems):
         if item == child:
               return i
      print "returning -1 from rowOfChild (Tree Item)"
      return -1
   
   def removeChild(self, row):
      try:
         value = self.childItems[row]
         self.childItems.remove(value)
      except Exception, e:
         print "in removeChild (Tree Item) except ",str(e)
         pass
   
   def __len__(self):
      return len(self.childItems)
   
class LMTreeView(QTreeView):
   
   def __init__(self, parent, client ,tmpDir):
      
      QTreeView.__init__(self,parent)
      self.client = client
      self.provider = PROVIDER
      self.tmpDir = tmpDir
      self.header().hide()
      self.doubleClicked.connect(self.handleEvent)
      #self.dragEnabled()
      #self.setDragDropMode(QAbstractItemView.DragOnly)
      self.header().setResizeMode(QHeaderView.ResizeToContents)
   # .................................................................      
   def handleEvent(self, index):
      
      # will need to get type
      childRowIdx = index.row()
      downloadType = self.model().nodeFromIndex(index.parent()).child(childRowIdx).type
      hit,lmId,parentName,leafName,grandparent = self.getDataFromDoubleClick(index)
      if downloadType == ARCHIVE_DWL_TYPE.OCCURRENCE: 
         #if hit and lmId:
         self.downloadShpFile(lmId, hit=hit, parentName=parentName)
      if downloadType == ARCHIVE_DWL_TYPE.PROJ:
         #if hit and lmId:
         self.downLoadProjectionTiff(lmId, parentName, grandparent, scenName=leafName)
      
   # ..............................................................  
   def getDataFromDoubleClick(self, itemIdx):
      """
      @summary: gets data from tree model from selection in view
      """
      
      childRowIdx = itemIdx.row()
      lmId = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      leafName = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).name
      hit = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).hit
      parentName = self.model().nodeFromIndex(itemIdx.parent()).name
      try:
         grandparent = self.model().nodeFromIndex(itemIdx.parent().parent()).name
      except Exception, e:
         grandparent = ''
      #if hit is None:
      #   hit = True  # this is temporary, to handle hit when still using them
      return hit, lmId, parentName, leafName, grandparent

   #............................................................
   def makeColorList(self):
      i = []
   
      i.append(QgsColorRampShader.ColorRampItem(0, QColor("#2b83ba"), "0"))
      i.append(QgsColorRampShader.ColorRampItem(25, QColor("#abdda4"), "25"))
      i.append(QgsColorRampShader.ColorRampItem(50, QColor("#ffffbf"), "50"))
      i.append(QgsColorRampShader.ColorRampItem(75, QColor("#fdae61"), "75"))
      i.append(QgsColorRampShader.ColorRampItem(100, QColor("#d7191c"), "100"))
      
      return i
   #............................................................
   def makeRenderer(self ,rasterLayer):
      
      try:
         fcn = QgsColorRampShader()
         fcn.setColorRampType(QgsColorRampShader.INTERPOLATED)
         lst = self.makeColorList()
         fcn.setColorRampItemList(lst)
         shader = QgsRasterShader()
         shader.setRasterShaderFunction(fcn)
      except Exception, e:
         print "exception in shader ",str(e)
         shader = None
       
      if shader is not None:
         try:
            renderer = QgsSingleBandPseudoColorRenderer(rasterLayer.dataProvider(), 1, shader)
            rasterLayer.setRenderer(renderer)
         except:
            pass
      

   # ..............................................................
   def addTiffToCanvas(self, path, tocName):
      
          
      rasterLayer = QgsRasterLayer(path,tocName)  
      self.makeRenderer(rasterLayer)

      if not rasterLayer.isValid():
         QMessageBox.warning(self,"status: ",
           "not a valid layer")           
      else:
         
         QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)  
     
   # .............................................................. 
   def addShpToCanvas(self, vectorpath, shapename):
     
      vectorLayer = QgsVectorLayer(vectorpath,shapename,'ogr')
      warningname = shapename    
      if not vectorLayer.isValid():
         QMessageBox.warning(self,"status: ",
           "%s not valid" % (warningname))           
      else:
         
         QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
         
   # ........................................       

   def downloadShpFile(self, occId, hit = None, parentName='occurrence set'):
      
      #if self.serviceRoot:         
      try:
         #if hit is not None:
         #   tocName = '%s_%s' % (self.provider, hit.displayName)
         #else:
         tocName = '%s' % (parentName)
         if self.tmpDir is not None:
            tmpDir = os.path.join(self.tmpDir,"%s.shp" % (tocName))
            try:
               if hit is not None:
                  self.client.sdm.getShapefileFromOccurrencesHint(hit,tmpDir,instanceName = self.provider, overwrite=True)
               else:
                  self.client.sdm.getOccurrenceSetShapefile(occId, filename=tmpDir, overwrite=True)
            except Exception, e:
               print str(e)
            else:
               try:
                  self.addShpToCanvas(tmpDir, tocName)
               except Exception, e:
                  message = "couldn't add shp file to canvas "+str(e)
                  QMessageBox.warning(self,"status: ", message)
                                  
         else:
            message = "No tmp directory set in Environment variable, try setting TMPDIR"
            QMessageBox.warning(self,"status: ",message) 
      except Exception, e:
            message = str(e)
            QMessageBox.warning(self,"status: ",message) 

   # ..............................................................

   def downLoadProjectionTiff(self ,lmId, algoName, displayName, scenName=''):
      """
      @summary: called from viewDownloadProjection, gets projection id from the 
      table model, opens a file dialog to get a filename and calls getProjecctionTiff
      in the sdm client library
      """
   
      try:
         tocName = '%s_%s_%s' % (displayName, algoName, scenName)
         if self.tmpDir is not None:
            tmpDir = os.path.join(self.tmpDir,"%s.tif" % (tocName))
            try:
               self.client.sdm.getProjectionTiff(lmId,filename=tmpDir)
            except Exception,e:
               QMessageBox.warning(self,"Error: ",
              "Problem with the Tiff service "+str(e)) 
            else:
               try:
                  self.addTiffToCanvas(tmpDir, tocName)
               except Exception, e:
                  message = "couldn't add shp file to canvas "+str(e)
                  QMessageBox.warning(self,"status: ", message)
         else:
            message = "No tmp directory set in Environment variable, try setting TMPDIR"
            QMessageBox.warning(self,"status: ",message) 
    
      except Exception, e:
         message = str(e)
         QMessageBox.warning(self,"status: ",message)
   # ..............................................................      
   def startDrag(self, *args, **kwargs):
      """
      @summary: drag event calls this but only for leaves in tree
      """
      
      # ..............
      # row - itemIdx.row()
      # row of parent - itemIdx.parent().row()
      # parent node - self.model().nodeFromIndex(itemIdx.parent())
      # selected data - self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData
      if self.tmpDir is not None:
         
         # --- get info from tree model
         itemIdx = self.selectionModel().selectedIndexes()[0]
         childRowIdx = itemIdx.row()
         lmId = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
         displayName = self.model().nodeFromIndex(itemIdx.parent()).name
         hit = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).hit
         downloadType = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).type
         parentName = self.model().nodeFromIndex(itemIdx.parent()).name
         scenName = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).name
         try:
            grandparent = self.model().nodeFromIndex(itemIdx.parent().parent()).name
         except Exception, e:
            grandparent = ''
         # ------- 
         
         if downloadType == ARCHIVE_DWL_TYPE.OCCURRENCE:
            fn = "%s.shp" % (toUnicode(displayName).encode('utf-8')) # provider is hardcoded here
         if downloadType == ARCHIVE_DWL_TYPE.PROJ:
            #fn = "Lifemapper_%s.tif" % (toUnicode(displayName).encode('utf-8'))
            fn = '%s_%s_%s' % (toUnicode(grandparent).encode('utf-8'),parentName,scenName)
         fullPath = os.path.join(self.tmpDir,fn)
         
         
         dlThread = QThread()
         dlw = DownLoadWorker(lmId=lmId,hit=hit,path=fullPath,client=self.client,
                              downloadType = downloadType,provider=self.provider)
         dlw.moveToThread(dlThread)
         dlw.finished.connect(dlThread.quit)
         dlThread.started.connect(dlw.downloadProcess)
         dlThread.start()
         dlw.deleteLater()
         
          
         drag = QDrag(self)  
         mimeData = QMimeData()
         #mimeData.setData("text/uri-list","/home/jcavner/USAdminBoundaries/Lower_48_Bison_Dissolved.shp")
         mimeData.setData("text/uri-list",fullPath)
         
         drag.setMimeData(mimeData)   
         pixmap = QPixmap()
         pixmap = pixmap.grabWidget(self, self.visualRect(itemIdx))
         drag.setPixmap(pixmap)
         result = drag.start(Qt.MoveAction)
      else:
         message = "No tmp directory set in Environment variable, try setting TMPDIR"
         QMessageBox.warning(self,"status: ",message)
      
class DownLoadWorker(QObject):
   
   finished = pyqtSignal()
   
   def __init__(self,lmId=None, hit=None, path=None, client=None,downloadType=None, provider="Lifemapper"):
      QObject.__init__(self)
      self.lmId = lmId
      self.hit = hit
      self.downloadType = downloadType
      self.tmpDir = path
      self.provider = provider
      self.client = client
   
   @pyqtSlot()
   def downloadProcess(self):
      
      if self.downloadType == ARCHIVE_DWL_TYPE.OCCURRENCE:
         try:
            if self.hit is not None:
               self.client.sdm.getShapefileFromOccurrencesHint(self.hit,self.tmpDir,instanceName = self.provider, 
                                                              overwrite=True)
            else:
               self.client.sdm.getOccurrenceSetShapefile(self.lmId, filename=self.tmpDir, overwrite=True)
         except Exception, e:
            pass
      if self.downloadType == ARCHIVE_DWL_TYPE.PROJ:
         try:
            self.client.sdm.getProjectionTiff(self.lmId,filename=self.tmpDir)
         except Exception, e:
            pass
      
      self.finished.emit()
      
class ArchiveComboModel(LmListModel):
   
   
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
         if index.row() == 0 and self.model:
            return "[start typing]"  # this is taken care of against combo with placeholder text
         else:   
            try: 
               return self.listData[index.row()].displayName
            except: 
               return #self.listData[index.row()]
           
      if index.isValid() and role == Qt.UserRole:
         return int(self.listData[index.row()])
      else:
         return 
      
   def updateList(self, newList):
      """
      @summary: Updates the contents of the list
      @param newList: A list of items to use for the new list
      @note: The provided list will replace the old list 
      """
      self.beginRemoveRows(QModelIndex(),0,len(self.listData)-1) # optional
      self.listData = [] # optional
      self.endRemoveRows() # optional
      
      self.beginInsertRows(QModelIndex(), 0, len(newList)-1) #just len makes auto with setIndex work better
      self.listData = newList
      self.endInsertRows()

class customWidget(QWidget):
   
   def __init__(self):
      QWidget.__init__(self)
      
   def sizeHint(self, *args, **kwargs):
      return QSize(550,800)

     
class Ui_Dock(object):
   
   def setupUi(self, dockWidget):
      
      
      self.setUpHintService()
      self.centralwidget = customWidget()
      self.centralwidget.setObjectName("centralwidget")
      
      self.verticalLayout = QVBoxLayout(self.centralwidget)
      self.verticalLayout.setObjectName("verticalLayout")
      
      self.treeView = LMTreeView(dockWidget,self.client,self.tmpDir)
      self.treeModel = BrowserTreeModel()
      self.treeView.setModel(self.treeModel)
      self.treeView.setObjectName("treeView")
      
      
      
      self.verticalLayout.addWidget(self.hint.combo)
      self.verticalLayout.addWidget(self.treeView)
      
      
      
      dockWidget.setWidget(self.centralwidget)
   # ..............................................................    
   def setUpHintService(self):
      """
      @summary: sets up the hint service and sets hint attribute
      combo can be added as a widget using self.hint.combo, callback
      adds extra functionality in addition to combo model
      """
      self.hint = Hint(self.client, callBack=self.callBack, setModel=False, serviceRoot=WEBSERVICES_ROOT)
      archiveComboModel = ArchiveComboModel([],None)
      self.hint.model = archiveComboModel
      self.hint.combo.lineEdit().setPlaceholderText("[Start Typing]")
      #self.hint.combo.setPlaceholderText("[Start Typing]") # for line Edit
      self.hint.combo.setModel(archiveComboModel)
      #self.comboEvent = ComboEventHandler() # don't use, doesn't work with Solr
      #self.hint.combo.installEventFilter(self.comboEvent)  # don't use, doesn't work with Solr
      self.hint.combo.setStyleSheet("""QComboBox::drop-down {width: 0px; border: none;} 
                                   QComboBox::down-arrow {image: url(noimg);}""")
      
   # .............................................................. 
   def callBack(self, items):
      """
      @summary: call back from hint class, where items are used to populate tree
      @param items: list of hit items
      """
      
      if items[0].displayName == '':
      #if len(items)  == 0:  # without SpeciesResult wrapper obj
         self.treeModel.beginRemoveRows(self.treeModel.index(0,0,QModelIndex()), 0, self.treeModel.provider.childCount()-1)
         self.treeModel.provider.childItems = []
         self.treeModel.endRemoveRows()
      else:
         row = 0
         self.treeModel.provider.childItems = []
         for sps in items:
            
            nameFolder = TreeItem(sps.displayName,sps.displayName,self.treeModel.provider)
            occSetName = "occurrence set (%s points)" % sps.numPoints
            occSet     = TreeItem(sps.occurrenceSetId,occSetName,nameFolder,
                                  type=ARCHIVE_DWL_TYPE.OCCURRENCE)
            try:
               for m in sps.models:
                  mF = TreeItem(m.algorithmCode,m.algorithmCode,nameFolder)
                  for p in m.projections:
                     TreeItem(p.projectionId,p.projectionScenarioCode,mF,type=ARCHIVE_DWL_TYPE.PROJ)
            except:
               pass
            self.treeModel.insertRow(row, QModelIndex())      
            row = row + 1
            
                     
         self.treeView.expand(self.treeModel.index(0,0,QModelIndex()))

   
class archiveBrowserDock(QDockWidget, Ui_Dock,):
   
   def __init__(self,iface, action=None):
      QDockWidget.__init__(self,None)
      
      self.setWindowTitle("Lifemapper Archive")
      self.iface = iface
      
      # ..................
      self.setTmpDir()
      self.action = action
      self.client = None
      self.action.triggered.connect(self.showHideBrowseDock)
      self.setupUi(self)


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
               self.treeView.client = self.client
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

   def setTmpDir(self):  
      
      if platform.mac_ver() == '': 
         tmp = None
         try:
            tmp = QDir.tempPath()  # this on windows might be weird
            if not os.path.exists(tmp):
               raise
         except:
            tmp = None
            try:
               #import tempfile
               tmp = tempfile.gettempdir()
               if not os.path.exists(tmp):
                  raise
            except:
               tmp = None
         self._tmpDir = tmp
      else:
         tmp = None
         if os.path.exists("/tmp"):
            self._tmpDir = "/tmp"
         else:
            home = os.path.expanduser("~")
            tmp = tempfile.mkdtemp(dir=home)  # need to check this in Mac
            if os.path.exists(tmp):
               self._tmpDir = tmp
            else:
               self._tmpDir = None
                           
   # .......................................           
   @property
   def tmpDir(self):
      return self._tmpDir
   # .......................................


                
class ComboEventHandler(QObject):
   
   def eventFilter(self, object, event):
      if event.type() == QEvent.KeyPress:         
         if event.key() == Qt.Key_Return:
            try:
               currentText = object.currentText()
               sL = currentText.split(" ")
               if len(sL) > 1:
                  currentText = " ".join(sL[:2])
                  object.hit.searchOccSets(searchText=currentText)    
            except Exception, e:
               print "EXCEPTION IN EVENT HANDLER ",str(e)   
      return QWidget.eventFilter(self, object, event)     

      
