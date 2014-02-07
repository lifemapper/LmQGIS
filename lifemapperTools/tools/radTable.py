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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.common.pluginconstants import PER_PAGE
import operator

#...............................................................................
#...............................................................................   
class RADTable(QtGui.QWidget): 
   
   def __init__(self, data, totalCount=None, *args):  
      QtGui.QWidget.__init__(self, *args) 
      self.tabledata = data
      self.noPages = None
      if totalCount is not None:
         self.totalCount = totalCount
         self.setNoPages() 
# ..............................................................................
   def setNoPages(self,totalCount=None):
      if totalCount is not None:
         self.totalCount = totalCount
      if self.totalCount <= PER_PAGE:
         self.noPages = 1
      elif self.totalCount%PER_PAGE:
         self.noPages = self.totalCount/PER_PAGE + 1
      else:
         self.noPages = self.totalCount/PER_PAGE
#...............................................................................     
   def createTable(self, header, editsIndexList=[],controlsIndexList=[],
                   hiddencolumns=[],spinBoxIndices=[],comboIndices=[],
                   htmlIndexList=[],fields=[],toolTips=[],container=None, minWidth=None):
      """
      @return: a QTableView, with the model set on it
      """
      self.comboIndices = comboIndices 
      if container is not None: 
         self.tableView = QtGui.QTableView(parent=container)
      else:
         self.tableView = QtGui.QTableView()
      
      self.pageSize = PER_PAGE   
      self.viewToolLayout = QtGui.QVBoxLayout()
      self.setLayout(self.viewToolLayout)
      self.viewToolLayout.addWidget(self.tableView)
      
      self.tableModel = RADTableModel(self.tabledata, header, editsIndexList, 
                                      controlsIndexList, fields=fields, parent=self,
                                      noPages=self.noPages,toolTips=toolTips)
      self.tableView.setModel(self.tableModel)
      self.createToolBar()
      if len(editsIndexList) > 0:
         self.tableView.setItemDelegate(RADDelegate(self.tableView,
                                                    spinBoxIndices=spinBoxIndices,
                                                    comboIndices=comboIndices,
                                                    controlIndexes=controlsIndexList,
                                                    htmlIndices=htmlIndexList))
      self.hiddenColumns = hiddencolumns
      
      self.tableView.resizeColumnsToContents()
      self.tableView.horizontalHeader().setStretchLastSection(True)
      #self.tableView.sortByColumn(int)
      if self.noPages is None:
         self.tableView.setSortingEnabled(True)
      for x in hiddencolumns:
         self.tableView.hideColumn(x)
      return self.tableView
   

   def createToolBar(self):
      #self.tableView.
      self.toolBar = QtGui.QHBoxLayout()
      self.pageForward = QtGui.QPushButton(">")
      self.pageForward.setMaximumWidth(30)
      self.pageForward.clicked.connect(lambda: self.tableModel.canGetMore(True))
      self.pageReadOut = QtGui.QLabel("1/%s" % (str(self.noPages)))
      self.pageReadOut.setMaximumWidth(50)
      self.pageBack = QtGui.QPushButton("<")
      self.pageBack.setMaximumWidth(30)
      self.pageBack.setEnabled(False)
      self.pageBack.clicked.connect(lambda: self.tableModel.canGetMore(False))
      self.toolBar.addSpacing(200)
      self.toolBar.addWidget(self.pageBack)
      self.toolBar.addWidget(self.pageReadOut)
      self.toolBar.addWidget(self.pageForward)
      self.toolBar.addSpacing(200)
      self.viewToolLayout.addLayout(self.toolBar)
      #self.layout().addLayout(self.toolBar)
      
   
   
   
   def resizeTable(self, minWidth=None):
      rowcount = self.tableModel.rowCount(None)
      vertical = self.tableView.verticalHeader()
      height = 0
      for i in range(0,rowcount):
         height += vertical.sectionSize(i)
      
      columncount = self.tableModel.columnCount(None)     
      horizontal = self.tableView.horizontalHeader()      
      width = 0
      for i in range(0,columncount):
         if i not in self.hiddenColumns:   
            width += horizontal.sectionSize(i)
      if minWidth is not None:
         if width <= (minWidth - 180):
            self.tableView.setMaximumSize(width, 300)
         else:
            maxWidth = minWidth-180
            self.tableView.setMaximumSize(maxWidth, 300)
      else:
         self.tableView.setMaximumSize(width, 300)
         

