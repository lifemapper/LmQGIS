from lifemapperTools.common.lmListModel import LmListModel, EnterTextEventHandler
from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import * 
import random

class TreeSearchListModel(LmListModel):
   """
   @summary: subclass of LmListModel that overrides data
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
         if index.row() == 1 and self.model:
            return "build new model"
         else:
            return self.listData[index.row()].customData()
      if index.isValid() and role == Qt.UserRole:
         return self.listData[index.row()].id 
      else:
         return
      
class TreeSearchResult(object):
   """
   @summary: Data structure for species search results in the tree json
   """
   # .........................................
   def __init__(self, name, mtrxId, treeId, path):
      """
      @summary: Constructor for SpeciesSearchResult object
      
      """
      self.name = name
      self.mtrxId = mtrxId
      self.treeId = treeId
      self.path = path  
      
      # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the TreeSearchResult 
                   object
      """
      return "%s" % (self.name)
   
class MCPAInputs(object):
   
   def inputEdits(self,parent=None):
      self.parent = parent
      self.group = QGroupBox()
      self.group.setObjectName("group")
      self.style = QStyleFactory.create("motif") # try plastique too!
      self.group.setStyle(self.style)
      
      resWidget = QWidget()
      resWidget.setMaximumSize(250, 384)
      
      inputVBox = QVBoxLayout(resWidget)
      
      ####### Tree #######
      
      treeGroup = QGroupBox("Tree")
      treeGroup.setStyle(self.style)
      treeVBox = QVBoxLayout()
      
      radioHoriz = QHBoxLayout()
      self.newickRadio = QRadioButton('newwick')
      self.newickRadio.setChecked(True)
      self.newickRadio.toggled.connect(self.toggleTreeSearch)
      self.encodedTreeRadio = QRadioButton('encoded')
      radioHoriz.addWidget(self.newickRadio)
      radioHoriz.addWidget(self.encodedTreeRadio)
      treeGroup.setLayout(treeVBox)
      
      self.newickWidget = QWidget()
      #self.newickWidget.setMaximumHeight(32)
      treeHBox = QHBoxLayout(self.newickWidget)
      treeHBox.setMargin(0)
      treeVBox.addLayout(radioHoriz)
      #treeVBox.addLayout(treeHBox)
      treeVBox.addWidget(self.newickWidget)
      
      treeLabel = QLabel("Phylogenetic Tree")
      treeLabel.setMinimumHeight(23)
      treeButton = QPushButton("Browse")
      treeButton.setFocusPolicy(Qt.NoFocus)
      treeButton.setMaximumSize(69, 28)
      treeButton.setMinimumSize(69, 28)
      self.treeLine = QLineEdit()
      self.treeLine.setMaximumHeight(28)
      self.treeLine.setMaximumWidth(164)
      treeButton.clicked.connect(lambda: self.openFileDialog({'newick':['nhx','tre']},self.treeLine))
      treeHBox.addWidget(treeButton)
      treeHBox.addWidget(self.treeLine)
      
      self.searchTreeCombo = QComboBox()
      self.searchTreeCombo.setMaximumHeight(32)
      self.searchTreeCombo.setMaximumWidth(210)
      self.searchTreeCombo.hide()
      
      self.searchTreeCombo.setEditable(True)
      self.searchTreeCombo.setAutoCompletion(True)
      self.searchTreeCombo.textChanged.connect(self.onTextChange)
      
      treeVBox.addWidget(self.searchTreeCombo)
      #########################################
      
      
      # what about the inputs for shapefile based??
      # what about without a shpgrid and lyr shp based ??
      GrimHBox = QHBoxLayout()
      GrimLabel = QLabel("Environmental Mtx")
      GrimButton = QPushButton("Browse")
      GrimButton.setFocusPolicy(Qt.NoFocus)
      GrimButton.setMaximumSize(69, 28)
      GrimButton.setMinimumSize(69, 28)
      self.GrimLine = QLineEdit()
      self.GrimLine.setMaximumWidth(164)
      GrimButton.clicked.connect(lambda: self.openFileDialog({'numpy':['npy']},self.GrimLine))
      GrimHBox.addWidget(GrimButton)
      GrimHBox.addWidget(self.GrimLine)
      
      # what about the inputs for shapefile based??
      BioGeoHBox = QHBoxLayout()
      BioGeoLabel = QLabel("Biogeographical Inputs")
      BioGeoButton = QPushButton("Browse")
      BioGeoButton.setFocusPolicy(Qt.NoFocus)
      BioGeoButton.setMaximumSize(69, 28)
      BioGeoButton.setMinimumSize(69, 28)
      self.BioGeoLine = QLineEdit()
      self.BioGeoLine.setMaximumWidth(164)
      BioGeoButton.clicked.connect(lambda: self.openFileDialog({'shapefiles':['shp']},self.BioGeoLine,oneFile=False))
      BioGeoHBox.addWidget(BioGeoButton)
      BioGeoHBox.addWidget(self.BioGeoLine)
      
      ## PAM ??
      PAMHBox = QHBoxLayout()
      PAMLabel = QLabel("PAM")
      PAMButton = QPushButton("Browse")
      PAMButton.setFocusPolicy(Qt.NoFocus)
      PAMButton.setMaximumSize(69, 28)
      PAMButton.setMinimumSize(69, 28)
      self.PAMLine = QLineEdit()
      self.PAMLine.setMaximumWidth(164)
      PAMButton.clicked.connect(lambda: self.openFileDialog({'numpy':['npy']},self.PAMLine))
      PAMHBox.addWidget(PAMButton)
      PAMHBox.addWidget(self.PAMLine)
      
      
      
      ############
      inputVBox.addWidget(treeLabel)
      inputVBox.addWidget(treeGroup)
      inputVBox.addWidget(GrimLabel)
      inputVBox.addLayout(GrimHBox)
      inputVBox.addWidget(BioGeoLabel)
      inputVBox.addLayout(BioGeoHBox)
      inputVBox.addWidget(PAMLabel)
      inputVBox.addLayout(PAMHBox)
      
      #return inputVBox
      return resWidget
      
