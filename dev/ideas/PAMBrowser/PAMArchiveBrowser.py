
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
from radTable import *
from lmListModel import LmListModel
from lmHint import Hint, SpeciesSearchResult
from LmQTree import BrowserTreeModel, TreeItem
import icons.icons

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

class WebPage(QWebPage):
   """
   Makes it possible to use a Python logger to print javascript console messages
   """
   def __init__(self, logger=None, parent=None):
      super(WebPage, self).__init__(parent)
      if not logger:
         logger = logging
      self.logger = logger
        

   def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
      self.logger.warning("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))


class PAMTableModel(RADTableModel):
   
   def flags(self, index):   
      if index.column() in self.editIndexes and index.column() not in self.controlIndexes:     
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable  
      elif index.column() in self.controlIndexes:
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable   
        
      #return QtCore.QAbstractTableModel.flags(self, index)
      return Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable

class PAMTab(QTabWidget):
   # try QTabBar instead
   def tabChanged(self,index):
      print index # nope

class LmWebView(QWebView):
   def __init__(self,parent=None):
      QWebView.__init__()
      self.loadFinished.connect(self.handleLoadFinished)
      
   def handleLoadFinished(self,):
      pass

class Ui_Dialog(object):
   
   def tabBarSetUp(self):
      
      
      self.tableView = self.setUpTable()
      self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableView.dragEnabled()
      
      #########  folder tab
      self.folderPage = QWidget()
      self.folderLayout = QVBoxLayout(self.folderPage)
      
      self.setUpFolderHintService()
      self.setUpFolderTreeView()
      
      self.folderLayout.addWidget(self.folderHint.combo)
      self.folderLayout.addWidget(self.folderTreeView)
      
      self.tabWidget = QTabBar()
      #self.tabWidget.setStyleSheet("QTabBar::tab { height: 32px; width: 82px; }")
      #self.tabWidget.setStyleSheet("QTabBar::tab:selected { margin-left: -2px; margin-right: -2px; }")
      newExpBut = QPushButton("New")
      newExpBut.setAutoDefault(False)
      self.tabWidget.addTab('folder view')  # for QTabBar, needs different layout
      self.tabWidget.addTab('table view')
      self.tabWidget.setTabButton(1,QTabBar.RightSide,newExpBut)
      
      self.tabBarVertLayout = QVBoxLayout()
      self.tabBarVertLayout.setMargin(0)
      self.tabBarVertLayout.addWidget(self.tabWidget)
      self.tabBarVertLayout.addWidget(self.folderPage)
   
   def regularTabLayout(self):
      
      ##### tabs
      self.tabWidget = QTabWidget()
      
      #########  folder tab
      self.folderPage = QWidget()
      self.folderLayout = QVBoxLayout(self.folderPage)

      
      self.setUpFolderHintService()
      #folderWin = QTextEdit()
      self.setUpFolderTreeView()
      self.folderLayout.addWidget(self.folderHint.combo)
      self.folderLayout.addWidget(self.folderTreeView)
      
      #########  table tab
      self.tablePage = QWidget()
      self.tableLayout = QVBoxLayout(self.tablePage)
      self.tableView = self.setUpTable()
      self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableView.dragEnabled()
      self.tableView.setDragDropMode(QAbstractItemView.DragOnly)
      
      self.tableLayout.addWidget(self.tableView)
      
      ##################
      self.tabWidget.addTab(self.folderPage, 'folder view')
      self.tabWidget.addTab(self.tablePage, 'table view')
      
      #newExpBut = QPushButton("New")
      #newExpBut.setAutoDefault(False)
      #self.tabWidget.setTabButton(1,QTabBar.RightSide,newExpBut)
   
   def setupUi(self, experimentname=''):
      self.resize(698, 410)   # orgin 648, 410
      self.setMinimumSize(698, 470)
      self.setMaximumSize(698, 470)
      #self.setSizeGripEnabled(True)
      
      TopLayout = QVBoxLayout(self)
      
      MainLayout = QHBoxLayout()  # might not want self here, had self origninally
      
      pythonCommandText = QTextEdit(">>>")
      #pythonCommandText.setStyleSheet("QFrame {border-top-style:dotted}")
      pythonCommandText.setMaximumHeight(55)
      pythonCommandText.setEnabled(False)
      
      TopLayout.addLayout(MainLayout)
      pythonHoriz = QHBoxLayout()
      #int left, int top, int right, int bottom
      pythonHoriz.setContentsMargins(31, 0, 0, 0)
      pythonHoriz.addWidget(pythonCommandText)
      TopLayout.addLayout(pythonHoriz)
      ##### tabs
      self.tabWidget = QTabWidget()
      
      ########  folder tab
      self.folderPage = QWidget()
      self.folderLayout = QVBoxLayout(self.folderPage)
      
      #self.hintCombo = QComboBox()
      self.setUpFolderHintService()
      #folderWin = QTextEdit()
      self.setUpFolderTreeView()
      self.folderLayout.addWidget(self.folderHint.combo)
      self.folderLayout.addWidget(self.folderTreeView)
      
      #########  table tab
      self.tablePage = QWidget()
      self.tableLayout = QVBoxLayout(self.tablePage)
      self.tableView = self.setUpTable()
      self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableView.dragEnabled()
      self.tableView.setDragDropMode(QAbstractItemView.DragOnly)
      
      self.tableLayout.addWidget(self.tableView)
      ####################
      #    new exp tab
      self.newExpPage = QWidget()
      self.newLayout = QVBoxLayout(self.newExpPage)
      self.newLayout.setContentsMargins(14, 36, 14, 87)
      
      #self.newLayout.setMargin(0)
      self.expName = QLineEdit()
      self.epsg   = QLineEdit()
      exl = QLabel("Experiment Name")
      exl.setMaximumHeight(35)
      self.newLayout.addWidget(exl)
      self.newLayout.addWidget(self.expName)
      epl = QLabel("EPSG")
      epl.setMaximumHeight(35)
      self.newLayout.addWidget(epl)
      self.newLayout.addWidget(self.epsg)
      self.newLayout.addWidget(QWidget())
      finishedBut = QPushButton("Done")
      finishedBut.setAutoDefault(False)
      self.newLayout.addWidget(finishedBut)
      
      ##################
      self.tabWidget.addTab(self.folderPage, 'search species')
      self.tabWidget.addTab(self.tablePage, 'table')
      self.tabWidget.addTab(self.newExpPage,'new experiment')
      #self.regularTabLayout()
      #self.tabBarSetUp()
      
      #################  Tree and Map  ############
      #  QWeb  put this in its own method?
      self.treeWebView = QWebView()
      self.treeWebView.loadFinished.connect(self.handleLoadFinished)
      self.treeWebView.setMaximumSize(300, 600)
      self.treeWebView.setPage(WebPage())
      self.treeWebView.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,
                                                      True)
      self.treeWebView.page().mainFrame().addToJavaScriptWindowObject("pyDialog", self)
      
      #pluginDir = os.path.dirname(os.path.realpath(__file__)) # gets the plugin tools directory
      url = os.path.join(self.currentDir,"QWeb","PAMTreeWeb.html")
      if self.OSXLinux:
         url = "file:///%s" % (url)
      else:
         url = "file:///%s" % (os.path.normpath(url).replace("\\","/"))
         
      self.treeWebView.load(QUrl(url))
      ############################################
   
      ###### map ####
      self.mapWebView = QWebView()
      self.mapWebView.hide()
      self.mapWebView.setMaximumSize(300, 600)
      self.mapWebView.setPage(WebPage())
      self.mapWebView.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,
                                                      True)
      self.folderTreeView.mapWebView = self.mapWebView
      self.mapWebView.page().mainFrame().addToJavaScriptWindowObject("pyDialogMap", self)
      
      #pluginDir2 = os.path.dirname(os.path.realpath(__file__)) # gets the plugin tools directory
      mapUrl = os.path.join(self.currentDir,"QWeb","PAMMapSelect.html")
      if self.OSXLinux:
         url = "file:///%s" % (mapUrl)
      else:
         url = "file:///%s" % (os.path.normpath(mapUrl).replace("\\","/"))
      
      self.mapWebView.load(QUrl(mapUrl))
      
      
      #####################
      
      
      vWidget = QWidget()
      treeVLayout = QVBoxLayout(vWidget)
      treeVLayout.setMargin(0)
      
      self.TreeMapButLayout = QHBoxLayout()
      self.TreeMapButLayout.setMargin(0)
      
      self.mapButton = QPushButton("map")
      self.mapButton.setAutoDefault(False)
      self.mapButton.clicked.connect(self.loadMap)
      
      self.loadBut = QPushButton('tree')
      self.loadBut.setAutoDefault(False)
      self.loadBut.clicked.connect(self.loadTree)
      
      
      
      ######### vert layout for map/tree buttons
      #vertButContainer = 
      self.verticalButLayout = QVBoxLayout()
      self.verticalButLayout.setContentsMargins(0, 31, 0, 225)
      #self.verticalButLayout.setMargin(0)
      
      lassoIcon = QIcon("icons/lasso.png")
      self.drawBut = QPushButton(lassoIcon,"")
      self.drawBut.setIconSize(QSize(20,19))
      self.drawBut.setAutoDefault(False)
      self.drawBut.setMaximumSize(27, 27)
      self.drawBut.clicked.connect(lambda: self.toggleZoomDraw("D"))
      self.drawBut.setEnabled(False)
      
      self.zoomBut = QPushButton('Z')
      self.zoomBut.setAutoDefault(False)
      self.zoomBut.setMaximumSize(27, 27)
      self.zoomBut.clicked.connect(lambda: self.toggleZoomDraw("Z"))
      self.zoomBut.setEnabled(False)
      
      # clear could work for both map and tree
      clearMapIcon = QIcon("icons/clearTreeSelection.png")
      self.clearMapSelection = QPushButton(clearMapIcon,"")
      self.clearMapSelection.setIconSize(QSize(25,25))
      self.clearMapSelection.setAutoDefault(False)
      self.clearMapSelection.setMaximumSize(27, 27)
      
      refreshIcon = QtGui.QIcon("icons/refresh.png")
      self.refreshTree = QPushButton(refreshIcon,"")
      self.refreshTree.setIconSize(QSize(24,24))
      self.refreshTree.setAutoDefault(False)
      self.refreshTree.setMaximumSize(27, 27)
      
      sepTopLine = QFrame()
      sepTopLine.setFrameShape(QFrame.HLine)
      sepTopLine.setFrameShadow(QFrame.Sunken)
      
      sepBotLine = QFrame()
      sepBotLine.setFrameShape(QFrame.HLine)
      sepBotLine.setFrameShadow(QFrame.Sunken)
      #############################
      
      self.TreeMapButLayout.addWidget(self.loadBut)
      self.TreeMapButLayout.addWidget(self.mapButton)
      
      self.verticalButLayout.addWidget(sepTopLine)
      self.verticalButLayout.addWidget(self.zoomBut)
      self.verticalButLayout.addWidget(self.drawBut)
      self.verticalButLayout.addWidget(self.clearMapSelection)
      self.verticalButLayout.addWidget(self.refreshTree)
      self.verticalButLayout.addWidget(sepBotLine)
      
      #treeVLayout.addWidget(self.loadBut)
      treeVLayout.addLayout(self.TreeMapButLayout)
      treeVLayout.addWidget(self.treeWebView)
      treeVLayout.addWidget(self.mapWebView)
      
      ###################################
      MainLayout.addLayout(self.verticalButLayout)
      MainLayout.addWidget(vWidget)
      MainLayout.addWidget(QWidget())  # spacer
      MainLayout.addWidget(self.tabWidget)  
      
   def handleLoadFinished(self, ok): 
      #handler
      if ok:
         self.treeWebView.page().mainFrame().evaluateJavaScript('loadTree("%s","%s");' % (self.treeJSON,str(665)))
   
           
      
   def toggleZoomDraw(self,ZD):
      
      if ZD == "D":
         self.mapWebView.page().mainFrame().evaluateJavaScript('drawPoly();')
      elif ZD == "Z":
         self.mapWebView.page().mainFrame().evaluateJavaScript('callZoom();')
   
   def setUpFolderHintService(self,data=[]):
      """
      @summary: sets up the hint service and sets hint attribute
      combo can be added as a widget using self.hint.combo, callback
      adds extra functionality in addition to combo model
      """
      self.folderHint = PAMHint(self.client, callBack=self.callBack, setModel=False,data=data) #, serviceRoot=CURRENT_WEBSERVICES_ROOT
      archiveComboModel = ArchiveComboModel([],None)
      self.folderHint.model = archiveComboModel
      self.folderHint.combo.lineEdit().setPlaceholderText("[Start Typing]")
      #self.hint.combo.setPlaceholderText("[Start Typing]") # for line Edit
      self.folderHint.combo.setModel(archiveComboModel)
      #self.comboEvent = ComboEventHandler() # don't use, doesn't work with Solr
      #self.hint.combo.installEventFilter(self.comboEvent)  # don't use, doesn't work with Solr
      self.folderHint.combo.setStyleSheet("""QComboBox::drop-down {width: 0px; border: none;} 
                                   QComboBox::down-arrow {image: url(noimg);}""")
   
   def setUpFolderTreeView(self):
      
      self.folderTreeView = LMFolderTreeView(self.client,dialog=self)#, parent = self.folderPage)
      #self.folderTreeView = QTreeView()
      self.folderModel = BrowserTreeModel(top='Africa Mammals PAM')
      self.folderTreeView.setModel(self.folderModel)
      self.folderTreeView.setObjectName("folderTreeView")
   
   def callBack(self, items, fromTree=False,fromBBOX=False):
      
      """
      @summary: call back from hint class, where items are used to populate tree
      @param items: list of hit items
      """
      try:
         print "in call back"
         self.treeMatchesinCallBack = []  # put just sps names in here
         if len(items) > 0:
            if items[0].displayName == '':
               #print "is in here right before it crashes?"
               self.folderModel.beginRemoveRows(self.folderModel.index(0,0,QModelIndex()), 0, self.folderModel.provider.childCount()-1)
               self.folderModel.provider.childItems = []
               self.folderModel.endRemoveRows()
               self.table.tableView.setModel(PAMTableModel([['','','','']],self.header,[],[]))
               if not fromTree:
                  self.treeWebView.page().mainFrame().evaluateJavaScript('clearSelection();')
               #self.treeWebView.page().mainFrame().evaluateJavaScript('loadTree("%s","%s");' % (self.jsonUrl, self.closeId))
            else:
               row = 0
               tableLL = []
               
               self.folderModel.beginRemoveRows(self.folderModel.index(0,0,QModelIndex()), 0, self.folderModel.provider.childCount()-1)
               self.folderModel.provider.childItems = []
               self.folderModel.endRemoveRows()
               # old way, below
               #self.folderModel.provider.childItems = [] # wonder if should clear like above
               
               #print "got here"
               for sps in items:
                  #print "and here"
                  tableLL.append([sps.displayName,sps.percentPresence,sps.minPresence,sps.maxPresence])
                  
                  nameFolder = TreeItem(sps.displayName,sps.displayName,self.folderModel.provider)
                  
                  
                  presenceFolder = TreeItem('Presence Values','presence values',nameFolder)
                  
                  
                  TreeItem(sps.percentPresence,"percent presence - %s" % (sps.percentPresence),presenceFolder)
                  TreeItem(sps.minPresence,"min presence - %s" % (sps.minPresence),presenceFolder)
                  TreeItem(sps.maxPresence,"max presence - %s" % (sps.maxPresence),presenceFolder)
                  mx = -999
                  if sps.displayName.replace(" ","_") in self.tipsByName:
                     if 'mx' in self.tipsByName[sps.displayName.replace(" ","_")]:
                        mx = int(self.tipsByName[sps.displayName.replace(" ","_")]['mx'])
                  TreeItem(mx,'view presence',presenceFolder,type="MAP")
                  
                  statsFolder = TreeItem('RAD stats','RAD stats',nameFolder)
                  if sps.displayName in self.statsBySps:
                     statDict = self.statsBySps[sps.displayName] # this is a dict
                     for stat in statDict:
                        label = " %s - %s" % (stat,str(statDict[stat]))
                        TreeItem((stat,statDict[stat],sps.displayName),label,statsFolder,type="RAD")
                  
                  if not fromTree:
                     if " " in sps.displayName:
                        self.treeMatchesinCallBack.append(sps.displayName.replace(" ","_"))
                     
                  self.folderModel.insertRow(row, QModelIndex())      
                  row = row + 1
                  #print "and here"
                             
               self.folderTreeView.expand(self.folderModel.index(0,0,QModelIndex()))
               #print "expanded"
               if not fromTree:
                  if len(self.treeMatchesinCallBack) > 0:
                     if fromBBOX:
                        if len(self.treeMatchesinCallBack) > 20:
                           self.treeMatchesinCallBack = self.treeMatchesinCallBack[:20]
                        print "len in treeMatchesinCallBack for BBOX ",len(self.treeMatchesinCallBack)
                     self.selectInTree()
                     
               self.table.tableView.setModel(PAMTableModel(tableLL,self.header,[],[]))
               self.table.tableView.resizeColumnsToContents()
               self.table.tableView.horizontalHeader().setStretchLastSection(True)
         else:
            self.treeMatchesinCallBack = []
            print "len = 0"
      except Exception, e:
         self.treeMatchesinCallBack = []
         print "exception in call back"
            
   def setUpTable(self):
      
      self.tableData = [['','','','']]  
      self.table =  RADTable(self.tableData)
      self.header = ['name','percent presence','min presence','max presence']
      return self.table.createTable(self.header)   