# ..............................................................................
# PADDelegate and RADTableView classes aren't being used right now, but we 
# may need them if we want to edit items in the table for specific datatypes, say
# like a combobox radio button or checkbox
# ..............................................................................        
class RADDelegate(QStyledItemDelegate):
   
   def __init__(self, owner, itemslist=[],comboIndices=[],spinBoxIndices=[],
                controlIndexes=[],htmlIndices=[]):
      #QtGui.QItemDelegate.__init__(self, owner)
      super(RADDelegate, self).__init__(owner)
      self.itemslist = itemslist
      self.spinBoxIndices = spinBoxIndices
      self.comboIndices = comboIndices
      self.controlIndices = controlIndexes
      self.htmlIndices = htmlIndices
      
      
   def paint(self, painter, option, index):
      if index.column()in self.htmlIndices:
         text = index.model().data[index.row()][index.column()]
         palette = QApplication.palette()
         document = QTextDocument()
         document.setDefaultFont(option.font)           
         document.setHtml(text)
         painter.save()
         painter.translate(option.rect.x(), option.rect.y())
         document.drawContents(painter)
         painter.restore()
     
      else:
         QStyledItemDelegate.paint(self, painter, option, index)


   def sizeHint(self, option, index):
      
      return QStyledItemDelegate.sizeHint(self, option, index)
   
   def _getRowPositionInModelgivenSkips(self,index, skips):
      rowIdx = index.row()
      position = rowIdx - sum(map(lambda x: x < rowIdx, skips))  
      return position
   
   def createEditor(self, parent, option, index):
      if index.column() in self.spinBoxIndices:
         spinbox = QSpinBox(parent)
         spinbox.setRange(0, 200000)
         spinbox.setSingleStep(1000)
         spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
         return spinbox
      elif (index.column() in self.comboIndices) and \
      (index.row() not in index.model().skipComboinRow) :
         combobox = QComboBox(parent)
         if len(index.model().fields) > 0:
            if isinstance(index.model().fields[0],list):
               rowPosition = self._getRowPositionInModelgivenSkips(index,index.model().skipComboinRow)
               #combobox.addItems(sorted(index.model().fields[index.row()]))
               combobox.addItems(sorted(index.model().fields[rowPosition]))
            else:
               combobox.addItems(sorted(index.model().fields))
         combobox.setEditable(True)
         return combobox
      elif index.row() in index.model().skipComboinRow and index.column() in self.comboIndices:
         return 
      elif index.column() not in self.controlIndices:
         editor = QLineEdit(parent)
         return editor
        
   def addFromSender(self): 
      pass 
   
   def setEditorData(self, editor, index):
      if index.column() in self.spinBoxIndices:
         value = index.data(QtCore.Qt.DisplayRole)
         editor.setValue(value)
      elif (index.column() in self.comboIndices) \
      and (index.row() not in index.model().skipComboinRow):
         
         value = str(index.data(QtCore.Qt.DisplayRole))
         i = editor.findText(value)
         if i == -1:
            i = 0
         editor.setCurrentIndex(i)
      else:
         # this is for QlineEdits, i.e. QLineText
         #value = index.model().data[index.column()][index.row()]
         value = str(index.data(QtCore.Qt.DisplayRole))
         editor.setText(value)

   
   def setModelData(self,editor,model,index):
      try:
         value = editor.value()
      except:
         pass
      try:
         value = editor.currentText()
      except:
         pass
      try:
         value = editor.text()
      except:
         pass
      model.setData(index, value)
   
   def updateEditorGeometry(self, editor, option, index):
      editor.setGeometry(option.rect)


