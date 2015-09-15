# -*- coding: utf-8 -*-
"""
@author: Jeff Cavner
@contact: jcavner@ku.edu

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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from lifemapperTools.tools.ui_listPALayersDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import ListExperiments
from lifemapperTools.tools.uploadLayers import UploadDialog
from lifemapperTools.tools.radTable import RADTable






class ListPALayersDialog(_Controller,QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, epsg=None,
                mapunits=None,resume=False):
      
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      self.interface = iface
      self.client = client
      if resume:
         self.interface.addProject(resume)
      cc = self.rejectBut
      bok = self.intersectBut
      self.inputs = inputs
      
      _Controller.__init__(self, iface, BASE_URL=ListExperiments.BASE_URL, 
                           STATUS_URL=ListExperiments.STATUS_URL, 
                           REST_URL=ListExperiments.REST_URL,
                           cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=True,outputfunc=self.showTable,
                           requestfunc=self.client.rad.getPALayers, inputs=inputs,
                           client=client)
      # this may need to list layers outside of the controller also
      self.expEPSG = epsg
      self.mapunits = mapunits
# ...........................................................................       
   def intersectPAM(self):
      
      self.close()
      inputs = {}
      QMessageBox.warning(self,"status: ",
        str(self.table.tableView.model().data))
# ...........................................................................       
   def setParams(self):
      update = 0
      layercount = len(self.table.tableView.model().data) 
      for record in enumerate(self.table.tableView.model().data):
         try:   
            inputs = {'attrPresence':record[1][3],'minPresence':record[1][4],
                      'maxPresence':record[1][5], 'percentPresence':record[1][6]}
            # this adds the expId
            inputs.update(self.inputs) 
            inputs.update({'lyrId':record[1][1]}) 
            addresponse = self.client.rad.addPALayer(**inputs)
         except:
            message = 'Could not add layer '+str(record[1][0]) +" to experiment"
            QMessageBox.warning(self,"status: ", message)
         else:
            if addresponse:
               update += 1
      message = 'Updated '+str(update) +" of "+ str(layercount) +" layers"
      QMessageBox.information(self,"status: ", message)
      
      
# ...........................................................................   
   def cleanInputGridLayout(self):
      
      """@summary:  cleans out the input grid layout"""
     
      if not(self.gridLayout_input.isEmpty()):
         for childindex in range(0,self.gridLayout_input.count()):
            item = self.gridLayout_input.takeAt(0)
            if not(type(item) is types.NoneType):
               item.widget().deleteLater()
              
         self.gridLayout_input.update()  
# ...........................................................................
   def getCount(self):
      try:
         pass
      except:
         pass
# ...........................................................................        
   
         
   def showTable(self, items, model):
      
      try:
         if len(items) == 0:
            raise Exception,"No Layers"
         
         data = [[o.name,o.id, o.attrPresence,
                  o.minPresence,o.maxPresence,o.percentPresence] for o in items]         
         self.table =  RADTable(data)         
         headerList = ['Layer title', 'Lyr id', 'Attr Presence','min Presence','max Presence',
                       'Percent Presence']
         self.tableview = self.table.createTable(headerList,editsIndexList=[999])
         self.holderGroup.hide()     
         self.gridLayout.addWidget(self.tableview,1,1,1,1) 
         header = self.tableview.horizontalHeader()
         
         self.ColumnSet.setEnabled(False)
         self.setAllColumnButton.setEnabled(False) 
         self.setParamsBut.setEnabled(False)
      except Exception, e:
         
         self.loadTabelLabel.setText("No layers to view")
         self.addLayersBut = QPushButton("Add Layers",self)
         self.buttonBox.addButton(self.addLayersBut, QDialogButtonBox.ActionRole)
         #QObject.connect(self.addLayersBut, SIGNAL("clicked()"), self.openAddLayers)
         self.addLayersBut.clicked.connect(self.openAddLayers)
         message = "There are no presence absence layers for this experiment"
         msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
# ........................................................................... 
   def openAddLayers(self): 
      self.close()
      d =  UploadDialog( self.iface, inputs = self.inputs,
                               client = self.client, epsg=self.expEPSG,
                               mapunits=self.mapunits ) 
      d.exec_()
# ...........................................................................      
   def makeEditable(self, section):
      if 'id' not in self.table.tableModel.headerdata[section] and \
         section not in self.table.tableModel.controlIndexes:
         self.currentsection = section
         self.table.tableModel.editIndexes = [section]
      else:
         self.table.tableModel.editIndexes = []  
   
# ...........................................................................       
   def addWMS(self,index):

         
      if index.column() in self.table.tableModel.controlIndexes:
         
         message = "This functionality will be available in a later release"
         msgBox = QMessageBox.information(self,
                                                   "Info...",
                                                   message,
                                                   QMessageBox.Ok)
         return

# ...........................................................................       
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('listPALayers')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
             

      
      