class PAMHint(Hint):
   
   def __init__(self, client, callBack=None, setModel=True, data=[]):
      Hint.__init__(self, client, callBack=callBack, setModel=setModel)
      self.layers = data
      
   def onTextChange(self, text):
      
      noChars = len(text)
      if text == '':  # never getting in here, callback vs. callBack
         self.combo.clear()
         self.combo.clearEditText()
         if self.callback is not None:
            self.callback([FolderSpsSearchResult('', '', '','','')])
                  
      if noChars >= 3:
         if text.count(" ") == 1:  
            return
         #if ' ' in text:
         #   text.replace(' ','%20')
         self.searchOccSets(text)
    
   def getIdxFromTuples(self,currentText):
      pass
      #idx = 0
      #if self.namedTuples is not None:
      #   for sH in self.namedTuples: 
      #      # probably will need to change this inside of Qgis        
      #      #if sH.name.lower() in unicode(currentText).lower():
      #      #if sH.name.lower() in currentText.lower():
      #      #if sH.displayName.lower() in currentText.lower():
      #      if sH.displayName in currentText:
      #         break
      #      idx += 1   
      #else:
      #   print "no namedTuples"      
      #return idx 
   
   def searchOccSets(self,searchText=''):
      """
      @summary: calls hint service
      @param    searchText: text to search for
      @todo:    needs a call back, probably set on init
      """
      #print "is this here?"
      # use toUnicode(searchText).encode('utf-8') for search
      try:                                         
         matches = [v for v in self.layers if v.displayName.startswith(searchText)]    
      except Exception, e:
         print "except in searchOccsets ",str(e)
      else:
         if len(matches) > 0:
            self.model.updateList(matches)
            if self.callback is not None:
               self.callback(matches)

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

