# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2011 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

@license: gpl2
@copyright: Copyright (C) 2013, University of Kansas Center for Research

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
import time
import types
import zipfile
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QUrl
from qgis.core import *
from lifemapperTools.tools.ui_uploadAncLayersDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GridConstructor
from lifemapperTools.common.pluginconstants import GENERIC_REQUEST


# .............................................................................

class UploadAncillDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """

# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      cc = self.rejectBut
      bok = self.acceptBut
      self.client = client
      self.inputs = inputs  
      _Controller.__init__(self, iface, BASE_URL=GridConstructor.BASE_URL, 
                           STATUS_URL=GridConstructor.STATUS_URL, 
                           REST_URL=GridConstructor.REST_URL,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, outputfunc=None, 
                           requestfunc=None, client=client )
      
# ..............................................................................       
   def accept(self):
     
      self.setAllGroup.hide()      
      #self.statuslabel.setText('Uploading') 
      self.outputGroup.setTitle('Outputs')
      self.outputGroup.show()
      successcount = 0
      layercount = len(self.table.tableView.model().data)
      for record in enumerate(self.table.tableView.model().data):
         self.progressbar.reset()  
         upload = False  
         try:
            f, extension = os.path.splitext(record[1][1])
            if extension == '.zip' or extension == '.shp':
               postresponse = self.client.rad.postVector(**{'filename':record[1][1],
                                                  'name':record[1][0]})
            if extension == '.tif':
               postresponse = self.client.rad.postRaster(**{'filename':record[1][1],
                                                  'name':record[1][0]})
         except:
            message = 'Could not upload layer '+str(record[1][0])
            QMessageBox.warning(self,"status: ", message)
         else:
            upload = True
         try:   
            inputs = {'attrValue':record[1][2],'calculateMethod':record[1][3],
                      'minPercent':record[1][4]}
            # this adds the expId
            inputs.update(self.inputs) 
            inputs.update({'lyrId':postresponse.id})
            #addAncLayer signature(self, expId, lyrId, attrValue=None, calculateMethod=None, 
            #       minPercent=None): 
            addresponse = self.client.rad.addAncLayer(**inputs)
            
         except:
            message = 'Could not add layer '+str(record[1][0]) +" to experiment"
            QMessageBox.warning(self,"status: ", message)
         else:
            if upload and addresponse:
               successcount += 1                         

            
         self.progressbar.setValue(100)
      self.acceptBut.setEnabled(False)
      message = 'Uploaded '+str(successcount) +" of "+ str(layercount) +" layers"
      QMessageBox.information(self,"status: ", message)
         
      
      
# ..............................................................................        
   def makeEditable(self, section):
      if 'id' not in self.table.tableModel.headerdata[section] and \
         section not in self.table.tableModel.controlIndexes:
         self.currentsection = section
         self.table.tableModel.editIndexes = [section]
         if section in self.table.comboIndices:
            self.ColumnSet.hide()
            self.ColumnCombo.show()
         else:
            self.ColumnCombo.hide()
            self.ColumnSet.show()
      else:
         self.table.tableModel.editIndexes = []     
      
      
# ..............................................................................         
   def help(self):
      self.help = QWidget()
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      #helpDialog.setSearchPaths(QStringList('documents'))
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('spatialStats')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()        
      
      
      
      
      
      
      
      