from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import * 



class MCPAInputs(object):
   
   def inputEdits(self,parent=None):
      self.parent = parent
      self.group = QGroupBox()
      self.group.setObjectName("group")
      self.style = QStyleFactory.create("motif") # try plastique too!
      self.group.setStyle(self.style)
      
      resWidget = QWidget()
      resWidget.setMaximumSize(250, 300)
      
      inputVBox = QVBoxLayout(resWidget)
      
      treeHBox = QHBoxLayout()
      treeLabel = QLabel("Phylogenetic Tree")
      treeLabel.setMinimumHeight(23)
      treeButton = QPushButton("Browse")
      treeButton.setFocusPolicy(Qt.NoFocus)
      treeButton.setMaximumSize(69, 32)
      treeButton.setMinimumSize(69, 32)
      self.treeLine = QLineEdit()
      self.treeLine.setMaximumWidth(164)
      treeButton.clicked.connect(lambda: self.openFileDialog({'newick':['nhx','tre']},self.treeLine))
      treeHBox.addWidget(treeButton)
      treeHBox.addWidget(self.treeLine)
      
      # what about the inputs for shapefile based??
      # what about without a shpgrid and lyr shp based ??
      GrimHBox = QHBoxLayout()
      GrimLabel = QLabel("Environmental Mtx")
      GrimButton = QPushButton("Browse")
      GrimButton.setFocusPolicy(Qt.NoFocus)
      GrimButton.setMaximumSize(69, 32)
      GrimButton.setMinimumSize(69, 32)
      GrimLine = QLineEdit()
      GrimLine.setMaximumWidth(164)
      GrimButton.clicked.connect(lambda: self.openFileDialog({'numpy':['npy']},GrimLine))
      GrimHBox.addWidget(GrimButton)
      GrimHBox.addWidget(GrimLine)
      
      # what about the inputs for shapefile based??
      BioGeoHBox = QHBoxLayout()
      BioGeoLabel = QLabel("Biogeographical Mtx")
      BioGeoButton = QPushButton("Browse")
      BioGeoButton.setFocusPolicy(Qt.NoFocus)
      BioGeoButton.setMaximumSize(69, 32)
      BioGeoButton.setMinimumSize(69, 32)
      BioGeoLine = QLineEdit()
      BioGeoLine.setMaximumWidth(164)
      BioGeoButton.clicked.connect(lambda: self.openFileDialog({'numpy':['npy']},BioGeoLine))
      BioGeoHBox.addWidget(BioGeoButton)
      BioGeoHBox.addWidget(BioGeoLine)
      
      ## PAM ??
      
      inputVBox.addWidget(treeLabel)
      inputVBox.addLayout(treeHBox)
      inputVBox.addWidget(GrimLabel)
      inputVBox.addLayout(GrimHBox)
      inputVBox.addWidget(BioGeoLabel)
      inputVBox.addLayout(BioGeoHBox)
      
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
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
      #fileDialog.setConfirmOverwrite( True )
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      setWidget.setText(str(filename[0]))
      
      
   def checkPAM_Metadata(self, PAM):
      
      pass
      
      

      
      
      