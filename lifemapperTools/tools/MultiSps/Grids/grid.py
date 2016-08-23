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
   
   def resolutionGroup(self):
      
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
      
      pass
   
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
   
   
   

   
   