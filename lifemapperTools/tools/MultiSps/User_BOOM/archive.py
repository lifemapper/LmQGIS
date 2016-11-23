import cPickle
import os
from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import * 
from lifemapperTools.common.lmHint import Hint, SpeciesSearchResult
from lifemapperTools.common.lmListModel import LmListModel
from lifemapperTools.icons import icons
from __builtin__ import True


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
               return self.listData[index.row()].taxaName
               #return self.listData[index.row()]
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

class PAMIconListModel(LmListModel):
   
   def __init__(self,data,startBut):
      
      LmListModel.__init__(self, data)
      self.startBut = startBut
      
   
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if not index.isValid() or not (0 <= index.row() < len(self.listData)):
         return None #QVariant()
      if role == Qt.DisplayRole:
         return self.listData[index.row()][1]
      if role == Qt.DecorationRole:
         return self.listData[index.row()][0]
      return None #QVariant()
   
   def flags(self, index):   
      if  index.isValid(): #index.column() in self.editIndexes and index.column() not in self.controlIndexes:     
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDropEnabled
      #elif index.column() in self.controlIndexes:
      #   return Qt.ItemIsEnabled | Qt.ItemIsSelectable   
        
      return QAbstractTableModel.flags(self, index)
   
   def setData(self, index, value, role=Qt.EditRole):
      """
      @summary: sets an individual item (cell) in the table data
      """
      try:
         # can send to server, or store name, andor enable start
         print "getting in here on drop, check to see if from drag"
         self.startBut.setEnabled(True)  # put this in function will need to do several things
         print type(value)
         self.listData[index.row()][1] = value.toString()
      except Exception, e:
         print "FAIL ",str(e)
         self.listData[index.row()][1] = str(value)
      self.dataChanged.emit(index,index)
      return True
   
   def updateList(self, newList):
      """
      @summary: Updates the contents of the list
      @param newList: A list of items to use for the new list
      @note: The provided list will replace the old list 
      """
      self.beginRemoveRows(QModelIndex(),0,len(self.listData)) # optional
      self.listData = [] # optional
      self.endRemoveRows() # optional
      self.beginInsertRows(QModelIndex(), 0, len(newList)) #just len makes auto with setIndex work better
      self.listData = newList
      
      self.endInsertRows()

class SpsSearchResult(object):
   
   """
   @summary: Data structure for species search results (Solr prj objects)
   """
   # .........................................
   def __init__(self, taxaName, species ):
      """
      @summary: Constructor for SpeciesSearchResult object
      @param displayName: The display name for the occurrence set
      @param occurrenceSetId: The Lifemapper occurrence set id
      @param numPoints: The number of points in the occurrence set
      """
      self.taxaName = taxaName
      self.species = species

   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      #return "%s (%s points)" % (self.displayName, self.numPoints)
      return "%s " % (self.taxaName)


class ArchiveHint(Hint):
   
   def __init__(self, client, callBack=None, setModel=True, data=[]):
      Hint.__init__(self, client, callBack=callBack, setModel=setModel)
      self.layers = data
      #self.combo = QComboBox()
      #self.combo.setEditable(True)
      
   def onTextChange(self, text):
      
      noChars = len(text)
      if text == '':  # never getting in here, callback vs. callBack
         self.combo.clear()
         self.combo.clearEditText()
         if self.callback is not None:
            self.callback('')
                  
      if noChars >= 3:
         #if text.count(" ") == 1:  
         #   return
         #if ' ' in text:
         #   text.replace(' ','%20')
         self.searchArchive(text)
         
   def searchArchive(self,searchText=''):
      """
      @summary: calls hint service
      @param    searchText: text to search for
      @todo:    needs a call back, probably set on init
      """
      #print "is this here?"
      # use toUnicode(searchText).encode('utf-8') for search
      try:                                         
         matches = [v for v in self.layers if v.taxaName.startswith(searchText)]    
      except Exception, e:
         print "except in searchArchive ",str(e)
      else:
         if len(matches) > 0:
            self.model.updateList(matches)  #this updates combo
            if self.callback is not None:
               self.callback(self.combo.currentText())  #this only updates listView



