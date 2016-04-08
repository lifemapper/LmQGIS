#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2012 Hans-Peter Jansen <hpj@urpla.net>.
## Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
## Contact: Nokia Corporation (qt-info@nokia.com)
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:LGPL$
## GNU Lesser General Public License Usage
## This file may be used under the terms of the GNU Lesser General Public
## License version 2.1 as published by the Free Software Foundation and
## appearing in the file LICENSE.LGPL included in the packaging of this
## file. Please review the following information to ensure the GNU Lesser
## General Public License version 2.1 requirements will be met:
## http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
##
## In addition, as a special exception, Nokia gives you certain additional
## rights. These rights are described in the Nokia Qt LGPL Exception
## version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU General
## Public License version 3.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of this
## file. Please review the following information to ensure the GNU General
## Public License version 3.0 requirements will be met:
## http:#www.gnu.org/copyleft/gpl.html.
##
## Other Usage
## Alternatively, this file may be used in accordance with the terms and
## conditions contained in a signed written agreement between you and Nokia.
## $QT_END_LICENSE$
##
#############################################################################


from PyQt4.QtCore import QDate, QPoint, Qt, QStringList
from PyQt4.QtGui import QColor, QIcon, QKeySequence, QPainter, QPixmap
from PyQt4.QtGui import (QAction, QActionGroup, QApplication, QColorDialog,
        QComboBox, QDialog, QFontDialog, QGroupBox, QHBoxLayout, QLabel,
        QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableWidget,
        QTableWidgetItem, QToolBar, QVBoxLayout)
#from PyQt4.QtPrintSupport import QPrinter, QPrintPreviewDialog

def decode_pos(pos):
   try:
      row = int(pos[1:]) - 1
      col = ord(str(pos[0])) - ord('A')
   except ValueError:
      row = -1
      col = -1
   
   return row, col


def encode_pos(row, col):
   return chr(col + ord('A')) + str(row + 1)
 
from PyQt4 import QtCore

qt_resource_data = b"\
\x00\x00\x00\xae\
\x89\
\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\
\x00\x00\x10\x00\x00\x00\x10\x04\x03\x00\x00\x00\xed\xdd\xe2\x52\
\x00\x00\x00\x0f\x50\x4c\x54\x45\xc0\xc0\xc0\xc0\xc0\xc0\xc0\xc0\
\xc0\xff\xff\xff\x00\x00\x00\x63\x34\x8b\x60\x00\x00\x00\x03\x74\
\x52\x4e\x53\x00\x01\x02\x0d\x63\x94\xb3\x00\x00\x00\x4b\x49\x44\
\x41\x54\x78\x5e\x3d\x8a\xc1\x0d\xc0\x30\x0c\x02\x1d\x89\x01\xba\
\x8b\x3d\x40\x54\xb3\xff\x4c\x05\xa7\x0a\x0f\x74\xe6\x1c\x41\xf2\
\x89\x58\x81\xcc\x7c\x0d\x2d\xa8\x50\x06\x96\xc0\x6a\x63\x9f\xa9\
\xda\x12\xec\xd2\xa8\xa5\x40\x03\x5c\x56\x06\xfc\x6a\xfe\x47\x0d\
\xb8\x2e\x50\x39\xde\xf1\x65\xf8\x00\x49\xd8\x14\x02\x64\xfa\x65\
\x99\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82\
"

qt_resource_name = b"\
\x00\x06\
\x07\x03\x7d\xc3\
\x00\x69\
\x00\x6d\x00\x61\x00\x67\x00\x65\x00\x73\
\x00\x0d\
\x0f\x7f\xc5\x07\
\x00\x69\
\x00\x6e\x00\x74\x00\x65\x00\x72\x00\x76\x00\x69\x00\x65\x00\x77\x00\x2e\x00\x70\x00\x6e\x00\x67\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x12\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

def qInitResources():
   QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
   QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()






#import spreadsheet_rc

#from spreadsheetdelegate import SpreadSheetDelegate
#from spreadsheetitem import SpreadSheetItem
#from printview import PrintView
#from util import decode_pos, encode_pos

from PyQt4.QtCore import QDate, Qt
from PyQt4.QtGui import QCompleter, QDateTimeEdit, QItemDelegate, QLineEdit

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QTableWidgetItem

#from util import decode_pos


