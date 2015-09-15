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
from LmCommon.common.lmconstants import OutputFormat # OutputFormat.GTIFF, OutputFormat.SHAPE 
import os


class Ui_Dialog(object):
   
   def setupUi(self, experimentname=''):
      
      self.hasOGR = True
      try:
         from osgeo import ogr
      except:
         self.hasOGR = False
         comboIndices = []
      else:
         comboIndices = [2]
      
      
      self.setObjectName("Dialog")
      self.resize(848, 610)
      self.setMinimumSize(848,610)
      self.setMaximumSize(1788,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      self.gridLayout.setRowMinimumHeight(0,90) 
      self.gridLayout.setRowMinimumHeight(1,90)
      self.gridLayout.setRowMinimumHeight(2,300)
      self.gridLayout.setRowMinimumHeight(3,70)
      
      self.data = [['','start','','','','','']]
      self.table =  RADTable(self.data) 
      header = ['  layer name      ', 'filepath', 'Presence Attribute', 
                'Minimum Presence', 'Maximum Presence', 'Percent Presence (1-100)     ','unique']
      self.tableview = self.table.createTable(header,editsIndexList=[2,3,4,5],
                                              hiddencolumns=[1,6],comboIndices=comboIndices)
      self.tableview.setSortingEnabled(False)
      self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableview.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
      self.tableview.setContextMenuPolicy(Qt.CustomContextMenu)
      self.tableview.customContextMenuRequested.connect(self.setAllPopUp)
     
      self.inputGroup = QtGui.QGroupBox()
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
         
      self.inputLayout = QtGui.QGridLayout()
      self.inputLayout.setObjectName("inputLayout")
      
        
      
      self.iFileLabel = QtGui.QLabel("Add Layers")
      self.iFileLabel.setMaximumSize(120, 32)
      self.fileButton = QtGui.QPushButton("Browse")
      self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
      self.fileButton.setMaximumSize(69, 32)
      self.fileButton.setMinimumSize(69, 32)
      self.fileButton.clicked.connect(self.showFileDialog)
      
      
      self.removeRecordsBut = QtGui.QPushButton("Remove")
      self.removeRecordsBut.setMaximumSize(69, 32)
      self.removeRecordsBut.setMinimumSize(69, 32)
      self.removeRecordsDirectionsLabel = QtGui.QLabel("Remove selected layers")
      self.removeRecordsBut.clicked.connect(self.removeRecords)
      
      self.inputLayout.addWidget(self.fileButton,                  0,0,1,1)
      self.inputLayout.addWidget(self.iFileLabel,                  0,1,1,1)
      self.inputLayout.addWidget(self.removeRecordsBut,            0,2,1,1)
      self.inputLayout.addWidget(self.removeRecordsDirectionsLabel,0,3,1,1)
      self.inputGroup.setLayout(self.inputLayout)
      self.inputGroup.setEnabled(False) 
      
      # for add widget, integers are fromrow,fromcolumn,rowspan,columnspan
      self.gridLayout.addWidget(self.inputGroup,1,0,1,1)
      self.gridLayout.addWidget(self.tableview,2,0,1,1)
      
      addLabel = "Add to Experiment "+experimentname
      buttonLen = len(addLabel) * 10
      self.acceptBut = QtGui.QPushButton(addLabel)
      self.acceptBut.setDefault(True)
      self.acceptBut.setMaximumSize(buttonLen, 30)
      self.acceptBut.setMinimumSize(buttonLen, 30)
      self.acceptBut.clicked.connect(self.accept)
      
      self.acceptLayout =  QtGui.QHBoxLayout() 
      self.acceptLayout.setAlignment(Qt.AlignCenter) 
      self.acceptLayout.addWidget(self.acceptBut)
      self.gridLayout.addLayout(self.acceptLayout,3,0,1,1)
      
      
      #############  Tree #########################
      
      
      ############   tree Group ###############
      self.treeGroup = QtGui.QGroupBox()
      self.treeGroup.setObjectName("treeGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.treeGroup.setStyle(self.style)
      
      
      
      ######### tab and pages ###################
      self.treeGroup = QtGui.QTabWidget()
      self.localPage = QWidget()
      self.treeGroup.addTab(self.localPage,"local")
      self.OTLPage = QWidget()
      self.treeGroup.addTab(self.OTLPage,"Open Tree of Life")
      ##########################################
      
      #self.treeLayout = QtGui.QGridLayout()
      
      #self.treeWidget = QtGui.QWidget()
      #self.treeWidget.setMinimumHeight(120)
      #self.treeLayout.addWidget(self.treeWidget)
      
      
      ########## open tree tab/layout ############
      
      self.OTLLayout = QtGui.QGridLayout()
      self.OTLLayout.setRowMinimumHeight(0,10)
      self.OTLLayout.setRowMinimumHeight(1,40)
      self.OTLLayout.setRowMinimumHeight(2,5)
      self.OTLLayout.setColumnMinimumWidth(0,120)
      self.OTLLayout.setColumnMinimumWidth(1,60)
      self.OTLLayout.setColumnMinimumWidth(2,60)
      
      self.getOTLTreeBut = QtGui.QPushButton("Get Tree")
      self.getOTLTreeBut.clicked.connect(self.getOTLTree)
      
      self.convertOTLTreeBut = QtGui.QPushButton("Convert")
      self.convertOTLTreeBut.clicked.connect(self.convertOTLNewick)
      self.convertOTLTreeBut.setEnabled(False)
      
      #### need some connects ########
      
      self.searchAuto = QtGui.QComboBox()
      self.searchAuto.setEditable(True)
      self.searchAuto.setAutoCompletion(True)
      self.searchAuto.textChanged.connect(self.onTextChange)
      
      self.OTLLayout.addWidget(QWidget(),0,0,1,1)
      self.OTLLayout.addWidget(self.searchAuto,1,0,1,1)
      self.OTLLayout.addWidget(self.getOTLTreeBut,1,1,1,1)
      self.OTLLayout.addWidget(self.convertOTLTreeBut,1,2,1,1)
      
      self.OTLPage.setLayout(self.OTLLayout)
      
      ############## local layout ##########
      self.treeLayout = QtGui.QGridLayout()
      self.treeLayout.setRowMinimumHeight(0,10)
      self.treeLayout.setRowMinimumHeight(1,40)
      self.treeLayout.setRowMinimumHeight(0,5)
      self.treeLayout.setColumnMinimumWidth(0,50)
      self.treeLayout.setColumnMinimumWidth(1,160)
      self.treeLayout.setColumnMinimumWidth(2,50)
      
      self.treeButton = QtGui.QPushButton("Browse")
      self.treeButton.setFocusPolicy(QtCore.Qt.NoFocus)
      self.treeButton.setMaximumSize(69, 32)
      self.treeButton.setMinimumSize(69, 32)
      self.treeButton.clicked.connect(self.showTreeFileDialog)
      
      self.convertButton = QtGui.QPushButton("Convert")
      self.convertButton.setMaximumSize(129, 32)
      self.convertButton.setMinimumSize(129, 32)
      self.convertButton.clicked.connect(self.convertNewick)
      
      self.treeLine = QtGui.QLineEdit()
      self.treeLine.setMinimumWidth(80)
      
      self.treeLayout.addWidget(QWidget(),0,0,1,1)
      self.treeLayout.addWidget(self.treeButton,1,0,1,1)
      self.treeLayout.addWidget(self.treeLine,1,1,1,1)
      self.treeLayout.addWidget(self.convertButton,1,2,1,1)
      
      #self.treeGroup.setLayout(self.treeLayout)
      self.localPage.setLayout(self.treeLayout)
      
      self.gridLayout.addWidget(self.treeGroup,0,0,1,1)
      
      
      ##############END TREE  ###############
       
      self.outputGroup = QtGui.QGroupBox(self)
      self.outputGroup.setObjectName("outputGroup")
      self.style2 = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.outputGroup.setStyle(self.style2)
      self.gridLayout_output = QtGui.QGridLayout(self.outputGroup)
      self.gridLayout_output.setObjectName("gridLayout_input")
      self.gridLayout.addWidget(self.outputGroup, 3,0,1,1)
      
       
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
       
      #self.acceptBut = QtGui.QPushButton("OK",self)
      #self.acceptBut.setEnabled(False)
      self.rejectBut = QtGui.QPushButton("Close",self)
      
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      
      self.helpBut.clicked.connect(self.help)
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.RejectRole)
      
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
         
      self.retranslateUi()
      
      self.rejectBut.clicked.connect(self.reject)
      
       
     
   
   def removeRecords(self):
      
      selectedrowidxs = self.table.tableView.selectionModel().selectedRows()
      noTotalRows = len(self.table.tableView.model().data)
      noSelectedRows = len(selectedrowidxs)
      if noSelectedRows == 0:
         
         QMessageBox.warning(self,"status: ",
                         "No layers selected from Upload table to remove") 
      else:
         if noTotalRows == noSelectedRows:
            emptyrow = ['' for x in range(0,len(self.table.tableView.model().data[0]))]
            emptyrow[1] = 'start'
            rowsToRemove = [r for r in self.table.tableView.model().data] 
            for row in rowsToRemove:
               self.table.tableView.model().removeRow(row)    
            self.table.tableView.model().insertRow(0,emptyrow)
            self.acceptBut.setEnabled(False)
            self.table.tableView.model().fields = []
            self.table.tableView.model().skipComboinRow = []
            self.tableview.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
         else:
            rowsToRemove = [index.model().data[index.row()] for index in selectedrowidxs]
            skips = self.table.tableView.model().skipComboinRow
            removeskips = []
            removeshpsRowIdxs = []
            fieldpositions = []
            for row,idx in zip(rowsToRemove,selectedrowidxs):
               self.table.tableView.model().removeRow(row)
               if idx.row() in skips:
                  removeskips.append(idx.row())
               else:
                  removeshpsRowIdxs.append(idx.row())
                  position = idx.row() - sum(map(lambda x: x < idx.row(), skips))
                  fieldpositions.append(position)
            removeskips_reversed = sorted(removeskips,reverse=True)
            skipscopy = list(skips)
            skipscopyShape = [x for x in skipscopy if x not in removeskips]
            if len(removeskips) > 0:
               for x in removeskips_reversed:
                  rmIdx = skipscopy.index(x)
                  skipscopy[rmIdx:] = [y-1 for y in skipscopy if y > skipscopy[rmIdx]]  
            if len(removeshpsRowIdxs) > 0: 
               subtracts = map(lambda y: map(lambda x: y < x, skipscopyShape),removeshpsRowIdxs)
               allSubtracts = map(sum,zip(*subtracts))
               allRasterSkips = map(operator.sub,skipscopy,allSubtracts)
            else:
               allRasterSkips = skipscopy
            
                  
            fields = self.table.tableView.model().fields
            newfields = [field for idx,field in enumerate(fields) if idx not in fieldpositions]
            self.table.tableView.model().fields = newfields
            self.table.tableView.model().skipComboinRow = allRasterSkips 
     
      
   # ................................................   
   def setAllPopUp(self,pos):
      """
      @summary: context menu with right click
      """
      try:
         index = self.tableview.indexAt(pos)
         if index.column() != 0:
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
         elif index.column() == 0:
            menu = QMenu()
            pathAction = menu.addAction('Find lyr for this species, deactivated')
            action = menu.exec_(QCursor.pos())
            self.setLyrPath(index)
            
      except:
         pass
   # ................................................       
   def checkForRaster(self,idx):
      if idx.model().data[idx.row()][idx.column()] == 'pixel':
         return True
      else:
         return False
      
   def checkForField(self, idx, value):
      skips = self.table.tableView.model().skipComboinRow
      position = idx.row() - sum(map(lambda x: x < idx.row(), skips))
      fields = self.table.tableView.model().fields[position]
      if value in fields:
         return True
      else:
         return False
       
   
   def setEmptyInColumn(self,index):
      """
      @summary: sets empty rows in column index to value in clicked cell
      """
      column = index.column()
      if column in self.table.tableModel.editIndexes:    
         value = index.model().data[index.row()][index.column()]
         for row, record in enumerate(self.table.tableView.model().data):
            if record[column] == '':
               self.table.tableView.model().setColumn(row, column, value)      
      else:
         QMessageBox.warning(self,"Tip: ",
        "This column is not editable")
   
   def setColumnsInSelectedRows(self,index):
      column = index.column()
      if column in self.table.tableModel.editIndexes:    
         value = index.model().data[index.row()][index.column()]
         selectedrowidxs = self.table.tableView.selectionModel().selectedRows()
         for idx in selectedrowidxs:
            if column in self.table.comboIndices:
               pixel = self.checkForRaster(idx)
               dataFieldExists = self.checkForField(idx, value)
            else:
               pixel = False
               dataFieldExists = True
            if not(pixel) and dataFieldExists:
               row = idx.row()
               self.table.tableView.model().setColumn(row, column, value)
         
      else:
         QMessageBox.warning(self,"Tip: ",
        "This column is not editable")
      
   def setAllInColumn(self, index):
      """
      @summary: sets a column value
      """ 
      column = index.column()
      if column in self.table.tableModel.editIndexes:    
         value = index.model().data[index.row()][index.column()]          
         for row, record in enumerate(self.table.tableView.model().data):
            if column in self.table.comboIndices:
               idx =  self.table.tableView.model().index(row,column)
               pixel = self.checkForRaster(idx)
               dataFieldExists = self.checkForField(idx, value)
            else:
               pixel = False
               dataFieldExists = True
            if not(pixel) and dataFieldExists:
               self.table.tableView.model().setColumn(row, column, value)
      else:
         QMessageBox.warning(self,"Tip: ",
        "This column is not editable")
         
            

      # .........................................
   def showFileDialog(self):
      """
      @summary: Shows a file selection dialog
      """
      settings = QtCore.QSettings()
      dirName = str(settings.value( "/UI/lastShapefileDir" ))
      folderName = QtGui.QFileDialog.getExistingDirectory(self, 
                                                     "Directory",
                                                     dirName,
                                                     QtGui.QFileDialog.ShowDirsOnly |
                                                     QtGui.QFileDialog.DontUseNativeDialog)
      if not(folderName == ''):
         self.processFolder(str(folderName))
      else:
         message = "please choose a directory with your species layers"
         msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)

   def addFiles(self,filenames):
      """
      @summary: adds records to the table's view
      """
      self.tableview.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.EditKeyPressed)
      shpList = [file for file in filenames if os.path.splitext(str(file))[1] == OutputFormat.SHAPE]
      fields = self.getFields(shpList) 
      if self.table.tableView.model().data[0][1] == 'start':
         lengthOfExistingData = 0
         self.table.tableView.model().fields = fields
      else:
         lengthOfExistingData =  len(self.table.tableView.model().data)
         lengthOfExistingFields = len(self.table.tableView.model().fields)
         map(lambda field: self.table.tableView.model().fields.append(field),fields)
      for x, file in enumerate(filenames):
         layername = os.path.basename(os.path.splitext(str(file))[0])
         if os.path.splitext(str(file))[1] == OutputFormat.GTIFF:
            self.table.tableView.model().insertRow(x,[layername,str(file),'pixel','','','',lengthOfExistingData+x])
            if lengthOfExistingData > 0:
               index = self.table.tableView.model().index(x+lengthOfExistingData,2)
               index.model().skipComboinRow.append(index.row())
            else:
               index = self.table.tableView.model().index(x,2)
               index.model().skipComboinRow.append(x)
            
         else:
            shpIdx = 0
            self.table.tableView.model().insertRow(x,[layername,str(file),'','','','',lengthOfExistingData+x])
            if self.hasOGR:
               # this branch sets the data for the combo boxes in the table's model data
               if lengthOfExistingData > 0:
                  comboindex = self.table.tableView.model().index(x+lengthOfExistingData,2)
                  self.table.tableView.model().setData(comboindex,
                                                       self.table.tableView.model().fields[lengthOfExistingFields + shpIdx][0]) 
               else: 
                  comboindex = self.table.tableView.model().index(x,2)
                  self.table.tableView.model().setData(comboindex,self.table.tableView.model().fields[shpIdx][0]) 
            else: # this probably needs to change for existing data
               index = self.table.tableView.model().index(x,2)  
               index.model().skipComboinRow.append(x)
            shpIdx += 1     
      self.tableview.resizeColumnsToContents()     
      #self.tableview.horizontalHeader().setStretchLastSection(True)
      self.acceptBut.setEnabled(True)
      
      
      
      

              
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Upload presence/absence layers", None, QtGui.QApplication.UnicodeUTF8))
      
   
   