# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2014 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

@license: gpl2
@copyright: Copyright (C) 2014, University of Kansas Center for Research

          Lifemapper Project, lifemapper [at] ku [dot] edu, 
          Biodiversity Institute,
          1345 Jayhawk Boulevard, Lawrence, Kansas, 66045, USA
   
          This program is free software; you can redistribute it and/or modify 
          it under the terms of the GNU General Public License as published by 
          the Free Software Foundation; either version 2 of the License, or (at 
          your option) any later version.
  
          This program is distributed in the hope that it will be useful, but 
          WITHOUT ANY WARRANTY; without even the implied warranty of 
          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
          General Public License for more details.
  
          You should have received a copy of the GNU General Public License 
          along with this program; if not, write to the Free Software 
          Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
          02110-1301, USA.
"""
import os
import types
import zipfile
from random import randint
import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from lifemapperTools.tools.ui_spatialStatsDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.tools.radTable import RADTable
from lifemapperTools.common.pluginconstants import RADStatTypes
from lifemapperTools.common.colorpalette import ColorPalette
from lifemapperTools.common.workspace import Workspace




class SpatialStatsDialog(_Controller, QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None,parent=None, resume=False):
      
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.client = client
      
      self.setupUi()
      self.interface = iface   
      if resume:
         self.interface.addProject(resume)   
      self.workspace = Workspace(self.interface,self.client)
      self.inputs = inputs
      self.StatsDialog = None
      self.AddBut = None
      cc = self.rejectBut
      bok = self.getStatsBut
      _Controller.__init__(self, iface, BASE_URL=None, STATUS_URL=None, REST_URL=None,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, 
                           client = client)
      self.rampIndex = 0
      self.rampTypes = ['bluered','bluegreen','greenred']      
      self.populatePSCombo()
# .............................................................................         
   def populatePSCombo(self):
      items = self.getAllPams()
      if items:
         self.pamsCombo.addItem("please select pam",userData="pleaseselect")
         for o in items:
            self.pamsCombo.addItem(o.title+"_"+str(o.id),userData=o.id)
      else:
         self.pamsCombo.addItem("no pams", userData="error")
# .............................................................................      
   def getAllPams(self):
      
      # send for the original pam
      origPSargs = {'randomized':0}
      origPSargs.update(self.inputs)
      randomPSargs = {'randomized':1}
      randomPSargs.update(self.inputs)
      try:
         origitems = self.client.rad.listPamSums(**origPSargs)
         randomitems = self.client.rad.listPamSums(**randomPSargs)
      except:
         message = "There is a problem with the pam listing service"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
         return False
      else:
         pamlist = origitems + randomitems
         return pamlist

         

# .............................................................................
   def classify(self, layer, fieldName):
      """
      @summary: auto classification for pamsum layers in map canvas using both old 
      and new renderers
      """
      # new style renderer
      numberOfClasses = 5
      if self.rampIndex >= len(self.rampTypes):
            self.rampIndex = 0
      colorramp = ColorPalette(ptype=self.rampTypes[self.rampIndex],n=numberOfClasses-1)
      self.rampIndex += 1
      #if layer.isUsingRendererV2():         
      # Get the field index based on the field name
      fieldIndex = layer.fieldNameIndex(fieldName)
      provider = layer.dataProvider()
      minimum = float(provider.minimumValue( fieldIndex ))
      maximum = float(provider.maximumValue( fieldIndex ))
      ranges = []       
      for i in range(0,numberOfClasses):
         red = colorramp[i][1] 
         green = colorramp[i][2]
         blue = colorramp[i][3]      
         color = QColor(red,green,blue)
         
         symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
         symbol.setColor(color)
         lower = ('%.*f' % (2, minimum + ( maximum - minimum ) / numberOfClasses * i ) )
         upper = ('%.*f' % (2, minimum + ( maximum - minimum ) / numberOfClasses * ( i + 1 ) ) )
         label = "%s - %s" % (lower, upper)
         newrange = QgsRendererRangeV2(
                                    float(lower),
                                    float(upper),
                                    symbol,
                                    label)
         ranges.append(newrange)
      renderer = QgsGraduatedSymbolRendererV2('',ranges)
      renderer.setMode(
              QgsGraduatedSymbolRendererV2.EqualInterval)
      renderer.setClassAttribute(fieldName)
      
      layer.setRendererV2(renderer)
     
         
      return layer
# ..............................................................................

      
   def accept(self): 
      # needs to validate combo selection
      
      # get value from combo
      currentPamidx = self.pamsCombo.currentIndex()
      pamsumid = str(self.pamsCombo.itemData(currentPamidx, role=Qt.UserRole))
      if pamsumid == 'pleaseselect':
         message = "Please select a pam from the drop down list"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
      elif pamsumid == 'error':
         message = "no pams, error in retrieval"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
         #self.outEdit.clear()
      else:
         
         self.progressbar.setValue(0) 
         
         bucketid = self.inputs['bucketId']
         expid = self.inputs['expId']
         self.addtoCanvas(pamsumid, bucketid, expid)
         self.progressbar.hide()
         #self.outEdit.clear()
      
# ..............................................................................
   def addtoCanvas(self, pamsumid, bucketid, expid):
      if self.isModal():
         self.setModal(False)
      
      self.progressbar.show()
      if self.speciesrichness.isChecked():
         fieldName = 'specrich'
         tocName = 'Species Richness'
      elif self.meanproportionalrangesize.isChecked():
         fieldName =  'avgpropRaS'    
         tocName =  'Mean Proportional Range Size'                                 
      elif self.proportionalspeciesdiversity.isChecked():        
         fieldName =  'propspecDi'     
         tocName = 'Proportional Species Diversity'                      
      elif self.localityrangesize.isChecked():
         fieldName =  'RaSLoc'   
         tocName = 'Per-site Range Size of a Locality'          
      #success = self.client.rad.getPamSumShapegrid(str(self.outEdit.text()),
      #                                         expid, bucketid, pamsumid)
      expFolder = self.workspace.getExpFolder(expid)
      if not expFolder:
         expFolder = self.workspace.createProjectFolder(expid)
      zipName = str(pamsumid)
      pathname = os.path.join(expFolder,zipName)
   
      success = self.client.rad.getPamSumShapegrid(pathname,
                                               expid, bucketid, pamsumid)
      if success:
         self.progressbar.setValue(100)
         #pathname = self.outEdit.text()
         zippath = os.path.dirname(str(pathname))                         
         z = zipfile.ZipFile(str(pathname),'r')
         for name in z.namelist():
            f,e = os.path.splitext(name)
            if e == '.shp':
               shapename = name
            z.extract(name,str(zippath))
         vectorpath = os.path.join(zippath,shapename)
         vectorLayer = QgsVectorLayer(vectorpath,shapename.replace('.shp',''),'ogr')
         warningname = shapename         
         if not vectorLayer.isValid():
            QMessageBox.warning(self.outputGroup,"status: ",
              warningname)
         else: 
            lyrs = QgsMapLayerRegistry.instance().mapLayers()
            for id in lyrs.keys():
               if str(lyrs[id].name()) == shapename.replace('.shp',''):
                  QgsMapLayerRegistry.instance().removeMapLayer(id) 
            classedLayer = self.classify(vectorLayer, fieldName)
            classedLayer.setLayerName(tocName)               
            QgsMapLayerRegistry.instance().addMapLayer(classedLayer)
    
      else:
         message = "Could not retrieve the shapefile"
         msgBox = QMessageBox.information(self,
                                          "Problem...",
                                          message,
                                          QMessageBox.Ok)
               
      
      
# ..............................................................................         
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('spatialview')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()   
      