class SpreadSheetItem(QTableWidgetItem):

   def __init__(self, text=None):
      if text is not None:
         super(SpreadSheetItem, self).__init__(text)
      else:
         super(SpreadSheetItem, self).__init__()

      self.isResolving = False

   def clone(self):
      item = super(SpreadSheetItem, self).clone()
      item.isResolving = self.isResolving

      return item

   def formula(self):
      return super(SpreadSheetItem, self).data(Qt.DisplayRole)

   def data(self, role):
      if role in (Qt.EditRole, Qt.StatusTipRole):
         return self.formula()
      if role == Qt.DisplayRole:
         return self.display()
      t = str(self.display())
      try:
         number = int(t)
      except ValueError:
         number = None
      if role == Qt.TextColorRole:
         if number is None:
            return QColor(Qt.black)
         elif number < 0:
            return QColor(Qt.red)
         return QColor(Qt.blue)
   
      if role == Qt.TextAlignmentRole:
         if t and (t[0].isdigit() or t[0] == '-'):
            return Qt.AlignRight | Qt.AlignVCenter
      return super(SpreadSheetItem, self).data(role)

   def setData(self, role, value):
      super(SpreadSheetItem, self).setData(role, value)
      if self.tableWidget():
         self.tableWidget().viewport().update()

   def display(self):
      # avoid circular dependencies
      if self.isResolving:
         return None
      self.isResolving = True
      result = self.computeFormula(str(self.formula().toString()), self.tableWidget())
      self.isResolving = False
      return result

   def computeFormula(self, formula, widget):
      if formula is None:
         return None
      # check if the string is actually a formula or not
      slist = formula.split(' ')
      if not slist or not widget:
         # it is a normal string
         return formula
      op = slist[0].lower()
      firstRow = -1
      firstCol = -1
      secondRow = -1
      secondCol = -1
      if len(slist) > 1:
         firstRow, firstCol = decode_pos(slist[1])
      if len(slist) > 2:
         secondRow, secondCol = decode_pos(slist[2])
      start = widget.item(firstRow, firstCol)
      end = widget.item(secondRow, secondCol)
      firstVal = 0
      try:
         firstVal = start and int(start.text()) or 0
      except ValueError:
         pass
      secondVal = 0
      try:
         secondVal = end and int(end.text()) or 0
      except ValueError:
         pass
      result = None
      if op == "sum":
         sum_ = 0
         for r in range(firstRow, secondRow + 1):
            for c in range(firstCol, secondCol + 1):
               tableItem = widget.item(r, c)
               if tableItem and tableItem != self:
                  try:
                        sum_ += int(tableItem.text())
                  except ValueError:
                        pass
         result = sum_
      elif op == "+":
         result = (firstVal + secondVal)
      elif op == "-":
         result = (firstVal - secondVal)
      elif op == "*":
         result = (firstVal * secondVal)
      elif op == "/":
         if secondVal == 0:
            result = "nan"
         else:
            result = (firstVal / secondVal)
      elif op == "=":
         if start:
            result = start.text()
      else:
         result = formula
      return result



class SpreadSheetDelegate(QItemDelegate):

   def __init__(self, parent = None):
      super(SpreadSheetDelegate, self).__init__(parent)

   def createEditor(self, parent, styleOption, index):
      if index.column() == 1:
         editor = QDateTimeEdit(parent)
         editor.setDisplayFormat(self.parent().currentDateFormat)
         editor.setCalendarPopup(True)
         return editor

      editor = QLineEdit(parent)
      # create a completer with the strings in the column as model
      allStrings = []
      for i in range(1, index.model().rowCount()):
         strItem = index.model().data(index.sibling(i, index.column()), Qt.EditRole)
         if strItem not in allStrings:
            allStrings.append(strItem)
      aS = [str(x.toString()) for x in allStrings]
      autoComplete = QCompleter(QStringList(",".join(aS)))
      editor.setCompleter(autoComplete)
      editor.editingFinished.connect(self.commitAndCloseEditor)
      return editor

   def commitAndCloseEditor(self):
      editor = self.sender()
      self.commitData.emit(editor)
      self.closeEditor.emit(editor, QItemDelegate.NoHint)

   def setEditorData(self, editor, index):
      if isinstance(editor, QLineEdit):
         editor.setText(index.model().data(index, Qt.EditRole).toString())
      elif isinstance(editor, QDateTimeEdit):
         editor.setDate(QDate.fromString(
              index.model().data(index, Qt.EditRole), self.parent().currentDateFormat))

   def setModelData(self, editor, model, index):
      if isinstance(editor, QLineEdit):
         model.setData(index, editor.text())
      elif isinstance(editor, QDateTimeEdit):
         model.setData(index, editor.date().toString(self.parent().currentDateFormat))