##...............................................................................
#class RADTableView(QtGui.QTableView):
#   
#   
#   def __init__(self, parent=None):
#
#         QtGui.QTableView.__init__(self, parent)
#         self.setItemDelegateForColumn(2,RADDelegate(self, self.checkValues)) 
#...............................................................................   
class RADTableModel(QAbstractTableModel): 
   
   getNext = pyqtSignal(int, bool)
   
   def __init__(self, datain, headerdata, edits, controls, fields=[], parent=None,
                noPages=None,toolTips=[], *args):
      #self.table = parent
      QAbstractTableModel.__init__(self, parent, *args)
      self.fields = fields
      self.editIndexes = edits
      self.controlIndexes = controls 
      self.data = datain
      self.toolTips = toolTips
      self.headerdata = headerdata
      self.skipComboinRow = []
      self.currentPage = 0
      self.noPages = noPages
      
   def setNoPages(self,noPages):
      self.noPages = noPages   
   
   def setCurrentPage(self,pageNo):
      self.currentPage = pageNo
      
# ..............................................................................
   def canGetMore(self,forward):
      if forward:
         if self.currentPage < self.noPages - 1:
            self.getMore(forward)
      else:
         if self.currentPage > 0:
            self.getMore(forward)
            
# ..............................................................................   
   def getMore(self,forward):
      #self.emit( SIGNAL( "getMore(PyQt_PyObject,PyQt_PyObject)" ), self.currentPage, forward)
      self.getNext.emit(self.currentPage,forward)

#...............................................................................      
   def rowCount(self, parent):
      return len(self.data)
#...............................................................................
   def columnCount(self, parent): 
      return len(self.data[0]) 
#...............................................................................   
   def data(self, index, role):
      
      if not index.isValid() or \
         not(0 <= index.row() < len(self.data)): 
         return  
      elif role != Qt.DisplayRole and index.column() not in self.controlIndexes:
         if role == Qt.BackgroundRole:
            if index.column() in self.editIndexes:
               return QColor(204,255,255)
         elif role == Qt.ToolTipRole and index.column() in self.toolTips:
            return self.data[index.row()][index.column()] 
         else:
            return 
      elif role == Qt.CheckStateRole:
         
         return self.data[index.row()][index.column()]
       
      
         
      return self.data[index.row()][index.column()]
#...............................................................................

   
   def removeRow(self,record):
      index = self.data.index(record)
      self.beginRemoveRows(QModelIndex(),index,index)
      self.data.remove(record)
      self.endRemoveRows()
      self.dataChanged.emit(QModelIndex(), QModelIndex())
      return True
      
   def insertRow(self, index, record):
      """
      @summary: inserts a row into the table data
      """
      startidx = len(self.data)
      if startidx == 1 and self.data[0][0] == '':
         self.data[0] = record
         self.dataChanged.emit(QModelIndex(), QModelIndex())
      else:        
         self.beginInsertRows(QModelIndex(),startidx,startidx)
         self.data.append(record)
         self.endInsertRows()
      return True
   
         
   def setColumn(self,row,column, value): 
      self.data[row][column] = value 
      self.dataChanged.emit(QModelIndex(), QModelIndex()) 
        
   def insertRows(self,records):
      self.data[0] = records.pop(0)
      NoRows = len(records)
      self.beginInsertRows(QModelIndex(),0,NoRows-1)     
      for record in records:
         self.data.append(record)
      self.endInsertRows()
      
      
      return True
      #
      
#...............................................................................   
   def setData(self, index, value, role=Qt.EditRole):
      """
      @summary: sets an individual item (cell) in the table data
      """
      try:
         self.data[index.row()][index.column()] = str(value)
      except:
         self.data[index.row()][index.column()] = str(value)
      self.dataChanged.emit(index,index)
      return True
#...............................................................................      
   def flags(self, index):   
      if index.column() in self.editIndexes and index.column() not in self.controlIndexes:     
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable  
      elif index.column() in self.controlIndexes:
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable   
        
      return QtCore.QAbstractTableModel.flags(self, index)
#...............................................................................   
   def headerData(self, col, orientation, role):
      if orientation == Qt.Horizontal and role == Qt.DisplayRole:
         return self.headerdata[col]
      return 
#...............................................................................   
   def sort(self, Ncol, order):
      """Sort table by given column number. This had to be reimplemented
      to allow setSortingEnabled on the view
      """
      try:
         self.layoutAboutToBeChanged.emit()
         self.data = sorted(self.data, key=operator.itemgetter(Ncol))        
         if order == Qt.DescendingOrder:
            self.data.reverse()
         self.layoutChanged.emit()
      except:
         pass