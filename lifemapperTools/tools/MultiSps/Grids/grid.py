from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import * 

#QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem



class ConstructGrid(object):

   def bboxEdit(self):
      
      bboxWidget = QWidget()
      bboxWidget.setMaximumSize(250, 250)
      
      vBox = QVBoxLayout(bboxWidget)
      
      
      nlabel = QLabel("Max Y")
      self.northEdit = QLineEdit()
      self.northEdit.setMaximumHeight(25)
      
      
      slabel = QLabel("Min Y")
      self.southEdit = QLineEdit()
      self.southEdit.setMaximumHeight(25)
      
      
      wlabel = QLabel("Min X")
      self.westEdit = QLineEdit()
      self.westEdit.setMaximumHeight(25)
   
      elabel = QLabel("Max X")
      self.eastEdit = QLineEdit()
      self.eastEdit.setMaximumHeight(25)
      
      h1 = QHBoxLayout()
      h1.addItem(QSpacerItem(40, 10))
      h1.addWidget(nlabel,alignment=Qt.AlignHCenter)
      h1.addItem(QSpacerItem(40, 10))
      vBox.addLayout(h1)
      
      h2 = QHBoxLayout()
      h2.addItem(QSpacerItem(55, 10))
      h2.addWidget(self.northEdit)
      h2.addItem(QSpacerItem(55, 10))
      vBox.addLayout(h2)
      
      h3 = QHBoxLayout()
      h3.addItem(QSpacerItem(45, 10))
      h3.addWidget(wlabel)
      h3.addItem(QSpacerItem(55, 10))
      h3.addWidget(elabel)
      h3.addItem(QSpacerItem(45, 10))
      vBox.addLayout(h3)
      
      h4 = QHBoxLayout()
      h4.addWidget(self.westEdit)
      h4.addWidget(QWidget())
      h4.addWidget(self.eastEdit)
      vBox.addLayout(h4)
      
      h5 = QHBoxLayout()
      h5.addItem(QSpacerItem(40, 10))
      h5.addWidget(slabel,alignment=Qt.AlignHCenter)
      h5.addItem(QSpacerItem(40, 10))
      vBox.addLayout(h5)
      
      h6 = QHBoxLayout()
      h6.addItem(QSpacerItem(55, 10))
      h6.addWidget(self.southEdit)
      h6.addItem(QSpacerItem(55, 10))
      vBox.addLayout(h6)
      
      return bboxWidget
   
   def BBOX_Aux_Group(self):
      
      ShapeOrBBOX = QWidget()
      RadioVBox = QVBoxLayout(ShapeOrBBOX)
      self.useSelectedFeature = QRadioButton('Use selected feature')
      self.useSelectedFeature.setChecked(False)
      self.useSelectedFeature.setAutoExclusive(False)
      self.useSelectedFeature.clicked.connect(self.checkUseSelected)
      
      self.enterCoords = QRadioButton('Enter Coords')
      self.enterCoords.setChecked(True)
      self.enterCoords.setAutoExclusive(False)   
      self.enterCoords.clicked.connect(self.checkEnterCoords)
      
   def resolutionVBox(self):
      
      resWidget = QWidget()
      resWidget.setMaximumSize(250, 260)
      vBox = QVBoxLayout(resWidget)
      
      resolutionGroup = QGroupBox("Resolution")
      resolutionGroup.setMaximumSize(260, 310)
      resolutionGroup.setLayout(vBox)
      style = QStyleFactory.create("motif") # try plastique too!
      resolutionGroup.setStyle(style)
            
      self.shapelabel = QLabel("Cell Shape")
      self.shapeHorizBox = QHBoxLayout()
      self.hexCheck = QRadioButton('hexagonal')
      self.hexCheck.setChecked(True)
      self.shapeHorizBox.addWidget(self.hexCheck)
      self.squareCheck = QRadioButton('square')
      self.squareCheck.setChecked(False)
      self.shapeHorizBox.addWidget(self.squareCheck)
      #self.shapeHorizBox.addSpacing(189)   
      
      self.epsglabel = QLabel("EPSG Code")    # get auto filled
      self.epsgEdit = QLineEdit()
      self.epsgEdit.setMaximumWidth(238)  
      
      self.mapunitslabel = QLabel("Map Units")  # get auto filled
      self.selectUnits = QComboBox()
      self.selectUnits.setMaximumWidth(238)
      self.selectUnits.addItem("feet",
           '1')
      self.selectUnits.addItem("inches",
          'inches')
      self.selectUnits.addItem("kilometers",
           'kilometers')
      self.selectUnits.addItem("meters",
           '0')
      self.selectUnits.addItem("miles",
           'miles')
      self.selectUnits.addItem("nauticalmiles",
           'nauticalmiles')
      self.selectUnits.addItem("dd",
           '2')
      
      self.reslabel = QLabel("Cell Size in map units")
      self.resEdit = QLineEdit()
      self.resEdit.setMaximumWidth(238)
      
      self.namelabel = QLabel("Grid Name")
      self.nameEdit = QLineEdit()
      self.nameEdit.setMaximumWidth(238)
      
      vBox.addWidget(self.shapelabel)
      vBox.addLayout(self.shapeHorizBox)
      vBox.addWidget(self.epsglabel)
      vBox.addWidget(self.epsgEdit)
      vBox.addWidget(self.mapunitslabel)
      vBox.addWidget(self.selectUnits)
      vBox.addWidget(self.reslabel)
      vBox.addWidget(self.resEdit)
      vBox.addWidget(self.namelabel)
      vBox.addWidget(self.nameEdit)
      
      #return resWidget
      return resolutionGroup
      
      
   
