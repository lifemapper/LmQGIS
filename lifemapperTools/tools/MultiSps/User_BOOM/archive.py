import cPickle
import os
from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import * 
from lifemapperTools.common.lmHint import Hint, SpeciesSearchResult
from lifemapperTools.common.lmListModel import LmListModel
from lifemapperTools.icons import icons
from lifemapperTools.common.pluginconstants import QGISProject
from __builtin__ import True


class ArchiveComboModel(LmListModel):
   """
   @summary: data model for (sps,...) user entry search combo
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

class PAMListingItem(object):
   """
   @note: rough class for PAM (Exp) items for listing, will need to change
   data method in PAMIconListModel and setData in same
   """
   def __init__(self,  icon, name, typeExps=None, treeId=None):
      """
      @summary: Constructor for SpeciesSearchResult object
      
      """
      self.name = name
      self.typeExps = typeExps
      self.treeId = treeId
      self.icon = icon
      
      
      # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the TreeSearchResult 
                   object
      """
      return "%s" % (self.name)


class PAMIconListModel(LmListModel):
   
   def __init__(self,data,startBut,customIdx=[]):
      
      LmListModel.__init__(self, data)
      self.startBut = startBut
      self.customData = customIdx
   
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
      elif role == Qt.DisplayRole:
         return self.listData[index.row()].name
      elif role == Qt.DecorationRole:
         return self.listData[index.row()].icon
      elif index.row() in self.customData:
         return self.listData[index.row()].customData()
      return None #QVariant()
   
   def flags(self, index):   
      if  index.isValid(): #index.column() in self.editIndexes and index.column() not in self.controlIndexes:     
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable# | Qt.ItemIsEditable | Qt.ItemIsDropEnabled
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
         self.startBut.setAutoDefault(True)
         print type(value)
         self.listData[index.row()].name = value.toString()
      except Exception, e:
         print "FAIL ",str(e)
         self.listData[index.row()].name = str(value)
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
      """
      @summary: subclass for list widget for species search results
      """
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
      #self.projectCanvas.setMinimumSize(698, 470)
      self.projectCanvas.doubleClicked.connect(parent.drillDown)
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
      """
      @note: considering doing things like setting EPSG code for an experiment with these 
      controls, another idea would be on click of "Start" have modeal subpanel
      """
      try:
         index = self.projectCanvas.indexAt(pos)
         value = 666# index.model().listData[index.row()][index.column()]
         menu = QMenu()
         setAllAction = menu.addAction('MCPA_maybe "'+str(value)+'"')
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
      
      self.newPAMButton = QPushButton("New PAM")
      if newButController is not None:
         self.newPAMButton.clicked.connect(newButController)
      self.newPAMButton.setAutoDefault(False)
      self.newPAMButton.setMinimumWidth(158)   # MIGHT WANT TO RETURN HORIZ LAYOUT
      
      self.startBut = QPushButton("Start")
      self.startBut.setEnabled(False)
      self.startBut.clicked.connect(self.startNewExp)
      #self.startBut.setAutoDefault(False)
      self.AddButton = QPushButton("Add To")
      self.AddButton.setEnabled(False)
      self.AddButton.setAutoDefault(False)
      
      
      return self.newPAMButton,self.startBut,self.AddButton
   
class UserArchiveController(Search,PAMList):
   
   def __init__(self, parent=None):
      """
      @note: question as to when self.checkExperiments() gets called, old method use to call
      on instantiation of new Exp dialog
      """
      
      PAMList.__init__(self)
      self.PAMProjectView(parent)
      self.getExpList()
      self.parent = parent
      print "in initial UserArchiveController ",self.startBut
      
   def flipToMCPA(self,index):
      """
      @note: if from folder stacked Widget will have to account for no tabs, will 
      need to send new exp Id to inputs panel
      """
      print index.row()
      try:  # tabs
         tabs = self.parent.tabWidget
         mcpaWidget = self.parent.mcpaPage
         tabs.setCurrentWidget(mcpaWidget)
      except: #stackedWidgets
         try: # folder stacked Widgets
            pass
         except: #vanilla stacked Widgets
            pass
      
      
   def _checkQgisProjForKey(self):
      """
      @ gets the project file name for the current QGIS project
      and if found in QSettings sets currentExpId to exp Id
      """
      project = QgsProject.instance()
      filename = str(project.fileName())  
      found = False
      s = QSettings()
      for key in s.allKeys():
         if 'RADExpProj' in key:
            value = str(s.value(key))
            if value == filename:
               found = True
               expId = key.split('_')[1]
               s.setValue("currentExpID", int(expId))  
      return found   

        
