# -*- coding: utf-8 -*-
"""
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
from PyQt4 import QtCore, QtGui
from lifemapperTools.tools.radTable import *
import os


class Ui_Dialog(object):
   
   def setupUi(self, experimentname=''):
      self.setObjectName("Dialog")
      self.resize(788, 725)
      self.setMinimumSize(588,560)
      self.setMaximumSize(1988,1600)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      
      ##########################################################################
      #    tables 
      ########################################################################## 
      self.data2 = [['','','','','','','','','']]
      self.table2 =  RADTable(self.data2) 
      header2 = ['  layer name                ', 'layerurl','Presence Attribute', 
                'Min Presence', 'Max Presence', '% Presence','Type','id','palayername']
      # added palayername for a shorter name, since author names in the 'layer name'
      # but didn't use it because you need to be able to rename, stashing it for now
      self.tableview2 = self.table2.createTable(header2,editsIndexList=[0,3,4,5],
                                              hiddencolumns=[1,6,7,8])
      self.tableview2.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableview2.setContextMenuPolicy(Qt.CustomContextMenu)
      self.tableview2.customContextMenuRequested.connect(self.setAllPopUp)
      ##########################################################################
      self.data1 = [['','','','','','','','','','','']]
      self.table1 =  RADTable(self.data1,totalCount=0)
      header1 = ['  layer name                ', 'id','preview', 'Algorithm', 
                'Scenario','Type','minVal','maxVal','noDataVal','resolution','notTitle']
      # added notTitle as a backup
      self.tableview1 = self.table1.createTable(header1,editsIndexList=[-999],
                                              hiddencolumns=[5,6,7,8,9,10],htmlIndexList=[2],
                                              controlsIndexList=[2])
      self.table1.pageForward.setEnabled(False)
      self.tableview1.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableview1.setContextMenuPolicy(Qt.CustomContextMenu)
      self.tableview1.customContextMenuRequested.connect(self.showInfoPopUp)
      
      #QObject.connect(self.tableview1, SIGNAL("clicked(const QModelIndex &)"), self.addWMS)
      #QObject.connect(self.tableview1.model(),SIGNAL("getMore(PyQt_PyObject,PyQt_PyObject)"),self.getNextPage)
      
      self.tableview1.clicked.connect(self.addWMS)
      self.tableview1.model().getNext.connect(self.getNextPage)

      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.inputGroup.setTitle("Search for Species")
      left,top,right,bottom = self.inputGroup.getContentsMargins()
      self.inputGroup.setContentsMargins(left, top, right, bottom+5)
      
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout.addLayout(self.gridLayout_input,0,0,1,1)
      self.gridLayout_input.setObjectName("gridLayout_input")
      
      self.gridLayout_input.setRowMinimumHeight(0,130)
      self.gridLayout_input.setRowMinimumHeight(1,40)
      self.gridLayout_input.setRowMinimumHeight(2,500)
      self.gridLayout_input.setRowMinimumHeight(3,50)
      self.gridLayout_input.setRowMinimumHeight(4,200)
      #self.gridLayout_input.setRowMinimumHeight(5,25)
      #self.gridLayout_input.setRowMinimumHeight(6,30)
      self.gridLayout_input.setRowMinimumHeight(5,30)
      
      self.queryHorizBoxLayout = QtGui.QGridLayout()
      self.queryHorizBoxLayout.setObjectName("queryHorizBoxLayout")
      
      
      #############  Search Controls and Labels ######################
      self.AlgorithmLabel = QtGui.QLabel("Algorithm Code for projection")
      self.AlgCodeCombo = QComboBox()                  
      self.publicRadio = QtGui.QRadioButton("Public") 
      self.publicRadio.setChecked(True) 
      #QtCore.QObject.connect(self.publicRadio, QtCore.SIGNAL("toggled(bool)"), self.checkPublic)
      self.publicRadio.toggled.connect(self.checkPublic)
      self.userRadio   = QtGui.QRadioButton("User") 
      #QtCore.QObject.connect(self.userRadio, QtCore.SIGNAL("toggled(bool)"), self.checkUser)
      self.userRadio.toggled.connect(self.checkUser)
      self.horizRadio  = QtGui.QHBoxLayout()
      self.horizRadio.addWidget(self.publicRadio)
      self.horizRadio.addWidget(self.userRadio)
           
      self.ScenarioLabel = QtGui.QLabel("Climate Scenario")    
      self.scenarioCombo = QComboBox() 
      self.searchLabel = QtGui.QLabel("Search layers by species name") 
      self.searchText = QtGui.QLineEdit()
      self.searchText.setObjectName('searchspecies')
      self.searchButton = QtGui.QPushButton(QtGui.QIcon("search.ico"), "Search")
      self.searchButton.setFocusPolicy(QtCore.Qt.NoFocus)
      #self.connect(self.searchButton, QtCore.SIGNAL("clicked()"), self.searchSpecies)
      self.searchButton.clicked.connect(self.searchSpecies)
      #########################################################################
      
      self.queryHorizBoxLayout.addLayout(self.horizRadio,    0,0,1,1)
      
      self.queryHorizBoxLayout.addWidget(self.AlgorithmLabel,1,0,1,1)
      self.queryHorizBoxLayout.addWidget(self.ScenarioLabel, 1,1,1,1)
      self.queryHorizBoxLayout.addWidget(self.searchLabel,   1,2,1,1)
      
      self.queryHorizBoxLayout.addWidget(self.AlgCodeCombo,  2,0,1,1)
      self.queryHorizBoxLayout.addWidget(self.scenarioCombo, 2,1,1,1)
      self.queryHorizBoxLayout.addWidget(self.searchText,    2,2,1,1)
      self.queryHorizBoxLayout.addWidget(self.searchButton,  2,3,1,1)
      
      
      self.inputGroup.setLayout(self.queryHorizBoxLayout)
      
      
      self.addSubtractLayout = QtGui.QGridLayout()
      self.addSubtractLayout.setColumnMinimumWidth(0,200)
      self.addSubtractLayout.setColumnMinimumWidth(1,100)
      self.addSubtractLayout.setColumnMinimumWidth(2,30)
      self.addSubtractLayout.setColumnMinimumWidth(3,30)
      self.addSubtractLayout.setColumnMinimumWidth(4,300)
      ##########################################################################
      #      Table labels
      self.searchResultTableLabel = QtGui.QLabel("Search Results (right click on result for more info)")
      self.layersToAddTableLabel = QtGui.QLabel("Layers to add to experiment")
      #self.layersToAddTableLabel.setMaximumWidth(167)
      self.gridLayout_input.addWidget(self.searchResultTableLabel,1,0,1,1)
      self.addSubtractLayout.addWidget(self.layersToAddTableLabel ,0,0,1,1)
      
      ##########################################################################
      #      Add and Remove Buttons 
      self.addButton = QtGui.QPushButton(QtGui.QIcon("search.ico"),"+")
      self.addButton.setMaximumSize(30, 30)
      self.addButton.setMinimumSize(30, 30)
      #self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.addLayersToUploadTable)
      self.addButton.clicked.connect(self.addLayersToUploadTable)
      
      self.removeButton = QtGui.QPushButton(QtGui.QIcon("search.ico"),"-")
      self.removeButton.setMaximumSize(30, 30)
      self.removeButton.setMinimumSize(30, 30)
      #self.connect(self.removeButton, QtCore.SIGNAL("clicked()"), self.removeSelectedLayersFromUploadTable)
      self.removeButton.clicked.connect(self.removeSelectedLayersFromUploadTable)
      ##########################################################################
      
      self.addSubtractLayout.addWidget(self.addButton,0,2,1,1,Qt.AlignCenter)
      self.addSubtractLayout.addWidget(self.removeButton,0,3,1,1,Qt.AlignCenter)
      
      
      addLabel = "Add to Experiment "+experimentname
      buttonLen = len(addLabel) * 10
      self.acceptBut = QtGui.QPushButton(addLabel)
      self.acceptBut.setMaximumSize(buttonLen, 30)
      self.acceptBut.setMinimumSize(buttonLen, 30)
      #self.acceptBut.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
      #self.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), 
      #                                                   self.accept)
      self.acceptBut.clicked.connect(self.accept)
      
      self.gridLayout_input.addWidget(self.inputGroup,0,0,1,1)
      self.gridLayout_input.addWidget(self.table1,2,0,1,1)
      self.gridLayout_input.addLayout(self.addSubtractLayout,3,0,1,1)
      self.gridLayout_input.addWidget(self.tableview2,4,0,1,1)
      self.gridLayout_input.addWidget(self.acceptBut,5,0,1,1,Qt.AlignCenter)
      
      
      
      # table labels
      self.searchTableLabel = QtGui.QLabel("Search Results")
      self.attributeTableLabel = QtGui.QLabel("Upload Table")
      
     
      self.outputGroup = QtGui.QGroupBox(self)
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout_output.setObjectName("gridLayout_input")
      self.gridLayout.addWidget(self.outputGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
       
      self.statuslabel = QtGui.QLabel(self.outputGroup)
      self.statuslabel.setObjectName('status')
      self.gridLayout_output.addWidget(self.statuslabel)
      #self.statuslabel.setText(QtGui.QApplication.translate("self", 
      #  'Running Process', None, QtGui.QApplication.UnicodeUTF8))
      
      self.progressbar = QtGui.QProgressBar(self.outputGroup)
      self.progressbar.setMinimum(0)
      self.progressbar.setMaximum(100)
      self.progressbar.setObjectName('progressbar')
      self.gridLayout_output.addWidget(self.progressbar)
       
      self.outputGroup.hide()
      ########################################################################## 
      
       
     
      self.rejectBut = QtGui.QPushButton("Close",self)    
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      #QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      self.helpBut.clicked.connect(self.help)
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)   
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
      
      # for add widget, integers are fromrow,fromcolumn,rowspan,columnspan
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
         
      self.retranslateUi()
      
      #QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      self.rejectBut.clicked.connect(self.reject)
      
   def setAllPopUp(self,pos):
      try:
         index = self.tableview2.indexAt(pos)
         value = index.model().data[index.row()][index.column()]
         menu = QMenu()
         setAllAction = menu.addAction('Set All in this column to "'+str(value)+'"')
         setSelected = menu.addAction('Set Selected in this column to "'+str(value)+'"')
         setEmpty = menu.addAction('Set empty cells in this column to "'+str(value)+'"')
         action = menu.exec_(QCursor.pos())
         if action == setAllAction:
            self.setAllInColumn(index)
         elif action == setSelected:
            self.setColumnsInSelectedRows(index)
         elif action == setEmpty:
            self.setEmptyInColumn(index)
      except:
         pass
   
   def setEmptyInColumn(self,index):
      
      column = index.column()
      if column in self.table2.tableModel.editIndexes:    
         value = index.model().data[index.row()][index.column()]
         for row, record in enumerate(self.table2.tableView.model().data):
            if record[column] == '':
               self.table2.tableView.model().setColumn(row, column, value)      
      else:
         QMessageBox.warning(self,"Tip: ",
        "This column is not editable")
   
   def setColumnsInSelectedRows(self,index):
      column = index.column()
      if column in self.table2.tableModel.editIndexes:    
         value = index.model().data[index.row()][index.column()]
         selectedrowidxs = self.table2.tableView.selectionModel().selectedRows()
         for idx in selectedrowidxs:
            row = idx.row()
            self.table2.tableView.model().setColumn(row, column, value)
         
      else:
         QMessageBox.warning(self,"Tip: ",
        "This column is not editable")
      
   def setAllInColumn(self, index):
      """
      @summary: sets a column value
      """ 
      column = index.column()
      if column in self.table2.tableModel.editIndexes:    
         value = index.model().data[index.row()][index.column()]          
         for row, record in enumerate(self.table2.tableView.model().data):
            self.table2.tableView.model().setColumn(row, column, value)
      else:
         QMessageBox.warning(self,"Tip: ",
        "This column is not editable")
         
         
   def removeSelectedLayersFromUploadTable(self):
      selectedrowidxs = self.table2.tableView.selectionModel().selectedRows()
      noTotalRows = len(self.table2.tableView.model().data)
      noSelectedRows = len(selectedrowidxs)
      if noSelectedRows == 0:
         
         QMessageBox.warning(self,"status: ",
                         "No layers selected from Upload table to remove") 
      else:
         if noTotalRows == noSelectedRows:
            emptyrow = ['' for x in range(0,len(self.table2.tableView.model().data[0]))]
            rowsToRemove = [r for r in self.table2.tableView.model().data] 
            for row in rowsToRemove:
               self.table2.tableView.model().removeRow(row)    
            self.table2.tableView.model().insertRow(0,emptyrow)
         else:
            rowsToRemove = [index.model().data[index.row()] for index in selectedrowidxs]
            for row in rowsToRemove:
               self.table2.tableView.model().removeRow(row)
            
   def addLayersToUploadTable(self):
      #table2
      selectedrowidxs = self.table1.tableView.selectionModel().selectedRows()
      if len(selectedrowidxs) == 0:
         
         QMessageBox.warning(self,"status: ",
                         "Please select at least one layer from search results. Have you done a search?")
      elif  len(selectedrowidxs) == 1 and selectedrowidxs[0].model().data[selectedrowidxs[0].row()][0] == '':
         QMessageBox.warning(self,"status: ",
                         "Have you done a search?")
      else:
         for x,index in enumerate(selectedrowidxs):
            # make a row here from the things we can get from the selected row
            layername = index.model().data[index.row()][0]
            # not using binomial with author name anymore, March 2015
            layerid = index.model().data[index.row()][1]
            layerurl = self.client.sdm.getProjectionUrl(layerid,frmt="tiff")
            layertype = index.model().data[index.row()][5]
            try:
               splL = layername.split(' ')
               palayername = "%s_%s_%s" % (splL[0],splL[1],splL[len(splL)-1])
               layername = palayername
            except:
               # get it from notTitle
               notTitle = index.model().data[index.row()][10]
               palayername = notTitle
               layername = notTitle
            # just stashing palayername in hidden column [8] for now 
            self.table2.tableView.model().insertRow(x,[layername, layerurl,"pixel",'','','',layertype,layerid,palayername])
            self.acceptBut.setEnabled(True)
         self.tableview2.resizeColumnsToContents()
         self.tableview2.horizontalHeader().setStretchLastSection(True)
      
   def addLayersToResultsTable(self,layers,userLayers=False):
      # table1
      self.table1.setNoPages(totalCount=self.projectionCount)
      self.table1.tableView.model().setNoPages(self.table1.noPages)
      readOut = "%s/%s" % (str(1),str(self.table1.noPages))
      self.table1.pageReadOut.setText(readOut)
      if not userLayers:
         for x, layer in enumerate(layers):
            try:
               layername = layer.title
            except:
               layername = layer.name
            else:
               # put notTitle (name) in hidden column [10], should be like prj_1233242
               try:
                  notTitle = layer.name
               except:
                  notTitle = "-999"
            layerid = layer.id
            Alg = layer.algorithmCode
            Scen = layer.scenarioCode
            try:
               minVal = layer.minVal
               maxVal = layer.maxVal
               noDataVal = layer.nodataVal
               resolution = layer.resolution
            except:
               minVal = 'no data'
               maxVal = 'no data'
               noDataVal = 'nodata'
               resolution = 'nodata'
            self.table1.tableView.model().insertRow(x,[layername, layerid,"<a href='nothing'>view</a>",Alg,Scen,'PUBLIC',minVal,maxVal,noDataVal,resolution,notTitle])
         self.tableview1.resizeColumnsToContents()
         self.tableview1.horizontalHeader().setStretchLastSection(True)
      else:
         for x, layer in enumerate(layers):
            try:
               layername = layer.title
            except:
               layername = layer.name
            layerid = layer.id
            Alg = layer.algorithmCode
            Scen = layer.scenarioCode
            try:
               minVal = layer.minVal
               maxVal = layer.maxVal
               noDataVal = layer.nodataVal
               resolution = layer.resolution
            except:
               minVal = 'no data'
               maxVal = 'no data'
               noDataVal = 'nodata'
               resolution = 'nodata'
            self.table1.tableView.model().insertRow(x,[layername, layerid,"<a href='nothing'>view</a>",Alg,Scen,'USER',minVal,maxVal,noDataVal,resolution])
      if self.tableview1.model().noPages == 1:
         self.table1.pageForward.setEnabled(False)
      elif self.tableview1.model().noPages > 1:
         self.table1.pageForward.setEnabled(True)
      self.tableview1.resizeColumnsToContents()
      self.tableview1.horizontalHeader().setStretchLastSection(True)
         
      
      
      

              
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Search for Lifemapper modeled Layers and Add to Experiment", None, QtGui.QApplication.UnicodeUTF8))
      
   
   