class FolderSpsSearchResult(object):
   
   """
   @summary: Data structure for species search results (Solr prj objects)
   """
   # .........................................
   def __init__(self, displayName, lyrId = None, minPresence=None,
                maxPresence=None, percentPresence=None ):
      """
      @summary: Constructor for SpeciesSearchResult object
      @param displayName: The display name for the occurrence set
      @param occurrenceSetId: The Lifemapper occurrence set id
      @param numPoints: The number of points in the occurrence set
      """
      self.displayName = displayName
      self.minPresence = minPresence
      self.maxPresence = maxPresence
      self.percentPresence = percentPresence

   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      #return "%s (%s points)" % (self.displayName, self.numPoints)
      return "%s " % (self.displayName)

class LMFolderTreeView(QTreeView):   
   
   def __init__(self, client ,tmpDir = None, parent=None, mapWebView=None, dialog=None):
         
         QTreeView.__init__(self,parent)
         self.client = client
         self.dialog = dialog
         self.setRootIsDecorated(True)
         self.RADAvg = {}
         self.coordByMtx = {}
         self.mapWebView = mapWebView
         #self.provider = PROVIDER
         #self.tmpDir = tmpDir
         self.header().hide()
         self.doubleClicked.connect(self.handleEvent)
         #self.dragEnabled()
         #self.setDragDropMode(QAbstractItemView.DragOnly)
         self.header().setResizeMode(QHeaderView.ResizeToContents)
         
   def handleEvent(self, index):
      
      # will need to get type
      #try:
         childRowIdx = index.row()
         downloadType = self.model().nodeFromIndex(index.parent()).child(childRowIdx).type
         
         if downloadType == 'RAD': # check that it is only a stat, look at orig
            stat,RADValue,sps = self.getDataFromDoubleClick(index)
            barDataList = list(csv.reader(open(os.path.join(self.dialog.currentDir,"QWeb","bar-data.txt"),'r')))
            barDataList[1][1] = RADValue
            barDataList[1][0] = sps
            if stat in self.RADAvg:
               avg = self.RADAvg[stat]
            else:
               avg = 999
            barDataList[2][1] = avg
            wr = csv.writer(open(os.path.join(self.dialog.currentDir,"QWeb","bar-data.txt"),'w')) #, dialect='excel')
            wr.writerows(barDataList)
            self.ChartDialog = RADStatsDialog(stat,self.dialog.dataFolder,self.dialog.OSXLinux)
            self.ChartDialog.setModal(False)
            self.ChartDialog.show()
            
         if downloadType == 'MAP':
            
            mx = self.model().nodeFromIndex(index.parent()).child(childRowIdx).itemData
            print "trying to map ",mx
            if int(mx) in self.coordByMtx:
               print "in dict"
               spsCSV = os.path.join(self.dialog.dataFolder,"presence-data_%s.csv" % (str(mx)))  
               wr = csv.writer(open(spsCSV,'w'))
               nl = list(self.coordByMtx[int(mx)][1])
               for l in nl:
                  l.extend(['z','z','z'])
               nl.insert(0,['lon','lat','code','city','country'])   
               wr.writerows(nl)
               if self.mapWebView is not None:
                  print "has mapView"
                  self.mapWebView.page().mainFrame().evaluateJavaScript('loadRange("%s");' % (spsCSV))
                  
      #except Exception,e:
         #$print "exception in folder event ",str(e)

   def getDataFromDoubleClick(self, itemIdx):
      """
      @summary: gets data from tree model from selection in view
      """
      
      childRowIdx = itemIdx.row()
      data = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      #leafName = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).name
      #hit = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).hit
      #parentName = self.model().nodeFromIndex(itemIdx.parent()).name
      #try:
      #   grandparent = self.model().nodeFromIndex(itemIdx.parent().parent()).name
      #except Exception, e:
      #   grandparent = ''
      ##if hit is None:
      ##   hit = True  # this is temporary, to handle hit when still using them
      #return hit, lmId, parentName, leafName, grandparent
      return data[0],data[1],data[2]

