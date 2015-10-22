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
import sys
import ConfigParser
from PyQt4 import QtCore, QtGui
#from qgis.utils import reloadPlugin, unloadPlugin
import lifemapperTools as LM
from LmCommon.common.localconstants import  WEBSERVICES_ROOT
from LmClient.lmClientLib import LMClient, OutOfDateException
from lifemapperTools.common.lmHint import LmListModel


ICON_VALUES = {'server':'SERVER'}


class ClickableLabel(QtGui.QLabel):
   
   clicked = QtCore.pyqtSignal(str)
   
   def __init__(self):
      
      QtGui.QLabel.__init__(self)
      #super(ClickableLabel, self).__init__()
      #pixmap = QtGui.QPixmap(":/plugins/lifemapperTools/icons/server.png") # in QGIS
      pixmap = QtGui.QPixmap("../icons/server.png") # in eclipse
      self.setPixmap(pixmap)
      self.setObjectName(ICON_VALUES['server'])
   
   def mousePressEvent(self, event):
      self.clicked.emit(self.objectName())




class Ui_Dialog(object):
   
   
   def HLine(self):
      
      hLine = QtGui.QFrame()
      hLine.setFrameShape(QtGui.QFrame.HLine)
      hLine.setFrameShadow(QtGui.QFrame.Sunken)
      return hLine
   
   def setupUi(self):
      
      self.setObjectName("Dialog")
      self.resize(478, 448)
      self.setMinimumSize(576,448)
      self.setMaximumSize(576,448)
      self.setSizeGripEnabled(True)
       
      
      self.gridLayout = QtGui.QGridLayout(self)
      self.gridLayout.setObjectName("gridLayout")
       
      ######  splash group
      self.inputGroup = QtGui.QGroupBox(self)
      self.inputGroup.setObjectName("inputGroup")
      self.style = QtGui.QStyleFactory.create("motif") # try plastique too!
      self.inputGroup.setStyle(self.style)
      self.gridLayout_input = QtGui.QGridLayout(self.inputGroup)
      self.gridLayout_input.setObjectName("gridLayout_input")
      
      self.gridLayout_input.setRowMinimumHeight(0,20)
      self.gridLayout_input.setRowMinimumHeight(1,100)
      self.gridLayout_input.setRowMinimumHeight(2,20)
      self.gridLayout_input.setRowMinimumHeight(3,20)
      self.gridLayout_input.setRowMinimumHeight(4,150)
      
      
      ## server
      self.serverTitle = QtGui.QLabel("Web Services")
      serverLine = self.HLine()
      self.serverLabel = ClickableLabel()
      self.serverLabel.clicked.connect(self.changeSettings)
      self.changeServerLab = QtGui.QLabel("Change Server")
      
      #self.websiteRoot = QtGui.QLineEdit()
      #self.websiteRoot.setText(WEBSERVICES_ROOT)
      
      self.gridLayout_input.addWidget(self.serverTitle,0,0,1,1,QtCore.Qt.AlignTop)
      self.gridLayout_input.addWidget(self.serverLabel,1,0,1,1)
      self.gridLayout_input.addWidget(self.changeServerLab,2,0,1,1)
      self.gridLayout_input.addWidget(serverLine,3,0,1,1)
      ##################
      # back and tab buttons
      self.allSettings = QtGui.QPushButton("All Settings")
      self.allSettings.setMaximumHeight(25)
      self.allSettings.setMaximumWidth(85)
      self.allSettings.clicked.connect(self.goToAll)
      ####### server group
      
      self.serverChangeGroup = QtGui.QGroupBox(self)
      
      self.serverChangeGroup.setStyle(self.style)
      self.serverChangeGroup.hide()
      self.changeServLyout = QtGui.QGridLayout(self.serverChangeGroup)
      
      self.changeServLyout.setColumnMinimumWidth(0,50)
      self.changeServLyout.setColumnMinimumWidth(1,5)
      self.changeServLyout.setColumnMinimumWidth(2,150)
      
      self.changeServLyout.setContentsMargins(0,10,0,10)
      
      self.changeServLyout.setRowMinimumHeight(0,10)
      self.changeServLyout.setRowMinimumHeight(1,30)
      self.changeServLyout.setRowMinimumHeight(2,230)
      self.changeServLyout.setRowMinimumHeight(3,30)
      
      self.serverList = self.makeServerListView()
      self.serverRadio = self.makeServerRadio()
      
      currentLyOut = QtGui.QGridLayout()
      currentLyOut.setRowMinimumHeight(0,10)
      currentLyOut.setRowMinimumHeight(0,10)
      currentServerTxt = QtGui.QLabel("current server:")
      serverTxt = QtGui.QLabel("http://svc.lifemappper.org")
      serverTxt.setMaximumWidth(190)
      #serverTxt.setWordWrap(True)
      currentLyOut.addWidget(currentServerTxt,0,0,1,1, QtCore.Qt.AlignBottom)
      currentLyOut.addWidget(serverTxt,1,0,1,1,QtCore.Qt.AlignTop)
      
      self.addNewBut = QtGui.QPushButton("Add New")
      self.addNewBut.setEnabled(False)
      
      self.changeServLyout.addWidget(self.allSettings, 0,0,1,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addWidget(self.serverList,  1,0,2,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addLayout(self.serverRadio, 1,2,1,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addLayout(currentLyOut,     2,2,1,1)#,QtCore.Qt.AlignTop)
      self.changeServLyout.addWidget(self.addNewBut, 3,0,1,1, QtCore.Qt.AlignBottom)

      
      self.gridLayout.addWidget(self.inputGroup, 4,0,4,0)
      self.gridLayout.addWidget(self.serverChangeGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
      
      
      
      ########################################
      #
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      #
      self.acceptBut = QtGui.QPushButton("OK",self)
      self.acceptBut.setDefault(True)
      self.buttonBox = QtGui.QDialogButtonBox(self)
      #
      #
      self.buttonBox.addButton(self.helpBut, QtGui.QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut,QtGui.QDialogButtonBox.ActionRole)
      #
      #
      self.buttonBox.setObjectName("buttonBox")
      self.gridLayout.addWidget(self.buttonBox, 8, 0 ,7, 3)
      #
      #self.helpBut.clicked.connect(self.help)
      #self.acceptBut.clicked.connect(self.accept)
   
   
   def makeServerRadio(self):
      
      #try:
      self.serverGroup = QtGui.QButtonGroup()
      
      defaultBut = QtGui.QRadioButton("default")
      defaultBut.setChecked(True)
      other = QtGui.QRadioButton("other")
      self.serverGroup.addButton(defaultBut)
      self.serverGroup.addButton(other)
      self.serverGroup.setId(defaultBut,1)
      self.serverGroup.setId(other,2)
      self.serverGroup.buttonClicked[int].connect(self.radioSeverChanged)
      
      #vertLyOut = QtGui.QVBoxLayout()
      vertLyOut = QtGui.QGridLayout()
      vertLyOut.setRowMinimumHeight(0,20)
      vertLyOut.setRowMinimumHeight(1,20)
      vertLyOut.addWidget(defaultBut,0,0,1,1)
      vertLyOut.addWidget(other,1,0,1,1)
      
      return vertLyOut
      
   def makeServerListView(self):
      
      serverList = QtGui.QListView()
      serverList.setEnabled(False)
      serverList.setMaximumWidth(310)
      serverList.setMinimumHeight(270)
      serverList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      serverList.clicked.connect(self.changeServer)
      serverList.setEnabled(False)
      # remember 
      # self.serversList.clearSelection()
      # indexObjs = self.projectionScenListView.selectedIndexes() # for multiple
      return serverList

class PreferencesDialog(QtGui.QDialog,Ui_Dialog):
   
   def __init__(self):
      
      QtGui.QDialog.__init__(self)
      self.client = None
      self.setupUi()
      self.setWindowTitle("Settings")
   
   def radioSeverChanged(self, radioId):
      
      if radioId == 1:
         self.resetToDefault()
      else:
         print "do something else"
              
   def resetToDefault(self):
      
      self.serverList.setEnabled(False)
      self.addNewBut.setEnabled(False)  
   
   def changeServer(self):
      
      print "change server"
   
   def goToAll(self, groupToHide=None):
      
      self.signOut()
      self.serverChangeGroup.hide()
      self.inputGroup.show()
   
   def buildClient(self):
      try:
         cl = LMClient()
      except OutOfDateException, e:
         message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
         QtGui.QMessageBox.warning(self,"Problem...",message,QtGui.QMessageBox.Ok)
      except:
         message = "No Network Connection"
         QtGui.QMessageBox.warning(self,"Problem...",message,QtGui.QMessageBox.Ok)
      else:
         self.client = cl
         #print "COOKIE AT TOGGLE WIDGET ",self.client._cl.cookieJar," ",self.client
         try:
            myVersion = LM.version() # test"Version 0.1.2" #
            myVersion = myVersion.strip("Version")
            myVersion = myVersion.strip()
            self.client._cl.checkVersion(clientName="lmQGIS",verStr=myVersion)
         except OutOfDateException, e:
            
            message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
            self.client.logout()
            self.client = None
            msgBox = QtGui.QMessageBox.warning(self,
                                             "Problem...",
                                             message,
                                             QtGui.QMessageBox.Ok)
   def getInstances(self):
      try:
         instanceObjs = self.client.sdm.getAvailableInstances()
      except:
         pass
      else:         
         items = []
         for server in instanceObjs:
            items.append(server)
         self.serverListModel.updateList(items)
   
   def signOut(self):
      pass
      
      
   def changeSettings(self, changeType):
      
      if self.client == None:
            self.buildClient()
      if self.client is not None:
         
         self.serverListModel = ServerModel([],self)
         self.serverList.setModel(self.serverListModel)
         self.getInstances()
      
         self.inputGroup.hide()
         self.serverChangeGroup.show()
      #sec = 'LmCommon - common'
      #k = 'WEBSERVICES_ROOT'
      #cfgPath = "/home/jcavner/ghWorkspace/core.git/config/site.ini"
      ##print changeType
      #cfg = ConfigParser.SafeConfigParser()
      #cfg.read(cfgPath)
      #if WEBSERVICES_ROOT == 'http://svc.lifemapper.org':
      #   print "flip to yeti"
      #   url = "http://yeti.lifemapper.org"
      #   cfg.set(sec,k,url)
      #else:
      #   print "flip to lifemapper"
      #   url = "http://svc.lifemapper.org"
      #   cfg.set(sec,k,url)
      #   
      #with open(cfgPath, 'wb') as configfile:
      #   cfg.write(configfile)   
class ServerModel(LmListModel):
   
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if index.isValid() and (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
         if index.row() == 1 and self.model:
            return "build new model"
         else:   
            try: return self.listData[index.row()][1]
            except: return self.listData[index.row()]  # probably want to watch this
           
      if index.isValid() and role == QtCore.Qt.UserRole:
         return int(self.listData[index.row()])
      else:
         return 
      
if __name__ == "__main__":
#  
   
   qApp = QtGui.QApplication(sys.argv)
   d = PreferencesDialog()#,experimentId=596106
   d.show()
   sys.exit(qApp.exec_())   