class MCPA_Controller(MCPAInputs):
   
   def openFileDialog(self,fileExtensions,setWidget,oneFile=True):
      """
      @summary: Shows a file selection dialog
      @param fileExtensions: dictionary, english name,list of extenstions
      """
      settings = QSettings()
      dirName = settings.value( "/UI/lastShapefileDir" )  ### have to take this out when in QGIS
      #filetypestr = "%s files (*.%s)" % ("newick", "nhx")
      extensions = ['*.%s' % (x) for x in fileExtensions[fileExtensions.keys()[0]]]
      filetypestr = "%s files (%s)" % (fileExtensions.keys()[0],' '.join(extensions)) 
      print filetypestr
      try:
         fileDialog = QgsEncodingFileDialog( self.parent, "Open File", dirName, filetypestr)
      except:
         fileDialog = QgsEncodingFileDialog( self.parent, "Open File", QString(), QString())
      #fileDialog.setDefaultSuffix(  "nhx"  )
      if oneFile:
         fileDialog.setFileMode( QFileDialog.AnyFile )
      else:
         fileDialog.setFileMode(QFileDialog.ExistingFiles) 
      fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
      #fileDialog.setConfirmOverwrite( True )
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      setWidget.setText(str(filename[0]))
   
   def toggleTreeSearch(self, button):
      
      
      if self.newickRadio.isChecked():
         self.searchTreeCombo.hide()
         self.newickWidget.show()
      if self.encodedTreeRadio.isChecked():
         self.setModels()
         self.newickWidget.hide()
         self.searchTreeCombo.show()

   # .......................................................................      
   def setModels(self):
      
      # ar 
      self.pilotList = []
      for x in range(0,33):
         self.pilotList.append({'name':'ace'+''.join(random.choice('0123456789ABCDEF') for i in range(4)),'path':''})
         self.pilotList.append({'name':'ara'+''.join(random.choice('0123456789ABCDEF') for i in range(4)),'path':''})
         self.pilotList.append({'name':'arab'+''.join(random.choice('0123456789ABCDEF') for i in range(4)),'path':''})
      print self.pilotList
      
      self.treeHintModel = TreeSearchListModel([])
      self.searchTreeCombo.setModel(self.treeHintModel)
      
   def searchJSON(self,text):
      
      matchingDicts =  [v for i,v in enumerate(self.pilotList) if v['name'].startswith(text)]
      if len(matchingDicts) > 0:
         self.searchItems = [TreeSearchResult(d['name'],'','',d["path"]) for d in matchingDicts]
      else:
         self.searchItems = [TreeSearchResult('','','','')]
      self.treeHintModel.updateList(self.searchItems)


   def getIdxFromSearchItems(self,currentText):
      
      idx = 0
      # sO search result Object
      for sH in self.searchItems:
         if sH.name == currentText:
            break
         idx += 1
      return idx 
   
   def onTextChange(self, text):
      """
      @summary: connected to combobox
      @param text: str from combobox
      """
      noChars = len(text)
      if text == '':
         self.searchTreeCombo.clear()
      if noChars >= 3:
         #if "_" in text or " " in text:
         currText = self.searchTreeCombo.currentText() # new on June 17 2015
         #currentIdx = self.searchTreeCombo.currentIndex()
         #if currentIdx == -1:
         idx = self.getIdxFromSearchItems(currText)
         self.searchTreeCombo.setCurrentIndex(idx)
         currentIdx = self.searchTreeCombo.currentIndex()
         try:
            self.path = self.treeHintModel.listData[currentIdx].path # might want the path here, instead
         except:
            pass
         else:
            return
      else:
         self.searchJSON(text)
      
   def checkPAM_Metadata(self, PAM):
      
      pass
      
      

      
      
      