class RADStatsDialog(QDialog):
   
   def __init__(self,statName,dataFolder,OSXLinux):
      QDialog.__init__(self)
      self.setWindowTitle("Statistic: "+statName)
      self.resize(380, 350)
      self.setMinimumSize(380, 350)
      self.setMaximumSize(1300, 1300)
      self.setSizeGripEnabled(True)
      self.chartWebView = QWebView(self)
      self.chartWebView.setMaximumSize(500, 500)
      self.chartWebView.setPage(WebPage())
      self.chartWebView.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,
                                                      True)
      
      pluginDir = os.path.dirname(os.path.realpath(__file__))
      url = os.path.join(pluginDir,"QWeb","RADStats2.html") 
      if OSXLinux:
         url = "file:///%s" % (url)
      else:
         url = "file:///%s" % (os.path.normpath(url).replace("\\","/"))
      
      
      self.chartWebView.load(QUrl(url))
      
class PAMDialog(QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   #__metaclass__ = classmaker()
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, inputs=None, client=None, epsg=None,
                experimentname='',expId=None, 
                treeJSON="file:///home/jcavner/PhyloXM_Examples/Liebold_notEverythinginMatrix.json",
                presenceDict=None,dataFolder=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      self.getOS()
      self.currentDir = os.path.dirname(os.path.realpath(__file__))
      self.dataFolder = dataFolder
      self.setWindowTitle("Archive (PAM) Browser")
      self.client = client
      #self.jsonUrl = treeJSON  # not being used
      self.treeJSON = treeJSON
      self.searchJSON = treeJSON
      self.prepareTreeForSearch()
      
      self._availablestats = None
      self.statsTypes = {}
      
      self.setupUi(experimentname=experimentname)
      
      self.getPALayers(expId,presenceDict)
   
   def getOS(self):
      
      self.OSXLinux = True
      if sys.platform == "win32" or sys.platform == "win64":
         self.OSXLinux = False
      
   
   def bboxCrossBbox(self,searchBBOX,spsBBOXDict):
      """
      @summary: returns true if bbox's intersect
      """
      
      spsMinX = spsBBOXDict['minX']
      spsMinY = spsBBOXDict['minY']
      spsMaxX = spsBBOXDict['maxX']
      spsMaxY = spsBBOXDict['maxY']
      
      sMinX = searchBBOX[0][0]
      sMinY = searchBBOX[0][1]
      sMaxX = searchBBOX[1][0]
      sMaxY = searchBBOX[1][1]
      
      hoverlaps = True
      voverlaps = True
      if (sMinX > spsMaxX) or (sMaxX < spsMinX):
         hoverlaps = False
      if (sMaxY < spsMinY) or (sMinY > spsMaxY):
         voverlaps = False
          
      return hoverlaps and voverlaps
   
   def pointInBBOX(self,searchBBOX, point):
      
      sMinX = searchBBOX[0][0]
      sMinY = searchBBOX[0][1]
      sMaxX = searchBBOX[1][0]
      sMaxY = searchBBOX[1][1]
      
      
      
      pointX = point[0]
      pointY = point[1]
      
      inside = False
      #print '(%s >= %s and %s <= %s) and (%s <= %s and %s >= s%s' % (str(pointX), str(sMinX), str(pointX), str(sMaxX), str(pointY),str(sMaxY),str(pointY),str(sMinY))
      if (pointX >= sMinX and pointX <= sMaxX) and (pointY <= sMaxY and pointY >= sMinY):
         inside = True
          
      return inside
   
   @pyqtSlot(str)
   def searchByBBOX(self,bboxStr):
      
      #self.treeWebView.page().mainFrame().evaluateJavaScript('loadTree("%s","%s");' % ("/home/jcavner/WorkshopWS/AfricaMammals_1055/tree/tree.json",str(665)))
      # prepare bbox
      minsStr = bboxStr.split(';')[0]
      maxsStr = bboxStr.split(';')[1]
      
      minX = float(minsStr.split(',')[0])
      minY = float(minsStr.split(',')[1])
      
      maxX = float(maxsStr.split(',')[0])
      maxY = float(maxsStr.split(',')[1])
      
      searchBBOX = ((minX,minY),(maxX,maxY))
      sendToCallBack = []             
      for mx in self.rangeByMtx: # data structure with coords
         spsBBOXDict = self.rangeByMtx[mx][0]
         if self.bboxCrossBbox(searchBBOX,spsBBOXDict):
            for point in self.rangeByMtx[mx][1]:
               if self.pointInBBOX(searchBBOX,point):
                  spsName = self.tipsByMx[mx]['name']
                  paValues = self.palookup[spsName]
                  sendToCallBack.append(paValues)
                  break
            
      self.callBack(sendToCallBack,fromTree=True,fromBBOX=True)
         # if intersect, loop thru coords and get mx
         # use name to get pa values, use palookup
         # build pa object, don't have to do this
      # send to pa objects to call back
      
   def prepareTreeForSearch(self):
      
      self.genusDict = {}
      self.comboDataModel = []
      self.pilotList = []
      self.allClades = {} 
      ########  new for Browser ####
      self.selectedinTreeFromFolder = []
      self.treeMatchesinCallBack = []
      self.tipsByName = {}
      self.tipsByMx = {}
      ########  experimental ##########
      self.tips = [] # list with all the tip pathIds
      self.repeatIds = []
      ########################
      jsonStr = open(self.searchJSON).read()
      treeDict = json.loads(str(jsonStr))
      self.flattenTreeToTips(treeDict)
      self.calcNoDesc()
      self.addGeneraToHintList()
   
   def loadMap(self):
      
      self.refreshTree.setEnabled(False)
      self.drawBut.setEnabled(True)
      self.zoomBut.setEnabled(True)
      
      if self.treeWebView.isVisible():
         self.treeWebView.hide()
      self.mapWebView.show()
      
   
   def loadTree(self):
      
      self.refreshTree.setEnabled(True)
      self.drawBut.setEnabled(False)
      self.zoomBut.setEnabled(False)
      
      if self.mapWebView.isVisible():
         self.mapWebView.hide()
      if not self.treeWebView.isVisible():
         self.treeWebView.show()
         #return  # big ???
      #if not self.flipOne:
      #self.treeWebView.page().mainFrame().evaluateJavaScript('loadTree("%s","%s");' % (self.jsonUrl, self.closeId))      
      #self.flipOne = True
   def zoomItem(self):
      
      if len(self.selectedinTreeFromFolder) > 0:
         if len(self.selectedinTreeFromFolder) > 5:
            idx = len(self.selectedinTreeFromFolder) / 2
            item = self.selectedinTreeFromFolder[int(idx)]
            print "zoom name check ",item["name"]
         else:
            item = self.selectedinTreeFromFolder[0]
            
         self.treeWebView.page().mainFrame().evaluateJavaScript('zoomToLeaf("%s","%s", "%s");' % (item["x"],item["y"],item["pathId"]))
     
   def selectInTree(self):
      
      
      paths = []
      ids   = []
      for sps in self.treeMatchesinCallBack:
         if sps in self.tipsByName:
            try:
               paths.append(self.tipsByName[sps]["path"])
               ids.append(self.tipsByName[sps]["pathId"])
            except Exception, e:
               print "not appending ",str(e)
            
      tipsString = ','.join(ids)     
      
      # make a list of lists of the tipless paths 
      llTiplessPaths = [map(int,ps.split(',')[1:]) for ps in paths]                  
      pathsUnionList = list(set().union(*llTiplessPaths))
      pathsUnionList.sort(reverse=True)
            
      # now convert to a string
      unionString = ','.join(map(str,pathsUnionList))
      try:        
         self.treeWebView.page().mainFrame().evaluateJavaScript('findClades("%s","%s","%s");' % (unionString,tipsString,'True'))
      except Exception, e:
         print "EXCEPT IN select in Tree ",(str)
      
      #self.zoomItem()
      
   @pyqtSlot(str)
   def addToLeavesforZoom(self,leavesJSON):
      
      leaves = json.loads(str(leavesJSON))
      self.selectedinTreeFromFolder = leaves["selected"]
      print self.selectedinTreeFromFolder
   
   @pyqtSlot(str)
   def addtoFolders(self,leavesJSON):
      """
      @summary: coming from javascript, adds to folder view
      """
       
      leaves = json.loads(str(leavesJSON))
      #needs to clear folder view ??
      self.folderHint.combo.clear()
      self.folderHint.combo.clearEditText()
      self.callBack([FolderSpsSearchResult('', '', '','','')],fromTree=True)
      
      inner = leaves.values()
      inner.sort(key=operator.itemgetter('name')) # sorts a list of dictionaries by a specific key
      
      items = []
      for d in inner:
         k = d["name"]
         if k in self.palookup:
            items.append(self.palookup[k])
         #result = SelectedResult(d["name"],d["x"],d["y"],d["pathId"],d["path"])
         #if d.has_key("length"):
         #   result.setLength(d["length"])
         #if d.has_key("mx"):
         #   result.setMatrix(d["mx"])
         #items.append(result)                               
      self.callBack(items,fromTree=True)          
      #for item in items:
      #   SelectedItem(item,self.list)  # this added to list items because of parent?
      #self.plotButton.setEnabled(True)
      #self.calcMNTD()
   
   def addGeneraToHintList(self):
     
      for genus in self.genusDict.keys():
         pathList = list(self.genusDict[genus][0])
         pathList.sort(reverse=True)
         pathStr = ','.join(map(str,pathList))
         gd = {}
         gd['name'] = genus
         gd['path'] = pathStr
         self.pilotList.append(gd)
   
   def flattenTreeToTips(self, clade):
      """
      @summary: builds leaf list, and allClades (without children) dict
      """
      if "pathId" in clade:
         self.allClades[clade["pathId"]] = dict((k,v) for k,v in clade.items() if k != "children")
         self.repeatIds.extend(clade['path'].split(','))  # map(int,clade['path'].split(','))
      if "children" in clade:  
         for child in clade["children"]:
            self.flattenTreeToTips(child)
      else:
         # this means it is a tip
         ########## new for browser
         if 'mx' in clade:
            self.tipsByMx[clade['mx']] = clade
         self.tipsByName[clade["name"]] = clade 
         ###################
         self.tips.append(clade["pathId"]) # list with all the tip pathIds
         self.pilotList.append(clade)
         if "_" in clade["name"]:  # want to probably think about this
            genus = clade["name"].split("_")[0]
            pl    = clade["path"].split(',')
            tip   = clade["pathId"]
            m     = map(int,pl[1:]) 
            if genus in self.genusDict:           
               self.genusDict[genus][0].update(m)
               self.genusDict[genus][1] = '%s,%s' % (self.genusDict[genus][1],tip)
            else:
               self.genusDict[genus] = [set(m),tip]
   
   
   def calcNoDesc(self):
      """
      @summary: uses Counter from collections to group, and then sorts
      ,counts the number of times a pathId is in a path
      """
      self.noIdInPaths = Counter(self.repeatIds)
      # a list of tuples sorted by the second element in each tuple
      sortedFreq = sorted(self.noIdInPaths.iteritems(), key=operator.itemgetter(1),reverse=True)
      
      self.closeId = sortedFreq[2][0]
      
      print "C ",self.closeId
     
   def getPALayers(self,expId, presenceDict):
      ##  CAN"T PICKLE LM OBJECTS, requires live call for now 
      try:
         palyrs = self.client.rad.getPALayers(expId)
         #palyrs = [] 
         if len(palyrs) == 0:
            raise
      except Exception, e:
         print "EXCEPTION IN GET PA LAYERS ",str(e)
         self.palyrs = None # ?
      else:
         #print palyrs
         self.palyrs = palyrs # ?
         l = []
         d = {}
         for pa in palyrs:
            o = FolderSpsSearchResult(pa.name.replace("_"," "),minPresence=pa.minPresence,
                                      maxPresence=pa.maxPresence,
                                      percentPresence=pa.percentPresence)
            l.append(o)
            d[pa.name] = o
         self.folderHint.layers = l
         self.palookup = d  #look up Folder objects/pa by name
      # RAD stats dynamic
      #self.buildStatsLookup()
      #pD = cPickle.load(open(presenceDict))
      #self.lyrsPresent = pD[1438]['layersPresent'] # hardcoding this bucketId for now
      #self.getSpsStats()
      #self.buildStatsBySps()
      # replaced with pickle
      self.rangeByMtx = cPickle.load(open(os.path.join(self.dataFolder,"coordByMtx_2.pkl"))) # _2 has bbox in first element
      self.statsBySps = cPickle.load(open(os.path.join(self.dataFolder,"statsBySps.pkl")))
      # write pickle, just once
      #cPickle.dump(self.statsBySps,open("/home/jcavner/PAMBrowser/statsBySps.pkl","wb"))
      self.folderTreeView.coordByMtx = self.rangeByMtx
      self.buildSpsAvg()
   
   def buildSpsAvg(self):
      
      self.avgs = {}
      #print self.statsBySps
      totalSps = float(len(self.statsBySps))
      #print 'total ',totalSps
      for sps in self.statsBySps: # sps key
         for stat in self.statsBySps[sps]:
            if stat not in self.avgs:
               self.avgs[stat] = float(self.statsBySps[sps][stat])
            else:
               self.avgs[stat] += float(self.statsBySps[sps][stat])
        
      for s in self.avgs:
         self.avgs[s] =  self.avgs[s] / totalSps    
      self.folderTreeView.RADAvg = self.avgs
      
   def buildStatsBySps(self):
      
      # for only mx
      # get the mx for the sps, if True in lyrs Present
      # sort lyrsPresent keys
      lpKeys = [k for k in self.lyrsPresent.keys() if self.lyrsPresent[k]]
      lpKeys.sort()
      self.statsBySps = {}
      for mx in self.tipsByMx:
         if self.lyrsPresent[int(mx)]:
            name = self.tipsByMx[mx]['name'].replace("_"," ")  # has under_bar
            idx = lpKeys.index(mx)  # get idx of mx in lpKeys
            spsDict = {}
            for stat in self.statsByStatName:
               spsDict[stat] = self.statsByStatName[stat][idx]   
            self.statsBySps[name] = spsDict
      #print len(self.statsBySps)
   def getSpsStats(self):
      
      self.statsByStatName = {}
      for stat in self.getAvailableSpeciesStats():
         v = self.getData(3103,stat)  # 3103, orig pamsum
         self.statsByStatName[stat] = v
   
   def getData(self, pam, stat):
      """
      @summary: this returns a column (with respect to the table) for a stat for
      a pam
      """
      args = {}
      args.update({'expId':1055, 'bucketId':1438})
      args.update({'pamSumId':pam})
      args.update({'stat':stat})
      try:
         stats = self.client.rad.getPamSumStatistic(**args)      
      except:
         return False
      else:
         return stats
   
   @property
   def availablestats(self):
      if self._availablestats is None or self._availablestats == False:
         self.setAvailableStats()      
      return self._availablestats
      
   def setAvailableStats(self):
      statsinputs = {}
      statsinputs.update({'expId':1055, 'bucketId':1438})
      statsinputs.update({'pamSumId':'original','stat':None})
      try:
         stats = self.client.rad.getPamSumStatistic(**statsinputs) 
      except:
         stats = False     
      self._availablestats = stats
      
   def buildStatsLookup(self):
      
      types = ['specieskeys' , 'siteskeys' , 'diversitykeys']
      statsType = {}
      for type in types:
         arguments = {}
         arguments.update({'expId':1055, 'bucketId':1438})
         arguments.update({'pamSumId':'original'})
         arguments.update({'keys':type})
         try:
            keys = self.client.rad.getPamSumStatisticsKeys(**arguments)
         except:
            pass
         else:
            values = [type.replace('keys','') for x in range(0,len(keys))]          
            #d = {k:v for k,v in zip(keys,values)}
            d = dict(zip(keys,values))
            statsType.update(d)
      self.statsTypes.update(statsType)
   
    
   def getAvailableSpeciesStats(self):
      """
      @summary: builds a list of of available species based stats
      """
      availablestats = self.availablestats
       
      availablespecies = []
      if availablestats:      
         for stat in availablestats:
            if stat in self.statsTypes.keys():
               if (self.statsTypes[stat] == 'species') and ('sigma' not in stat)  and ('covariance' not in stat):
                  availablespecies.append(stat)          
      else:
         message = "There is a problem with the statistical service"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      return availablespecies 
    

if __name__ == "__main__":
#  
   #QTableWidget, can use setCellWidget() to put insert a button into a table
   
   from LmClient.lmClientLib import LMClient
   client =  LMClient()
   client.login(userId='Workshop', pwd='Workshop')
   
   expId = 1055
   epsg = 3410
   bucket = 1438
   dataFolder = "/home/jcavner/PAMBrowser"
   treeJson = os.path.join(dataFolder,"tree.json")
   sitesPresentPath = os.path.join(dataFolder,"sitesPresent.pkl")
   qApp = QApplication(sys.argv)
   
   d = PAMDialog(None,client=client,expId = expId,
                 treeJSON=treeJson,presenceDict=sitesPresentPath,
                 dataFolder=dataFolder)
   
   d.show()
   
   sys.exit(qApp.exec_())
   
      