class SpreadSheet(QMainWindow):

   dateFormats = ["dd/M/yyyy", "yyyy/M/dd", "dd.MM.yyyy"]

   currentDateFormat = dateFormats[0]

   def __init__(self, rows, cols, parent = None):
      super(SpreadSheet, self).__init__(parent)

      self.toolBar = QToolBar()
      self.addToolBar(self.toolBar)
      self.formulaInput = QLineEdit()
      self.cellLabel = QLabel(self.toolBar)
      self.cellLabel.setMinimumSize(80, 0)
      self.toolBar.addWidget(self.cellLabel)
      self.toolBar.addWidget(self.formulaInput)
      self.table = QTableWidget(rows, cols, self)
      for c in range(cols):
         character = chr(ord('A') + c)
         self.table.setHorizontalHeaderItem(c, QTableWidgetItem(character))

      self.table.setItemPrototype(self.table.item(rows - 1, cols - 1))
      self.table.setItemDelegate(SpreadSheetDelegate(self))
      self.createActions()
      self.updateColor(0)
      self.setupMenuBar()
      self.setupContents()
      self.setupContextMenu()
      self.setCentralWidget(self.table)
      self.statusBar()
      self.table.currentItemChanged.connect(self.updateStatus)
      self.table.currentItemChanged.connect(self.updateColor)
      self.table.currentItemChanged.connect(self.updateLineEdit)
      self.table.itemChanged.connect(self.updateStatus)
      self.formulaInput.returnPressed.connect(self.returnPressed)
      self.table.itemChanged.connect(self.updateLineEdit)
      self.setWindowTitle("Spreadsheet")

   def createActions(self):
      self.cell_sumAction = QAction("Sum", self)
      self.cell_sumAction.triggered.connect(self.actionSum)

      self.cell_addAction = QAction("&Add", self)
      self.cell_addAction.setShortcut(Qt.CTRL | Qt.Key_Plus)
      self.cell_addAction.triggered.connect(self.actionAdd)

      self.cell_subAction = QAction("&Subtract", self)
      self.cell_subAction.setShortcut(Qt.CTRL | Qt.Key_Minus)
      self.cell_subAction.triggered.connect(self.actionSubtract)

      self.cell_mulAction = QAction("&Multiply", self)
      self.cell_mulAction.setShortcut(Qt.CTRL | Qt.Key_multiply)
      self.cell_mulAction.triggered.connect(self.actionMultiply)

      self.cell_divAction = QAction("&Divide", self)
      self.cell_divAction.setShortcut(Qt.CTRL | Qt.Key_division)
      self.cell_divAction.triggered.connect(self.actionDivide)

      self.fontAction = QAction("Font...", self)
      self.fontAction.setShortcut(Qt.CTRL | Qt.Key_F)
      self.fontAction.triggered.connect(self.selectFont)

      self.colorAction = QAction(QIcon(QPixmap(16, 16)), "Background &Color...", self)
      self.colorAction.triggered.connect(self.selectColor)

      self.clearAction = QAction("Clear", self)
      self.clearAction.setShortcut(Qt.Key_Delete)
      self.clearAction.triggered.connect(self.clear)

      self.aboutSpreadSheet = QAction("About Spreadsheet", self)
      self.aboutSpreadSheet.triggered.connect(self.showAbout)

      self.exitAction = QAction("E&xit", self)
      self.exitAction.setShortcut(QKeySequence.Quit)
      self.exitAction.triggered.connect(QApplication.instance().quit)

      self.printAction = QAction("&Print", self)
      self.printAction.setShortcut(QKeySequence.Print)
      self.printAction.triggered.connect(self.print_)

      self.firstSeparator = QAction(self)
      self.firstSeparator.setSeparator(True)

      self.secondSeparator = QAction(self)
      self.secondSeparator.setSeparator(True)

   def setupMenuBar(self):
      self.fileMenu = self.menuBar().addMenu("&File")
      self.dateFormatMenu = self.fileMenu.addMenu("&Date format")
      self.dateFormatGroup = QActionGroup(self)
      for f in self.dateFormats:
         action = QAction(f, self, checkable=True,
                 triggered=self.changeDateFormat)
         self.dateFormatGroup.addAction(action)
         self.dateFormatMenu.addAction(action)
         if f == self.currentDateFormat:
            action.setChecked(True)
              
      self.fileMenu.addAction(self.printAction)
      self.fileMenu.addAction(self.exitAction)
      self.cellMenu = self.menuBar().addMenu("&Cell")
      self.cellMenu.addAction(self.cell_addAction)
      self.cellMenu.addAction(self.cell_subAction)
      self.cellMenu.addAction(self.cell_mulAction)
      self.cellMenu.addAction(self.cell_divAction)
      self.cellMenu.addAction(self.cell_sumAction)
      self.cellMenu.addSeparator()
      self.cellMenu.addAction(self.colorAction)
      self.cellMenu.addAction(self.fontAction)
      self.menuBar().addSeparator()
      self.aboutMenu = self.menuBar().addMenu("&Help")
      self.aboutMenu.addAction(self.aboutSpreadSheet)

   def changeDateFormat(self):
      action = self.sender()
      oldFormat = self.currentDateFormat
      newFormat = self.currentDateFormat = action.text()
      for row in range(self.table.rowCount()):
         item = self.table.item(row, 1)
         date = QDate.fromString(item.text(), oldFormat)
         item.setText(date.toString(newFormat))

   def updateStatus(self, item):
      if item and item == self.table.currentItem():
         self.statusBar().showMessage(item.data(Qt.StatusTipRole).toString(), 1000)
         self.cellLabel.setText("Cell: (%s)" % encode_pos(self.table.row(item),
                                                                    self.table.column(item)))

   def updateColor(self, item):
      pixmap = QPixmap(16, 16)
      color = QColor()
      if item:
         color = item.backgroundColor()
      if not color.isValid():
         color = self.palette().base().color()
      painter = QPainter(pixmap)
      painter.fillRect(0, 0, 16, 16, color)
      lighter = color.lighter()
      painter.setPen(lighter)
      # light frame
      painter.drawPolyline(QPoint(0, 15), QPoint(0, 0), QPoint(15, 0))
      painter.setPen(color.darker())
      # dark frame
      painter.drawPolyline(QPoint(1, 15), QPoint(15, 15), QPoint(15, 1))
      painter.end()
      self.colorAction.setIcon(QIcon(pixmap))

   def updateLineEdit(self, item):
      if item != self.table.currentItem():
         return
      if item:
         self.formulaInput.setText(item.data(Qt.EditRole).toString())
      else:
         self.formulaInput.clear()

   def returnPressed(self):
      text = self.formulaInput.text()
      row = self.table.currentRow()
      col = self.table.currentColumn()
      item = self.table.item(row, col)
      if not item:
         self.table.setItem(row, col, SpreadSheetItem(text))
      else:
         item.setData(Qt.EditRole, text)
      self.table.viewport().update()

   def selectColor(self):
      item = self.table.currentItem()
      color = item and QColor(item.background()) or self.table.palette().base().color()
      color = QColorDialog.getColor(color, self)
      if not color.isValid():
         return
      selected = self.table.selectedItems()
      if not selected:
         return
      for i in selected:
         i and i.setBackground(color)
      self.updateColor(self.table.currentItem())

   def selectFont(self):
      selected = self.table.selectedItems()
      if not selected:
         return
      font, ok = QFontDialog.getFont(self.font(), self)
      if not ok:
         return
      for i in selected:
         i and i.setFont(font)

   def runInputDialog(self, title, c1Text, c2Text, opText,
                      outText, cell1, cell2, outCell):
      rows = []
      cols = []
      for r in range(self.table.rowCount()):
         rows.append(str(r + 1))
      for c in range(self.table.columnCount()):
         cols.append(chr(ord('A') + c))
      addDialog = QDialog(self)
      addDialog.setWindowTitle(title)
      group = QGroupBox(title, addDialog)
      group.setMinimumSize(250, 100)
      cell1Label = QLabel(c1Text, group)
      cell1RowInput = QComboBox(group)
      c1Row, c1Col = decode_pos(cell1)
      cell1RowInput.addItems(rows)
      cell1RowInput.setCurrentIndex(c1Row)
      cell1ColInput = QComboBox(group)
      cell1ColInput.addItems(cols)
      cell1ColInput.setCurrentIndex(c1Col)
      operatorLabel = QLabel(opText, group)
      operatorLabel.setAlignment(Qt.AlignHCenter)
      cell2Label = QLabel(c2Text, group)
      cell2RowInput = QComboBox(group)
      c2Row, c2Col = decode_pos(cell2)
      cell2RowInput.addItems(rows)
      cell2RowInput.setCurrentIndex(c2Row)
      cell2ColInput = QComboBox(group)
      cell2ColInput.addItems(cols)
      cell2ColInput.setCurrentIndex(c2Col)
      equalsLabel = QLabel("=", group)
      equalsLabel.setAlignment(Qt.AlignHCenter)
      outLabel = QLabel(outText, group)
      outRowInput = QComboBox(group)
      outRow, outCol = decode_pos(outCell)
      outRowInput.addItems(rows)
      outRowInput.setCurrentIndex(outRow)
      outColInput = QComboBox(group)
      outColInput.addItems(cols)
      outColInput.setCurrentIndex(outCol)

      cancelButton = QPushButton("Cancel", addDialog)
      cancelButton.clicked.connect(addDialog.reject)
      okButton = QPushButton("OK", addDialog)
      okButton.setDefault(True)
      okButton.clicked.connect(addDialog.accept)
      buttonsLayout = QHBoxLayout()
      buttonsLayout.addStretch(1)
      buttonsLayout.addWidget(okButton)
      buttonsLayout.addSpacing(10)
      buttonsLayout.addWidget(cancelButton)

      dialogLayout = QVBoxLayout(addDialog)
      dialogLayout.addWidget(group)
      dialogLayout.addStretch(1)
      dialogLayout.addItem(buttonsLayout)

      cell1Layout = QHBoxLayout()
      cell1Layout.addWidget(cell1Label)
      cell1Layout.addSpacing(10)
      cell1Layout.addWidget(cell1ColInput)
      cell1Layout.addSpacing(10)
      cell1Layout.addWidget(cell1RowInput)

      cell2Layout = QHBoxLayout()
      cell2Layout.addWidget(cell2Label)
      cell2Layout.addSpacing(10)
      cell2Layout.addWidget(cell2ColInput)
      cell2Layout.addSpacing(10)
      cell2Layout.addWidget(cell2RowInput)
      outLayout = QHBoxLayout()
      outLayout.addWidget(outLabel)
      outLayout.addSpacing(10)
      outLayout.addWidget(outColInput)
      outLayout.addSpacing(10)
      outLayout.addWidget(outRowInput)
      vLayout = QVBoxLayout(group)
      vLayout.addItem(cell1Layout)
      vLayout.addWidget(operatorLabel)
      vLayout.addItem(cell2Layout)
      vLayout.addWidget(equalsLabel)
      vLayout.addStretch(1)
      vLayout.addItem(outLayout)
      if addDialog.exec_():
         cell1 = cell1ColInput.currentText() + cell1RowInput.currentText()
         cell2 = cell2ColInput.currentText() + cell2RowInput.currentText()
         outCell = outColInput.currentText() + outRowInput.currentText()
         return True, cell1, cell2, outCell

      return False, None, None, None

   def actionSum(self):
      row_first = 0
      row_last = 0
      row_cur = 0
      col_first = 0
      col_last = 0
      col_cur = 0
      selected = self.table.selectedItems()
      if selected:
         first = selected[0]
         last = selected[-1]
         row_first = self.table.row(first)
         row_last = self.table.row(last)
         col_first = self.table.column(first)
         col_last = self.table.column(last)

      current = self.table.currentItem()
      if current:
         row_cur = self.table.row(current)
         col_cur = self.table.column(current)

      cell1 = encode_pos(row_first, col_first)
      cell2 = encode_pos(row_last, col_last)
      out = encode_pos(row_cur, col_cur)
      ok, cell1, cell2, out = self.runInputDialog("Sum cells", "First cell:",
              "Last cell:", u"\N{GREEK CAPITAL LETTER SIGMA}", "Output to:",
              cell1, cell2, out)
      if ok:
         row, col = decode_pos(out)
         self.table.item(row, col).setText("sum %s %s" % (cell1, cell2))

   def actionMath_helper(self, title, op):
      cell1 = "C1"
      cell2 = "C2"
      out = "C3"
      current = self.table.currentItem()
      if current:
         out = encode_pos(self.table.currentRow(), self.table.currentColumn())
      ok, cell1, cell2, out = self.runInputDialog(title, "Cell 1", "Cell 2",
              op, "Output to:", cell1, cell2, out)
      if ok:
         row, col = decode_pos(out)
         self.table.item(row, col).setText("%s %s %s" % (op, cell1, cell2))

   def actionAdd(self):
      self.actionMath_helper("Addition", "+")

   def actionSubtract(self):
      self.actionMath_helper("Subtraction", "-")

   def actionMultiply(self):
      self.actionMath_helper("Multiplication", "*")

   def actionDivide(self):
      self.actionMath_helper("Division", "/")

   def clear(self):
      for i in self.table.selectedItems():
         i.setText("")

   def setupContextMenu(self):
      self.addAction(self.cell_addAction)
      self.addAction(self.cell_subAction)
      self.addAction(self.cell_mulAction)
      self.addAction(self.cell_divAction)
      self.addAction(self.cell_sumAction)
      self.addAction(self.firstSeparator)
      self.addAction(self.colorAction)
      self.addAction(self.fontAction)
      self.addAction(self.secondSeparator)
      self.addAction(self.clearAction)
      self.setContextMenuPolicy(Qt.ActionsContextMenu)

   def setupContents(self):
      titleBackground = QColor(Qt.lightGray)
      titleFont = self.table.font()
      titleFont.setBold(True)
      # column 0
      self.table.setItem(0, 0, SpreadSheetItem("Item"))
      self.table.item(0, 0).setBackground(titleBackground)
      self.table.item(0, 0).setToolTip("This column shows the purchased item/service")
      self.table.item(0, 0).setFont(titleFont)
      self.table.setItem(1, 0, SpreadSheetItem("AirportBus"))
      self.table.setItem(2, 0, SpreadSheetItem("Flight (Munich)"))
      self.table.setItem(3, 0, SpreadSheetItem("Lunch"))
      self.table.setItem(4, 0, SpreadSheetItem("Flight (LA)"))
      self.table.setItem(5, 0, SpreadSheetItem("Taxi"))
      self.table.setItem(6, 0, SpreadSheetItem("Dinner"))
      self.table.setItem(7, 0, SpreadSheetItem("Hotel"))
      self.table.setItem(8, 0, SpreadSheetItem("Flight (Oslo)"))
      self.table.setItem(9, 0, SpreadSheetItem("Total:"))
      self.table.item(9, 0).setFont(titleFont)
      self.table.item(9, 0).setBackground(Qt.lightGray)
      # column 1
      self.table.setItem(0, 1, SpreadSheetItem("Date"))
      self.table.item(0, 1).setBackground(titleBackground)
      self.table.item(0, 1).setToolTip("This column shows the purchase date, double click to change")
      self.table.item(0, 1).setFont(titleFont)
      self.table.setItem(1, 1, SpreadSheetItem("15/6/2006"))
      self.table.setItem(2, 1, SpreadSheetItem("15/6/2006"))
      self.table.setItem(3, 1, SpreadSheetItem("15/6/2006"))
      self.table.setItem(4, 1, SpreadSheetItem("21/5/2006"))
      self.table.setItem(5, 1, SpreadSheetItem("16/6/2006"))
      self.table.setItem(6, 1, SpreadSheetItem("16/6/2006"))
      self.table.setItem(7, 1, SpreadSheetItem("16/6/2006"))
      self.table.setItem(8, 1, SpreadSheetItem("18/6/2006"))
      self.table.setItem(9, 1, SpreadSheetItem())
      self.table.item(9, 1).setBackground(Qt.lightGray)
      # column 2
      self.table.setItem(0, 2, SpreadSheetItem("Price"))
      self.table.item(0, 2).setBackground(titleBackground)
      self.table.item(0, 2).setToolTip("This column shows the price of the purchase")
      self.table.item(0, 2).setFont(titleFont)
      self.table.setItem(1, 2, SpreadSheetItem("150"))
      self.table.setItem(2, 2, SpreadSheetItem("2350"))
      self.table.setItem(3, 2, SpreadSheetItem("-14"))
      self.table.setItem(4, 2, SpreadSheetItem("980"))
      self.table.setItem(5, 2, SpreadSheetItem("5"))
      self.table.setItem(6, 2, SpreadSheetItem("120"))
      self.table.setItem(7, 2, SpreadSheetItem("300"))
      self.table.setItem(8, 2, SpreadSheetItem("1240"))
      self.table.setItem(9, 2, SpreadSheetItem())
      self.table.item(9, 2).setBackground(Qt.lightGray)
      # column 3
      self.table.setItem(0, 3, SpreadSheetItem("Currency"))
      self.table.item(0, 3).setBackgroundColor(titleBackground)
      self.table.item(0, 3).setToolTip("This column shows the currency")
      self.table.item(0, 3).setFont(titleFont)
      self.table.setItem(1, 3, SpreadSheetItem("NOK"))
      self.table.setItem(2, 3, SpreadSheetItem("NOK"))
      self.table.setItem(3, 3, SpreadSheetItem("EUR"))
      self.table.setItem(4, 3, SpreadSheetItem("EUR"))
      self.table.setItem(5, 3, SpreadSheetItem("USD"))
      self.table.setItem(6, 3, SpreadSheetItem("USD"))
      self.table.setItem(7, 3, SpreadSheetItem("USD"))
      self.table.setItem(8, 3, SpreadSheetItem("USD"))
      self.table.setItem(9, 3, SpreadSheetItem())
      self.table.item(9,3).setBackground(Qt.lightGray)
      # column 4
      self.table.setItem(0, 4, SpreadSheetItem("Ex. Rate"))
      self.table.item(0, 4).setBackground(titleBackground)
      self.table.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
      self.table.item(0, 4).setFont(titleFont)
      self.table.setItem(1, 4, SpreadSheetItem("1"))
      self.table.setItem(2, 4, SpreadSheetItem("1"))
      self.table.setItem(3, 4, SpreadSheetItem("8"))
      self.table.setItem(4, 4, SpreadSheetItem("8"))
      self.table.setItem(5, 4, SpreadSheetItem("7"))
      self.table.setItem(6, 4, SpreadSheetItem("7"))
      self.table.setItem(7, 4, SpreadSheetItem("7"))
      self.table.setItem(8, 4, SpreadSheetItem("7"))
      self.table.setItem(9, 4, SpreadSheetItem())
      self.table.item(9,4).setBackground(Qt.lightGray)
      # column 5
      self.table.setItem(0, 5, SpreadSheetItem("NOK"))
      self.table.item(0, 5).setBackground(titleBackground)
      self.table.item(0, 5).setToolTip("This column shows the expenses in NOK")
      self.table.item(0, 5).setFont(titleFont)
      self.table.setItem(1, 5, SpreadSheetItem("* C2 E2"))
      self.table.setItem(2, 5, SpreadSheetItem("* C3 E3"))
      self.table.setItem(3, 5, SpreadSheetItem("* C4 E4"))
      self.table.setItem(4, 5, SpreadSheetItem("* C5 E5"))
      self.table.setItem(5, 5, SpreadSheetItem("* C6 E6"))
      self.table.setItem(6, 5, SpreadSheetItem("* C7 E7"))
      self.table.setItem(7, 5, SpreadSheetItem("* C8 E8"))
      self.table.setItem(8, 5, SpreadSheetItem("* C9 E9"))
      self.table.setItem(9, 5, SpreadSheetItem("sum F2 F9"))
      self.table.item(9,5).setBackground(Qt.lightGray)

   def showAbout(self):
      QMessageBox.about(self, "About Spreadsheet", """
          <HTML>
          <p><b>This demo shows use of <c>QTableWidget</c> with custom handling for
           individual cells.</b></p>
          <p>Using a customized table item we make it possible to have dynamic
           output in different cells. The content that is implemented for this
           particular demo is:
          <ul>
          <li>Adding two cells.</li>
          <li>Subtracting one cell from another.</li>
          <li>Multiplying two cells.</li>
          <li>Dividing one cell with another.</li>
          <li>Summing the contents of an arbitrary number of cells.</li>
          </HTML>
      """)

   def print_(self):
      pass
      #printer = QPrinter(QPrinter.ScreenResolution)
      #dlg = QPrintPreviewDialog(printer)
      #view = PrintView()
      #view.setModel(self.table.model())
      #dlg.paintRequested.connect(view.print_)
      #dlg.exec_()


if __name__ == '__main__':

   import sys

   app = QApplication(sys.argv)
   sheet = SpreadSheet(10, 6)
   #sheet.setWindowIcon(QIcon(QPixmap(":/images/interview.png")))
   sheet.resize(640, 420)
   sheet.show()
   sys.exit(app.exec_())

    
