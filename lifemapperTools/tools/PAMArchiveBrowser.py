
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
from lifemapperTools.common.LmQTree import BrowserTreeModel, TreeItem

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
      self.resize(648, 410)
      self.setMinimumSize(648, 410)
      self.setMaximumSize(648, 410)
      self.setSizeGripEnabled(True)
      
      MainLayout = QHBoxLayout(self)
      
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
      
      ##################
      self.tabWidget.addTab(self.folderPage, 'folder view')
      self.tabWidget.addTab(self.tablePage, 'table view')
      
      #self.regularTabLayout()
      #self.tabBarSetUp()
      
      #################  Tree and Map  ############
      #  QWeb  put this in its own method?
      self.treeWebView = QWebView()
      self.treeWebView.setMaximumSize(300, 600)
      self.treeWebView.setPage(WebPage())
      self.treeWebView.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,
                                                      True)
      self.treeWebView.page().mainFrame().addToJavaScriptWindowObject("pyDialog", self)
      url = "http://google.com"
      pluginDir = os.path.dirname(os.path.realpath(__file__)) # gets the plugin tools directory
      url = os.path.join(pluginDir,"PAMTreeWeb.html")
      url = "file:///%s" % (url)
      print url
      self.treeWebView.load(QUrl(url))
      
   
      ###### map ####
      self.mapWebView = QWebView()
      self.mapWebView.hide()
      self.mapWebView.setMaximumSize(300, 600)
      self.mapWebView.setPage(WebPage())
      self.mapWebView.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,
                                                      True)
      self.folderTreeView.mapWebView = self.mapWebView
      #self.mapWebView.page().mainFrame().addToJavaScriptWindowObject("pyDialog", self)
      url2 = "http://google.com"
      pluginDir2 = os.path.dirname(os.path.realpath(__file__)) # gets the plugin tools directory
      url2 = os.path.join(pluginDir2,"PAMMap.html")
      url2 = "file:///%s" % (url2)
      print url2
      #url2 = "file:///home/jcavner/PAMBrowser/map.html"
      self.mapWebView.load(QUrl(url2))
      
      
      #####################
      
      
      vWidget = QWidget()
      treeVLayout = QVBoxLayout(vWidget)
      
      self.TreeMapButLayout = QHBoxLayout()
      self.TreeMapButLayout.setMargin(0)
      
      self.mapButton = QPushButton("map")
      self.mapButton.setAutoDefault(False)
      self.mapButton.clicked.connect(self.loadMap)
      
      self.loadBut = QPushButton('tree')
      self.loadBut.setAutoDefault(False)
      self.loadBut.clicked.connect(self.loadTree)
      
      self.TreeMapButLayout.addWidget(self.loadBut)
      self.TreeMapButLayout.addWidget(self.mapButton)
      
      #treeVLayout.addWidget(self.loadBut)
      treeVLayout.addLayout(self.TreeMapButLayout)
      treeVLayout.addWidget(self.treeWebView)
      treeVLayout.addWidget(self.mapWebView)
      
      ###################################
      
      MainLayout.addWidget(vWidget)
      MainLayout.addWidget(self.tabWidget)   # good
      #MainLayout.addLayout(self.tabBarVertLayout)
   
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
      
      self.folderTreeView = LMFolderTreeView(self.client)#, parent = self.folderPage)
      #self.folderTreeView = QTreeView()
      self.folderModel = BrowserTreeModel(top='Africa Mammals PAM')
      self.folderTreeView.setModel(self.folderModel)
      self.folderTreeView.setObjectName("folderTreeView")
   
   def callBack(self, items, fromTree=False):
      
      """
      @summary: call back from hint class, where items are used to populate tree
      @param items: list of hit items
      """
      self.treeMatchesinCallBack = []
      if len(items) > 0:
         if items[0].displayName == '':
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
            self.folderModel.provider.childItems = []
            for sps in items:
               
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
                           
            self.folderTreeView.expand(self.folderModel.index(0,0,QModelIndex()))
            
            if not fromTree:
               if len(self.treeMatchesinCallBack) > 0:
                  self.selectInTree()
                  
            self.table.tableView.setModel(PAMTableModel(tableLL,self.header,[],[]))
            self.table.tableView.resizeColumnsToContents()
            self.table.tableView.horizontalHeader().setStretchLastSection(True)
            
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
      
      # use toUnicode(searchText).encode('utf-8') for search
      try:                                         
         matches = [v for v in self.layers if v.displayName.startswith(searchText)]    
      except Exception, e:
         pass
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
   
   def __init__(self, client ,tmpDir = None, parent=None, mapWebView=None):
         
         QTreeView.__init__(self,parent)
         self.client = client
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
      childRowIdx = index.row()
      downloadType = self.model().nodeFromIndex(index.parent()).child(childRowIdx).type
      
      if downloadType == 'RAD': # check that it is only a stat, look at orig
         stat,RADValue,sps = self.getDataFromDoubleClick(index)
         barDataList = list(csv.reader(open("/home/jcavner/PAMBrowser/bar-data.csv",'r')))
         barDataList[1][1] = RADValue
         barDataList[1][0] = sps
         if stat in self.RADAvg:
            avg = self.RADAvg[stat]
         else:
            avg = 999
         barDataList[2][1] = avg
         wr = csv.writer(open("/home/jcavner/PAMBrowser/bar-data.csv",'w')) #, dialect='excel')
         wr.writerows(barDataList)
         self.ChartDialog = RADStatsDialog(stat)
         self.ChartDialog.setModal(False)
         self.ChartDialog.show()
         
      if downloadType == 'MAP':
         
         mx = self.model().nodeFromIndex(index.parent()).child(childRowIdx).itemData
         print "trying to map ",mx
         if int(mx) in self.coordByMtx:
            print "in dict"
            spsCSV = "/home/jcavner/PAMBrowser/presence-data_%s.csv" %(str(mx))
            wr = csv.writer(open(spsCSV,'w'))
            nl = list(self.coordByMtx[int(mx)])
            for l in nl:
               l.extend(['z','z','z'])
            nl.insert(0,['lon','lat','code','city','country'])   
            wr.writerows(nl)
            if self.mapWebView is not None:
               print "has mapView"
               self.mapWebView.page().mainFrame().evaluateJavaScript('loadRange("%s");' % (spsCSV))

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
   
   def __init__(self,statName):
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
      #self.chartWebView.page().mainFrame().addToJavaScriptWindowObject("pyDialog", self)
      #url = "http://google.com"
      #pluginDir = os.path.dirname(os.path.realpath(__file__)) # gets the plugin tools directory
      #browserPath = "/home/jcavner/PAMBrowser/"
      #url = os.path.join(browserPath,"RADStats.html")
      url = "file:///home/jcavner/PAMBrowser/RADStats2.html"  # %s" % (url)
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
                presenceDict=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setWindowTitle("Archive (PAM) Browser")
      self.client = client
      self.jsonUrl = treeJSON
      self.searchJSON = treeJSON
      self.prepareTreeForSearch()
      
      self._availablestats = None
      self.statsTypes = {}
      
      self.setupUi(experimentname=experimentname)
      
      self.getPALayers(expId,presenceDict)
      
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
      
      if self.treeWebView.isVisible():
         self.treeWebView.hide()
      self.mapWebView.show()
      
   
   def loadTree(self):
      
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
      
      try:
         palyrs = self.client.rad.getPALayers(expId)  
      except:
         self.palyrs = None # ?
      else:
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
         self.palookup = d
      # RAD stats dynamic
      #self.buildStatsLookup()
      #pD = cPickle.load(open(presenceDict))
      #self.lyrsPresent = pD[1438]['layersPresent'] # hardcoding this bucketId for now
      #self.getSpsStats()
      #self.buildStatsBySps()
      # replaced with pickle
      self.rangeByMtx = cPickle.load(open("/home/jcavner/PAMBrowser/coordByMtx.pkl"))
      self.statsBySps = cPickle.load(open("/home/jcavner/PAMBrowser/statsBySps.pkl"))
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


   from LmClient.lmClientLib import LMClient
   client =  LMClient()
   client.login(userId='Workshop', pwd='Workshop')
   
   expId = 1055
   epsg = 3410
   bucket = 1438
   treeJson = "/home/jcavner/WorkshopWS/AfricaMammals_1055/tree/tree.json"
   sitesPresentPath = "/home/jcavner/WorkshopWS/AfricaMammals_1055/sitesPresent.pkl"
   qApp = QApplication(sys.argv)
   
   d = PAMDialog(None,client=client,expId = expId,
                 treeJSON=treeJson,presenceDict=sitesPresentPath)
   
   d.show()
   
   sys.exit(qApp.exec_())