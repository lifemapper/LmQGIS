# -*- coding: utf-8 -*-
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
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.tools.radTable import RADTable
import operator



class Ui_Dialog(object):
   
   def setupUi(self, diversityheader, allpamsumids):
      self.setObjectName("Dialog")
      self.resize(990, 780)
      self.setMinimumSize(990,780)
      self.setMaximumSize(1940,1780)
      self.setSizeGripEnabled(True)
       
       
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      
      #self.inputGroup = QtGui.QGroupBox(self)
      #self.inputGroup.setObjectName("inputGroup")
      #self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      #self.inputGroup.setStyle(self.style)
      
      self.tableGroup = QtGui.QGroupBox(self)
      self.tableGroup.setObjectName("tableGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.tableGroup.setStyle(self.style)
      
      
      self.sitesLabel = QtGui.QLabel(self.tableGroup)
      self.sitesLabel.setText('Sites')
      self.sitesLabel.setGeometry(QtCore.QRect(10, 10, 60, 15))
      
      self.exportsites = QtGui.QLabel(self.tableGroup)
      self.exportsites.setText('<a href="sites">export sites table</a>')
      QtCore.QObject.connect(self.exportsites, QtCore.SIGNAL("linkActivated(QString)"), self.export)
      self.exportsites.setGeometry(QtCore.QRect(90,8,150,20))
      
      self.speciesLabel = QtGui.QLabel(self.tableGroup)
      self.speciesLabel.setText('Species')
      self.speciesLabel.setGeometry(QtCore.QRect(500, 10, 60, 15))
      
      self.exportSpecies = QtGui.QLabel(self.tableGroup)
      self.exportSpecies.setText('<a href="species">export species table</a>')
      QtCore.QObject.connect(self.exportSpecies, QtCore.SIGNAL("linkActivated(QString)"), self.export)
      self.exportSpecies.setGeometry(QtCore.QRect(580,8,150,20))
      
      
      self.diversityLabel = QtGui.QLabel(self.tableGroup)
      self.diversityLabel.setText('Diversity')
      self.diversityLabel.setGeometry(QtCore.QRect(10, 370, 60, 15))
      
      self.exportdiversity = QtGui.QLabel(self.tableGroup)
      self.exportdiversity.setText('<a href="diversity">export diversity table</a>')
      QtCore.QObject.connect(self.exportdiversity, QtCore.SIGNAL("linkActivated(QString)"), self.export)
      self.exportdiversity.setGeometry(QtCore.QRect(90,368,150,20))
      
      
      ############ sites table #######################
      self.sitesdata = [[' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']]
      self.sitestable =  RADTable(self.sitesdata)
      sitesheader = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
      self.sitestableview = self.sitestable.createTable(sitesheader,editsIndexList=[999],
                                                        container=self.tableGroup)
      self.sitestableview.setGeometry(QtCore.QRect(10,40,450,300))
      self.sitestableview.setSelectionBehavior(QAbstractItemView.SelectColumns)
      ############# species table #######################
      self.speciesdata = [[' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']]
      self.speciestable =  RADTable(self.speciesdata)
      speciesheader = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
      self.speciestableview = self.speciestable.createTable(speciesheader,editsIndexList=[999],
                                                            container=self.tableGroup)      
      self.speciestableview.setGeometry(QtCore.QRect(490,40,450,300))
      self.speciestableview.setSelectionBehavior(QAbstractItemView.SelectColumns)
      
      ############ diversity table #######################
      dl = len(diversityheader)
      self.diversitydata = [l + [' ' for x in range(0,dl)] for l in [[id] for id in allpamsumids]]
      self.diversitytable =  RADTable(self.diversitydata)
      diversityheader.insert(0,'id')
      self.diversitytableview = self.diversitytable.createTable(diversityheader,editsIndexList=[999],
                                                        container=self.tableGroup)
      self.diversitytableview.setGeometry(QtCore.QRect(10,395,450,300))
      
      ##################### Plot Controls ######################################
      self.sitesPlotColumns = QtGui.QRadioButton('Scatter Plot for Sites',self.tableGroup)
      self.sitesPlotColumns.setToolTip("Plot two columns from Sites Table")
      self.sitesPlotColumns.setChecked(False)
      self.sitesPlotColumns.setGeometry(QtCore.QRect(490, 415, 183, 25))
      self.sitesPlotColumns.setObjectName("sitesPlotColumns")
      self.sitesPlotColumns.setEnabled(True)
      
      self.speciesPlotColumns = QtGui.QRadioButton('Scatter Plot for Species',self.tableGroup)
      self.speciesPlotColumns.setToolTip("Plot two columns from Species Table")
      self.speciesPlotColumns.setChecked(False)
      self.speciesPlotColumns.setGeometry(QtCore.QRect(490, 455, 183, 25))
      self.speciesPlotColumns.setObjectName("speciesPlotColumns")
      self.speciesPlotColumns.setEnabled(True)
      ##########################################################################
      
      
      self.gridLayout.addWidget(self.tableGroup,0,0,3,2)
      
     
      #self.getStatsBut = QtGui.QPushButton("Get Stats",self)
      self.acceptBut = QtGui.QPushButton("OK",self)
      self.acceptBut.setDefault(True)
      self.rejectBut = QtGui.QPushButton("Close",self)
      #
      self.buttonBox = QtGui.QDialogButtonBox(self)
      self.buttonBox.setObjectName("buttonBox")
      
      
      self.buttonBox.addButton(self.rejectBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QtGui.QDialogButtonBox.ActionRole)
      
         
      
      self.gridLayout.addWidget(self.buttonBox, 8, 1 ,1, 1)
      
      QtCore.QObject.connect(self.rejectBut, QtCore.SIGNAL("clicked()"), self.reject)
      QtCore.QObject.connect(self.acceptBut, QtCore.SIGNAL("clicked()"), self.accept)
      
      
      #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
      #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept) 
      
      self.retranslateUi()
       
      
      
          
   def retranslateUi(self):
      self.setWindowTitle(QtGui.QApplication.translate("self", 
         "Statistics", None, QtGui.QApplication.UnicodeUTF8))
      
#...............................................................................
#...............................................................................   
