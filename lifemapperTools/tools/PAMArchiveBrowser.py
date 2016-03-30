
import sys, os
import logging
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


class Ui_Dialog(object):
   
   def setupUi(self, experimentname=''):
      self.resize(648, 410)
      self.setMinimumSize(648, 410)
      self.setMaximumSize(648, 410)
      self.setSizeGripEnabled(True)
      
      MainLayout = QHBoxLayout(self)
      
      ##### tabs
      self.tabWidget = QTabWidget()
      
      #########  folder tab
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
      
      self.tableLayout.addWidget(self.tableView)
      
      ##################
      self.tabWidget.addTab(self.folderPage, 'folder view')
      self.tabWidget.addTab(self.tablePage, 'table view')
      
      ######################
      #  QWeb  put this in its own method
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
      self.treeWebView.load(QUrl(url))
      #####################
      
      
      vWidget = QWidget()
      treeVLayout = QVBoxLayout(vWidget)
      
      self.loadBut = QPushButton('load')
      self.loadBut.setAutoDefault(False)
      self.loadBut.clicked.connect(self.loadTree)
      treeVLayout.addWidget(self.loadBut)
      treeVLayout.addWidget(self.treeWebView)
      ######################
      #MainLayout.addWidget(QTextEdit())
      #MainLayout.addWidget(self.treeWebView)
      MainLayout.addWidget(vWidget)
      MainLayout.addWidget(self.tabWidget)
   
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
      
      self.folderTreeView = LMFolderTreeView(self.client, parent = self.folderPage)
      #self.folderTreeView = QTreeView()
      self.folderModel = BrowserTreeModel(top='pam')
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
            #self.treeMatchesinCallBack = []
         else:
            row = 0
            self.folderModel.provider.childItems = []
            for sps in items:
               
               nameFolder = TreeItem(sps.displayName,sps.displayName,self.folderModel.provider)
               #occSetName = "occurrence set (%s points)" % sps.numPoints
               #occSet     = TreeItem(sps.occurrenceSetId,occSetName,nameFolder,
               #                      type='new')
               stats = TreeItem('presence values','presence values',nameFolder)
               #try:
               #   for m in sps.models:
               #      mF = TreeItem(m.algorithmCode,m.algorithmCode,nameFolder)
               #      for p in m.projections:
               #         TreeItem(p.projectionId,p.projectionScenarioCode,mF,type='new')
               #except:
               #   pass
               if not fromTree:
                  if " " in sps.displayName:
                     self.treeMatchesinCallBack.append(sps.displayName.replace(" ","_"))
                  
               self.folderModel.insertRow(row, QModelIndex())      
               row = row + 1
                           
            self.folderTreeView.expand(self.folderModel.index(0,0,QModelIndex()))
            
            if not fromTree:
               if len(self.treeMatchesinCallBack) > 0:
                  self.selectInTree()
         
   def setUpTable(self):
      
      self.tableData = [['start','','']]  
      self.table =  RADTable(self.tableData)
      header = ['1','2','3']
      return self.table.createTable(header)   

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
            if len(text.split(" ")) == 1: # don't know, look in orig
               self.combo.clear()
               self.combo.clearEditText()
         #   currText = self.combo.currentText()
         #   idx = self.getIdxFromTuples(currText)
         #   self.combo.setCurrentIndex(idx) 
               
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
   
   def __init__(self, client ,tmpDir = None, parent=None):
         
         QTreeView.__init__(self,parent)
         self.client = client
         self.setRootIsDecorated(True)
         #self.provider = PROVIDER
         #self.tmpDir = tmpDir
         self.header().hide()
         #self.doubleClicked.connect(self.handleEvent)
         #self.dragEnabled()
         #self.setDragDropMode(QAbstractItemView.DragOnly)
         self.header().setResizeMode(QHeaderView.ResizeToContents)
         

      
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
                treeJSON="file:///home/jcavner/PhyloXM_Examples/Liebold_notEverythinginMatrix.json"):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.client = client
      self.jsonUrl = treeJSON
      self.searchJSON = treeJSON
      self.prepareTreeForSearch()
      
      
      self.setupUi(experimentname=experimentname)
      
      self.getPALayers(expId)
      
   def prepareTreeForSearch(self):
      
      self.genusDict = {}
      self.comboDataModel = []
      self.pilotList = []
      self.allClades = {} 
      ########  new for Browser ####
      self.selectedinTreeFromFolder = []
      self.treeMatchesinCallBack = []
      self.tipsByName = {}
      ########  experimental ##########
      self.tips = [] # list with all the tip pathIds
      self.repeatIds = []
      ########################
      jsonStr = open(self.searchJSON).read()
      treeDict = json.loads(str(jsonStr))
      self.flattenTreeToTips(treeDict)
      self.calcNoDesc()
      self.addGeneraToHintList()
   
   def loadTree(self):
      
      self.treeWebView.page().mainFrame().evaluateJavaScript('loadTree("%s","%s");' % (self.jsonUrl, self.closeId))      
   
   def zoomItem(self):
      
      if len(self.selectedinTreeFromFolder) > 0:
         if len(self.selectedinTreeFromFolder) > 5:
            idx = int(len(self.selectedinTreeFromFolder)) / 2
            item = int(self.selectedinTreeFromFolder[idx])
         else:
            item = self.selectedinTreeFromFolder[0]
            
         self.treeWebView.page().mainFrame().evaluateJavaScript('zoomToLeaf("%s","%s", "%s");' % (item.dx,item.dy,item.pathId))
     
   def selectInTree(self):
      
      
      paths = []
      ids   = []
      print self.tipsByName
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
      
      self.zoomItem()
      
   @pyqtSlot(str)
   def addToLeavesforZoom(self,leavesJSON):
      
      leaves = json.loads(str(leavesJSON))
      self.selectedinTreeFromFolder = leaves.values()
   
   @pyqtSlot(str)
   def addtoFolders(self,leavesJSON):
      """
      @summary: coming from javascript, adds to folder view
      """
       
      leaves = json.loads(str(leavesJSON))
      #needs to clear folder view ??
      self.folderHint.combo.clear()
      self.folderHint.combo.clearEditText()
      self.callBack([FolderSpsSearchResult('', '', '','','')])
      
      inner = leaves.values()
      inner.sort(key=operator.itemgetter('name')) # sorts a list of dictionaries by a specific key
      
      items = []
      for d in inner:
         k = d["name"]
         if k in self.lookup:
            items.append(self.lookup[k])
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
         self.tipsByName[clade["name"]] = clade 
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
     
   def getPALayers(self,expId):
      
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
         self.lookup = d
      
if __name__ == "__main__":
#  


   from LmClient.lmClientLib import LMClient
   client =  LMClient()
   client.login(userId='Workshop', pwd='Workshop')
   
   expId = 1055
   epsg = 3410
   bucket = 1438
   treeJson = "/home/jcavner/WorkshopWS/AfricaMammals_1055/tree/tree.json"
   qApp = QApplication(sys.argv)
   d = PAMDialog(None,client=client,expId = expId,treeJSON=treeJson)
   
   d.show()
   sys.exit(qApp.exec_())