class Search(object):
   
   #def __init__(self):
      
   #   self.PAMProjectView()
      
   def hintBox(self, data=[], parent=None):
      
      """
      @summary: sets up the hint service and sets hint attribute
      combo can be added as a widget using self.hint.combo, callback
      adds extra functionality in addition to combo model
      """
      self.parent = parent
      self.folderHint = ArchiveHint(None, callBack=self.callBack, setModel=False,data=data) #, serviceRoot=CURRENT_WEBSERVICES_ROOT
      archiveComboModel = ArchiveComboModel([],None)
      self.folderHint.model = archiveComboModel
      self.folderHint.combo.lineEdit().setPlaceholderText("[Start Typing]")
      self.folderHint.combo.setModel(archiveComboModel)
      self.folderHint.combo.setStyleSheet("""QComboBox::drop-down {width: 0px; border: none;} 
                                   QComboBox::down-arrow {image: url(noimg);}""")
      self.archiveListView()
      self.folderHint.layers = self.getTaxa()
      
      return self.folderHint,self.listView
   
   def callBack(self, currentItem):
      
      self.listView.clear()
      
      if str(currentItem) in self.taxa:
         for res in self.taxa[str(currentItem)]:
            QListWidgetItem(res, self.listView, QListWidgetItem.UserType)
   
  
      
   def archiveListView(self):
      
      self.listView = LmListWidget(self.parent)
      self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
      self.listView.setDragEnabled(True)
      self.listView.setDragDropMode(QAbstractItemView.DragOnly)
   
   def getTaxa(self):
      
      taxa = cPickle.load(open(os.path.join("/home/jcavner","taxaLookup.pkl")))
      self.taxa = taxa
      spsByTaxa = [SpsSearchResult(k,taxa[k]) for k in taxa.keys()]
      return spsByTaxa

class LmListWidget(QListWidget):
   
   def __init__(self,parent):
      QListWidget.__init__(self, parent)
   
   def mimeTypes_bad(self, *args, **kwargs):
      #return QListWidget.mimeTypes(self, *args, **kwargs)
      print "mime types"
      nl = QStringList()
      nl.append("text/uri-list")
      return nl
   def mimeData(self, *args, **kwargs):
      
      print "args ",type(args[0][0]) # wow
      print "kargs ",kwargs
      return QListWidget.mimeData(self, *args, **kwargs)
   
   def mimeData_bad(self, *args, **kwargs):
      
      print "mime"
      mimeData = QMimeData()
      mimeData.setData("text/uri-list","/home/jcavner/pamsum832.prj")
      return mimeData
      
   def startDrag(self, *args, **kwargs):
      print "start drag"
      #print "args ",dir(args[0])
      #print "kargs ",kwargs
      #drag = QDrag(self)  
      #mimeData = QMimeData()
      #mimeData.setData("text/uri-list","/home/jcavner/pamsum832.prj")
      ###mimeData.setData("text/uri-list",fullPath)
      ##
      #drag.setMimeData(mimeData)   
      ###pixmap = QPixmap()
      ###pixmap = pixmap.grabWidget(self, self.visualRect(itemIdx))
      ###drag.setPixmap(pixmap)
      ##result = drag.start(Qt.MoveAction)
      #drag.start(Qt.MoveAction)
      return QListWidget.startDrag(self, *args, **kwargs)

class PAMListView(QListView):
   
   def __init__(self,parent=None):
      QListView.__init__(self, parent)
   
   def dragMoveEvent(self, *args, **kwargs):
      
      #print "over view"
      #
      
      return QListView.dragMoveEvent(self, *args, **kwargs)


