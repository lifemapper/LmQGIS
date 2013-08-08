"""
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
import sys
import os.path
from collections import Counter, defaultdict
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.lmClientLib import LMClient
from lifemapperTools.tools.radTable import  RADTable, RADTableModel




class Ui_Dialog(object):
   
   def setupUi(self):
      self.setObjectName("Dialog")
      self.resize(700, 400)
      self.setMinimumSize(700,400)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
      
      self.gridLayout_input = QtGui.QGridLayout()
      self.gridLayout_input.setRowMinimumHeight(0,30)
      self.gridLayout_input.setRowMinimumHeight(1,350)
      self.gridLayout_input.setRowMinimumHeight(2,40)
      
      
         
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setAutoDefault(False)
      self.helpBut.setMaximumSize(30, 30)
      QtCore.QObject.connect(self.helpBut, QtCore.SIGNAL("clicked()"), self.help)
      self.acceptBut = QtGui.QPushButton("Ok", self)
      QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"),self.accept)
      self.rejectBut = QtGui.QPushButton("Close",self)
      self.rejectBut.setAutoDefault(False) 
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"),self.reject)
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)   
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole) 
     
      
      # for add widget, integers are fromrow,fromcolumn,rowspan,columnspan
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)

      self.gridLayout.addLayout(self.gridLayout_input,0,0,1,1)

class ListScenariosDialog(QtGui.QDialog, Ui_Dialog):   
   
   def __init__(self, items=None, client=None, layoutItem=None):
      QtGui.QDialog.__init__(self)
      self.client = client
      self.layoutItem = layoutItem
      self.setupUi()
      if items is not None:
         self.showTable(items)
      
   def showTable(self, items):
      self.data = []
      for o in items:
         try:
            title = o[0].title
         except:
            title = "someTitle"+str(o[0].id)
         self.data.append([title,int(o[0].id),o[1]])
      self.table =  RADTable(self.data)
      header = [' Title  ', '  ID  ','  Layer Type Code  ']
      self.tableview = self.table.createTable(header) 
      self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
      self.tableview.setSelectionMode(QAbstractItemView.SingleSelection)
      self.gridLayout_input.addWidget(self.tableview,1,0,1,1)
      
   def accept(self):
      selectedrowindex = self.table.tableView.selectionModel().currentIndex().row()
      if selectedrowindex == -1:
         QMessageBox.warning(self,"status: ",
                         "Please select one experiment")
         return 
      selectedrow = self.table.tableView.model().data[selectedrowindex]
      layerId = selectedrow[1]
      QgsProject.instance().emit(QtCore.SIGNAL("choseEnvLayer(PyQt_PyObject,PyQt_PyObject)" ),
                                          self.layoutItem, layerId) 
      self.close()
   
   def help(self):
      pass
      
       