# ..............................................................................
      
   def checkExperiments(self):
      """
      @summary: gets the current expId, if there is one it gets the current
      project path associated with that id.  If there is a project path, it 
      triggers a save project.  If there is no path, it asks a save as, and sets 
      the project path for the id. The last thing it does is to open a new 
      qgis project
      """   
      s = QSettings()
      currentExpId  = s.value("currentExpID",QGISProject.NOEXPID,type=int)
      if currentExpId != QGISProject.NOEXPID:
         currentpath = str(s.value("RADExpProj_"+str(currentExpId),
                                   QGISProject.NOPROJECT))
         if currentpath != QGISProject.NOPROJECT and currentpath != '':
            self.interface.actionSaveProject().trigger()
         else:
            if len(QgsMapLayerRegistry.instance().mapLayers().items()) > 0:
               #self.interface.actionSaveProjectAs().trigger()
               self.workspace.saveQgsProjectAs(currentExpId)
               
         # now  actionNewProject
         self.interface.actionNewProject().trigger()
         s.setValue("currentExpID",QGISProject.NOEXPID)
      else: # no experiment Id
         # there is a case where a Qgis project can be opened but there is no
         # current id, like after a sign out but that Qgis project belongs to an id, in that case it needs
         # to start a new project
         if len(QgsMapLayerRegistry.instance().mapLayers().items()) == 0 or self._checkQgisProjForKey():      
            self.interface.actionNewProject().trigger()
   
   def startNewExp(self):
      """
      @summary: called on click of start button,
      @note: need to (maybe) incoroporate QSettings routing similar to new exp in old RAD 
      """
      print "at new experiment"
      #self.checkExperiments()  # this will have to be checked in QGIS
      try:
         pass
      except:
         pass
      
   def getExpList(self):
      """
      @summary: gets listing of user experiments,  will need to use 
      client library, for now just mockup
      """
      self.data = []
      try:
         for i,x in enumerate(range(0,25)):
            icon = QIcon(":/plugins/lifemapperTools/icons/Grid_Owl.png")
            # append PAMListingItem instead, (icon, name, typeExps=None, treeId=None)
            #self.data.append([icon,"PAM %s" % (int(i))])
            self.data.append(PAMListingItem(icon,"Experiment %s" % (int(i))))
      except:
         pass
      else:
         self.archiveModel = PAMIconListModel(self.data,self.startBut)
         self.projectCanvas.setModel(self.archiveModel)
         
   def enteredName(self,something):
      
      print something
         
   def createNewPAM_ICON(self):
      """
      @summary: just creates a PAM Icon, will need add metadata to 
      the data model behind the icon when this happens
      """
      
      self.projectCanvas.setEditTriggers(QAbstractItemView.CurrentChanged)
      icon = QIcon(":/plugins/lifemapperTools/icons/Grid_Owl.png")
      # insert PAMListingItem instead, (icon, name, typeExps=None, treeId=None)
      #self.data.insert(0, [icon,"New PAM"])
      self.data.insert(0,PAMListingItem(icon,"New PAM"))
      self.archiveModel.updateList(self.data)
      
      self.projectCanvas.setEditTriggers(QAbstractItemView.CurrentChanged)
      newIdx = self.archiveModel.index(0)
      #selModel = self.projectCanvas.selectionModel()
      #selModel.select(newIdx,QItemSelectionModel.Select)
      self.projectCanvas.setCurrentIndex(newIdx)
      self.projectCanvas.setEditTriggers(QAbstractItemView.DoubleClicked)
      #QAbstractItemView.currentIndex().connect.entered(self.enteredName)  #???? should be a way here 
      # even with a list model
      
      
      
      
      
      
      
      
      
      
      