class PAMList():
   
   def __init__(self):
      
      self.ExpButtons()
   
   def PAMProjectView(self,parent=None):
      
      #self.projectCanvas = QListView()
      self.projectCanvas = PAMListView(parent=parent)
      self.projectCanvas.setViewMode(QListView.IconMode)
      self.projectCanvas.setMovement(QListView.Snap)  # QListView.Static doesn't allow drop?
      self.projectCanvas.setGridSize(QSize(100,100))
      self.projectCanvas.setIconSize(QSize(80,80))
      self.projectCanvas.setWrapping(True)
      
      self.projectCanvas.setContextMenuPolicy(Qt.CustomContextMenu)
      self.projectCanvas.customContextMenuRequested.connect(self.setAllPopUp)
      
      #self.projectCanvas.setDragEnabled(True)
      #self.projectCanvas.setDragDropMode(QAbstractItemView.DropOnly)
      self.projectCanvas.setAcceptDrops(True)
      #self.projectCanvas.setDragDropOverwriteMode(True) # replaces text, without Static?
      
   def setAllPopUp(self,pos):
      try:
         index = self.projectCanvas.indexAt(pos)
         value = index.model().listData[index.row()][index.column()]
         menu = QMenu()
         setAllAction = menu.addAction('MCPA "'+str(value)+'"')
         setSelected = menu.addAction('Set Selected in this column to "'+str(value)+'"')
         setEmpty = menu.addAction('Set empty cells in this column to "'+str(value)+'"')
         action = menu.exec_(QCursor.pos())
         if action == setAllAction:
            self.flipToMCPA(index)
         elif action == setSelected:
            self.setColumnsInSelectedRows(index)
         elif action == setEmpty:
            self.setEmptyInColumn(index)
      except Exception, e:
         print str(e) 
      
   def ExpButtons(self,newButController=None):
      
      newPAMButton = QPushButton("New PAM")
      if newButController is not None:
         newPAMButton.clicked.connect(newButController)
      newPAMButton.setAutoDefault(False)
      newPAMButton.setMinimumWidth(158)   # MIGHT WANT TO RETURN HORIZ LAYOUT
      
      self.startBut = QPushButton("Start")
      self.startBut.setEnabled(False)
      self.startBut.setAutoDefault(False)
      self.AddButton = QPushButton("Add To")
      self.AddButton.setEnabled(False)
      self.AddButton.setAutoDefault(False)
      
      
      return newPAMButton,self.startBut,self.AddButton
   
class UserArchiveController(Search,PAMList):
   
   def __init__(self, parent=None):
      
      PAMList.__init__(self)
      self.PAMProjectView(parent)
      self.getData()
      self.parent = parent
      
      
   def flipToMCPA(self,index):
      print index.row()
      tabs = self.parent.tabWidget
      mcpaWidget = self.parent.mcpaPage
      tabs.setCurrentWidget(mcpaWidget)
      
      
   def getData(self):
      self.data = []
      try:
         for i,x in enumerate(range(0,25)):
            icon = QIcon(":/plugins/lifemapperTools/icons/Grid_Owl.png")
            self.data.append([icon,"PAM %s" % (int(i))])
      except:
         pass
      else:
         self.archiveModel = PAMIconListModel(self.data,self.startBut)
         self.projectCanvas.setModel(self.archiveModel)
         
   def enteredName(self,something):
      
      print something
         
   def createNewPAM(self):
      
      self.projectCanvas.setEditTriggers(QAbstractItemView.CurrentChanged)
      icon = QIcon(":/plugins/lifemapperTools/icons/Grid_Owl.png")
      self.data.insert(0, [icon,"New PAM"])
      self.archiveModel.updateList(self.data)
      
      self.projectCanvas.setEditTriggers(QAbstractItemView.CurrentChanged)
      newIdx = self.archiveModel.index(0)
      #selModel = self.projectCanvas.selectionModel()
      #selModel.select(newIdx,QItemSelectionModel.Select)
      self.projectCanvas.setCurrentIndex(newIdx)
      self.projectCanvas.setEditTriggers(QAbstractItemView.DoubleClicked)
      #QAbstractItemView.currentIndex().connect.entered(self.enteredName)  #???? should be a way here 
      # even with a list model
      
      
      
      
      
      
      
      
      
      
      