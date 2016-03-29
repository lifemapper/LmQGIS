
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lifemapperTools.tools.radTable import *
from lifemapperTools.common.lmListModel import LmListModel
from lifemapperTools.common.lmHint import Hint, SpeciesSearchResult
from lifemapperTools.common.LmQTree import BrowserTreeModel, TreeItem



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
      
      MainLayout.addWidget(QTextEdit())
      MainLayout.addWidget(self.tabWidget)
   
   def setUpFolderHintService(self):
      """
      @summary: sets up the hint service and sets hint attribute
      combo can be added as a widget using self.hint.combo, callback
      adds extra functionality in addition to combo model
      """
      self.folderHint = PAMHint(self.client, callBack=self.callBack, setModel=False) #, serviceRoot=CURRENT_WEBSERVICES_ROOT
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
      self.folderModel = BrowserTreeModel(top='pam')
      self.folderTreeView.setModel(self.folderModel)
      self.folderTreeView.setObjectName("folderTreeView")
   
   def callBack(self, items):
      print "in call back"
      #"""
      #@summary: call back from hint class, where items are used to populate tree
      #@param items: list of hit items
      #"""
      #
      #if items[0].displayName == '':
      ##if len(items)  == 0:  # without SpeciesResult wrapper obj
      #   self.treeModel.beginRemoveRows(self.treeModel.index(0,0,QModelIndex()), 0, self.treeModel.provider.childCount()-1)
      #   self.treeModel.provider.childItems = []
      #   self.treeModel.endRemoveRows()
      #else:
      #   row = 0
      #   self.treeModel.provider.childItems = []
      #   for sps in items:
      #      
      #      nameFolder = TreeItem(sps.displayName,sps.displayName,self.treeModel.provider)
      #      occSetName = "occurrence set (%s points)" % sps.numPoints
      #      occSet     = TreeItem(sps.occurrenceSetId,occSetName,nameFolder,
      #                            type=ARCHIVE_DWL_TYPE.OCCURRENCE)
      #      try:
      #         for m in sps.models:
      #            mF = TreeItem(m.algorithmCode,m.algorithmCode,nameFolder)
      #            for p in m.projections:
      #               TreeItem(p.projectionId,p.projectionScenarioCode,mF,type=ARCHIVE_DWL_TYPE.PROJ)
      #      except:
      #         pass
      #      self.treeModel.insertRow(row, QModelIndex())      
      #      row = row + 1
      #      
      #               
      #   self.treeView.expand(self.treeModel.index(0,0,QModelIndex()))
   def setUpTable(self):
      
      self.tableData = [['start','','']]  
      self.table =  RADTable(self.tableData)
      header = ['1','2','3']
      return self.table.createTable(header)   

class PAMHint(Hint):

   def searchOccSets(self,searchText=''):
      """
      @summary: calls hint service
      @param    searchText: text to search for
      @todo:    needs a call back, probably set on init
      """
      print "here"
      # use toUnicode(searchText).encode('utf-8') for search
      #root = self.serviceRoot
      #try:
      #   #self.namedTuples = self.client.sdm.hint(toUnicode(searchText).encode('utf-8'),
      #   #                                        maxReturned=60,serviceRoot=root)   
      #   self.namedTuples = self.client.sdm.searchArchive(toUnicode(searchText).encode('utf-8'))    
      #except Exception, e:
      #   #print "or is throwing except ", e 
      #   pass
      #else:
      #   items = []
      #   if self.namedTuples is not None:
      #      if len(self.namedTuples) > 0:
      #         for species in self.namedTuples:
      #            
      #            items.append(SpeciesSearchResult(species.displayName,species.occurrenceSetId,
      #                                             numPoints=species.numPoints,models=species.models
      #                                             )) 
      #            # species.name,species.id, downloadUrl=species.downloadUrl, numModels=species.numModels
      #      else:  # added this Sept. 29
      #         items.append(SpeciesSearchResult('', '', '',''))
      #   else:  
      #      items.append(SpeciesSearchResult('', '', '',''))
      #      
      #   self.model.updateList(items) #uncomment when gong back to combo from lineEdit
      #   if self.callback is not None:
      #      self.callback(items)

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
                experimentname='',expId=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.client = client
      self.setupUi(experimentname=experimentname)
      
      #self.getPALayers(expId)
      
     
   

      
   def getPALayers(self,expId):
      
      try:
         palyrs = self.client.rad.getPALayers(expId)  
      except:
         self.palyrs = None
      else:
         self.palyrs = palyrs
      print dir(self.palyrs[0])
      
if __name__ == "__main__":
#  


   from LmClient.lmClientLib import LMClient
   client =  LMClient()
   client.login(userId='Workshop', pwd='Workshop')
   
   expId = 1055
   epsg = 3410
   bucket = 1438
   
   qApp = QApplication(sys.argv)
   d = PAMDialog(None,client=client,expId = expId)
   
   d.show()
   sys.exit(qApp.exec_())