class GridController(ConstructGrid):  #  will be able to inherit from multiple Ui classes
   
   def checkUseSelected(self):
      
      if self.useSelectedFeature.isChecked():         
         self.northEdit.clear()
         self.southEdit.clear()
         self.eastEdit.clear()
         self.westEdit.clear()
         self.northEdit.setEnabled(False)
         self.southEdit.setEnabled(False)
         self.eastEdit.setEnabled(False)
         self.westEdit.setEnabled(False)         
         self.enterCoords.setChecked(False)
         self.getFeatureWKT()         
      elif not self.useSelectedFeature.isChecked():
         self.useSelectedFeature.setChecked(True)
   
   def checkEnterCoords(self):
      if self.enterCoords.isChecked():
         self.northEdit.clear()
         self.southEdit.clear()
         self.eastEdit.clear()
         self.westEdit.clear()
         
         self.northEdit.setEnabled(True)
         self.southEdit.setEnabled(True)
         self.eastEdit.setEnabled(True)
         self.westEdit.setEnabled(True)
         
         self.northEdit.setFocus(Qt.OtherFocusReason)
         
         self.useSelectedFeature.setChecked(False)
         
         self.selectedFeatureWKT = None
      elif not self.enterCoords.isChecked():
         self.northEdit.setFocus(Qt.OtherFocusReason)
         self.enterCoords.setChecked(True)
   
   def _checkBoundingBox(self): 
      """ this was using a test float"""
      validBBox = True
      try:
         if float(self.northEdit.text()) < float(self.southEdit.text()):
            validBBox = False
         elif float(self.eastEdit.text()) < float(self.westEdit.text()):
            validBBox = False
      except:
         validBBox = False
         
      return validBBox
   
   
   def validate(self):
      
      """
      @summary: Validates the inputs for the dialog
      """
      valid = True
      message = ""
      self.keyvalues = {}
      if self.hexCheck.isChecked():
         self.keyvalues['cellShape'] = 'hexagon'
      elif self.squareCheck.isChecked():
         self.keyvalues['cellShape'] = 'square'          
      self.keyvalues['mapUnits'] = str(self.selectUnits.currentText())
      self.keyvalues['bbox'] = str(self.westEdit.text())+","+ \
                                str(self.southEdit.text())+","+\
                                str(self.eastEdit.text())+","+ \
                                str(self.northEdit.text())
      self.keyvalues['cellSize'] = str(self.resEdit.text())
      self.keyvalues['epsgCode'] = str(self.epsgEdit.text())
      self.keyvalues['shpName'] = str(self.nameEdit.text())      
        
      if self.selectedFeatureWKT is not None:
         self.keyvalues['cutout'] = self.selectedFeatureWKT         
      if len(self.northEdit.text()) <= 0 or not self._testFloat(self.northEdit.text()):
         message = "Please supply a max y"
         valid = False
      elif len(self.southEdit.text()) <= 0 or not self._testFloat(self.southEdit.text()):
         message = "Please supply a min y"
         valid = False 
      elif len(self.eastEdit.text()) <= 0 or not self._testFloat(self.eastEdit.text()):
         message = "Please supply a max x"
         valid = False
      elif len(self.westEdit.text()) <= 0 or not self._testFloat(self.westEdit.text()):
         message = "Please supply a min x"
         valid = False
      elif not self._checkBoundingBox():
         message = "bounding box is incorrect"
         valid = False
      elif len(self.resEdit.text()) <= 0:
         message = "Please supply a cell size"
         valid = False 
      elif len(self.epsgEdit.text()) <= 0:
         message = "Please supply an epsg code"
         valid = False
      elif len(self.nameEdit.text()) <= 0:
         message = "Please supply grid name"
         valid = False         
      
      if not valid:
         msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
      return valid 
   
   def getFeatureWKT(self):
      layer = self.iface.activeLayer()
      if layer:
         features = layer.selectedFeatures()
         if len(features) == 1:
            # check for just one feature ?
            g = features[0].geometry()
            bboxRect = g.boundingBox()
            minx = bboxRect.xMinimum()
            miny = bboxRect.yMinimum()
            maxx = bboxRect.xMaximum()
            maxy = bboxRect.yMaximum()
            # set bounding box inputs
            self.eastEdit.setText(str(maxx))
            self.westEdit.setText(str(minx))
            self.northEdit.setText(str(maxy))
            self.southEdit.setText(str(miny))
            Qwkt = g.exportToWkt()
            self.selectedFeatureWKT = str(Qwkt)
         else:
            self.northEdit.setEnabled(True)
            self.southEdit.setEnabled(True)
            self.eastEdit.setEnabled(True)
            self.westEdit.setEnabled(True)
   
            self.northEdit.clear()
            self.southEdit.clear()
            self.eastEdit.clear()
            self.westEdit.clear()
            
            self.northEdit.setFocus(Qt.OtherFocusReason)
            self.useSelectedFeature.setChecked(False)
            self.enterCoords.setChecked(True)
            self.selectedFeatureWKT = None           
            message = "Select one feature"
            msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
      else:
         self.northEdit.setEnabled(True)
         self.southEdit.setEnabled(True)
         self.eastEdit.setEnabled(True)
         self.westEdit.setEnabled(True)
   
         self.northEdit.clear()
         self.southEdit.clear()
         self.eastEdit.clear()
         self.westEdit.clear()
         
         self.northEdit.setFocus(Qt.OtherFocusReason)
         self.useSelectedFeature.setChecked(False)
         self.enterCoords.setChecked(True)
         self.selectedFeatureWKT = None
            
         #self.useSelectedFeature.setChecked(False)
         message = "There is no active layer"
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
       
       
# ..............................................................................
   
   
   

   
   