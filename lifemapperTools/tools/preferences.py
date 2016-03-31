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
import os
import ConfigParser
from PyQt4 import QtCore, QtGui
#from qgis.utils import reloadPlugin, unloadPlugin
import lifemapperTools as LM
from lifemapperTools.common.pluginconstants import  CURRENT_WEBSERVICES_ROOT
from LmClient.lmClientLib import LMClient, OutOfDateException
from lifemapperTools.common.lmListModel import LmListModel

ICON_VALUES = {'server':'SERVER'}
#CONFIG = os.environ.get("LIFEMAPPER_CONFIG_FILE")
CONFIG = "/home/jcavner/ghWorkspace/LmQGIS.git/lifemapperTools/config/site.ini" # comment out when in qgis
SECTION = 'LmCommon - common'
ITEM = 'CURRENT_WEBSERVICES_ROOT'


#BANNER_ICONS = {'idigbio':':/plugins/lifemapperTools/icons/idigbio_logo_0.png',
#               'lifemapper':':/plugins/lifemapperTools/icons/lm_poster_276_45.png'}

def getURLFromConfig():

   try:
      cfg = ConfigParser.SafeConfigParser()
      cfg.read(CONFIG)
      url = cfg.get(SECTION,ITEM)
   except:
      url = None
   return url


class ClickableLabel(QtGui.QLabel):
   
   clicked = QtCore.pyqtSignal(str)
   
   def __init__(self):
      
      QtGui.QLabel.__init__(self)
      #super(ClickableLabel, self).__init__()
      pixmap = QtGui.QPixmap(":/plugins/lifemapperTools/icons/server.png") # in QGIS
      #pixmap = QtGui.QPixmap("../icons/server.png") # in eclipse
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
      #self.resize(478, 448)
      self.setMinimumSize(576,448)
      self.setMaximumSize(576,448)
      #self.setSizeGripEnabled(True)
       
      
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
      self.serverLabel.setToolTip("Change Lifemapper instance or server that provides LM Web Services")
      self.serverLabel.clicked.connect(self.changeSettings)
      self.changeServerLab = QtGui.QLabel("Services URL")
      
      #self.websiteRoot = QtGui.QLineEdit()
      #self.websiteRoot.setText(CURRENT_WEBSERVICES_ROOT)
      
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
      self.changeServLyout.setRowMinimumHeight(1,20)
      self.changeServLyout.setRowMinimumHeight(2,30)
      self.changeServLyout.setRowMinimumHeight(3,230)
      self.changeServLyout.setRowMinimumHeight(4,30)
      
      
      
      stableLmInstances = QtGui.QLabel("Stable Lifemapper Instances")
      
      self.serverList = self.makeServerListView()
      self.serverRadio = self.makeServerRadio()
      
      currentLyOut = QtGui.QGridLayout()
      currentLyOut.setRowMinimumHeight(0,10)
      currentLyOut.setRowMinimumHeight(0,10)
      currentServerTxt = QtGui.QLabel("current server:")
      self.serverTxt = QtGui.QLabel("http://svc.lifemappper.org")
      self.serverTxt.setMaximumWidth(190)
      #serverTxt.setWordWrap(True)
      currentLyOut.addWidget(currentServerTxt,0,0,1,1, QtCore.Qt.AlignBottom)
      currentLyOut.addWidget(self.serverTxt,1,0,1,1,QtCore.Qt.AlignTop)
      
      self.addNewBut = QtGui.QPushButton("Add New")
      self.addNewBut.clicked.connect(self.openAddNewUrl)
      self.addNewBut.setEnabled(False)
      
      self.changeServLyout.addWidget(self.allSettings, 0,0,1,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addWidget(stableLmInstances,1,0,1,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addWidget(self.serverList,  2,0,2,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addLayout(self.serverRadio, 2,2,1,1,QtCore.Qt.AlignTop)
      self.changeServLyout.addLayout(currentLyOut,     3,2,1,1)#,QtCore.Qt.AlignTop)
      self.changeServLyout.addWidget(self.addNewBut, 4,0,1,1, QtCore.Qt.AlignBottom)

      
      self.gridLayout.addWidget(self.inputGroup, 4,0,4,0)
      self.gridLayout.addWidget(self.serverChangeGroup, 4,0,4,0)
      self.gridLayout.setRowStretch(4,6)
      
      
      
      ########################################
      #
      self.helpBut = QtGui.QPushButton("?",self)
      self.helpBut.setMaximumSize(30, 30)
      #
      self.acceptBut = QtGui.QPushButton("Save Changes",self)
      self.acceptBut.clicked.connect(self.writeInit)
      self.acceptBut.setEnabled(False)
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
      
      self.defaultBut = QtGui.QRadioButton("Restore Defaults")
      #self.defaultBut.setChecked(True)
      self.other = QtGui.QRadioButton("Change")
      self.serverGroup.addButton(self.defaultBut)
      self.serverGroup.addButton(self.other)
      self.serverGroup.setId(self.defaultBut,1)
      self.serverGroup.setId(self.other,2)
      self.serverGroup.buttonClicked[int].connect(self.radioSeverChanged)
      
      #vertLyOut = QtGui.QVBoxLayout()
      vertLyOut = QtGui.QGridLayout()
      vertLyOut.setRowMinimumHeight(0,20)
      vertLyOut.setRowMinimumHeight(1,20)
      vertLyOut.addWidget(self.defaultBut,0,0,1,1)
      vertLyOut.addWidget(self.other,1,0,1,1)
      
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
   
   
class NewUrlSubDialog(QtGui.QDialog):
   
   def __init__(self, parent):
      QtGui.QDialog.__init__(self)
      self.parent = parent
      self.parent.acceptBut.setEnabled(False)
      self.setWindowTitle("New Url")
      self.setMinimumSize(376,100)
      self.setMaximumSize(376,100)
      
      gridLyOut = QtGui.QGridLayout(self)
      gridLyOut.setRowMinimumHeight(0,50)
      gridLyOut.setRowMinimumHeight(1,50)
      
      gridLyOut.setColumnMinimumWidth(0,350)
      gridLyOut.setColumnMinimumWidth(1,5)
      
      self.enterUrlLine = QtGui.QLineEdit()
      
      
      
      newUrlAccept = QtGui.QPushButton("Accept")
      newUrlAccept.clicked.connect(self.accept)
      cancel = QtGui.QPushButton("Cancel")
      cancel.clicked.connect(self.reject)
      
      self.buttonBox = QtGui.QDialogButtonBox()
      
      self.buttonBox.addButton(cancel,QtGui.QDialogButtonBox.RejectRole)
      self.buttonBox.addButton(newUrlAccept,QtGui.QDialogButtonBox.ActionRole)
      
      gridLyOut.addWidget(self.enterUrlLine,0,0,1,2)
      gridLyOut.addWidget(self.buttonBox,   1,1,1,1)
           
   def accept(self):
      
      newUrl = self.enterUrlLine.text()
      if newUrl != '':
         try:
            cl = LMClient(server=newUrl)
         except:
            self.parent.acceptBut.setEnabled(False)
            message = "invalid lifemapper web services url"
            self.enterUrlLine.clear()
            QtGui.QMessageBox.warning(self,
                                          "Problem...",
                                          message,
                                          QtGui.QMessageBox.Ok)
         else:
            
            self.parent.setCurrentUrlTxt(newUrl)
            if newUrl != getURLFromConfig():
               self.parent.newUrl = newUrl
               self.parent.acceptBut.setEnabled(True)
               self.parent.acceptBut.setFocus(True)
            else:
               self.parent.newUrl = None
               self.parent.acceptBut.setEnabled(False)
            self.close()
      elif newUrl == '':
         self.close()

class PreferencesDialog(QtGui.QDialog,Ui_Dialog):
   
   def __init__(self):
      
      QtGui.QDialog.__init__(self)
      self.client = None
      self.newUrl = None
      #self.bannerPath = None
      self.setupUi()
      #self.setCurrentUrlTxt(CURRENT_WEBSERVICES_ROOT)  # might want to put this in changeSettings
      self.setWindowTitle("Settings")
   
   def openAddNewUrl(self):
   
      d = NewUrlSubDialog(self)
      d.exec_()
   
   def setCurrentUrlTxt(self, serverUrl):
      """
      @summary: sets text, and maybe should set self.newUrl
      """
      self.serverTxt.setText(serverUrl)
         
   def radioSeverChanged(self, radioId):
      """
      @summary: change back and forth from default
      @param radioId: id from radio button
      """
      if radioId == 1:
         self.resetToDefault()
      else:
         self.serverList.setEnabled(True)
         self.addNewBut.setEnabled(True)
   
   #def getBanner(self,Sn):
   #   
   #   iconPth = None
   #   if Sn.lower() in BANNER_ICONS:
   #      iconPth = BANNER_ICONS[Sn.lower()]
   #   return iconPth
                 
   def resetToDefault(self):
      """
      @summary: resets url to default and disables 
      change controls
      """
      
      # get lifemapper
      lifemapperUrlList = self.serverListModel.match(self.serverListModel.index(0),QtCore.Qt.DisplayRole,
                                                     "lifemapper", hits= 1, flags = QtCore.Qt.MatchContains)
      if len(lifemapperUrlList) > 0:
         serverIdx = lifemapperUrlList[0]
         self.serverList.setCurrentIndex(serverIdx)
         
         newUrl = self.serverListModel.listData[serverIdx.row()][1]
         serverName = self.serverListModel.listData[serverIdx.row()][0]
         self.setCurrentUrlTxt(newUrl)
         if newUrl != getURLFromConfig():
            self.acceptBut.setEnabled(True)
            #self.bannerPath = self.getBanner(serverName)
            self.newUrl = newUrl
         else:
            
            self.newUrl = None
            self.acceptBut.setEnabled(False)
         
      self.serverList.setEnabled(False)
      self.addNewBut.setEnabled(False)  
   
   def changeServer(self, index):
      """
      @summary: called on selection in server list
      """
      newUrl = self.serverListModel.listData[index.row()][1]
      print "n url ",newUrl," ",getURLFromConfig()
      serverName = self.serverListModel.listData[index.row()][0]
      self.setCurrentUrlTxt(newUrl)
      if newUrl != getURLFromConfig():
         self.acceptBut.setEnabled(True)
         self.acceptBut.setFocus(True)
         print "new url"
         self.newUrl = newUrl
         #self.bannerPath = self.getBanner(serverName)
      else:
         self.newUrl = None
         self.acceptBut.setEnabled(False)
         
   def goToAll(self, groupToHide=None):
      
      self.signOut()  # might not need
      self.acceptBut.setEnabled(False)
      self.serverChangeGroup.hide()
      self.inputGroup.show()
   
   def buildClient(self):
      try:
         cl = LMClient()
      except OutOfDateException, e:
         message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
         QtGui.QMessageBox.warning(self,"Problem...",message,QtGui.QMessageBox.Ok)
      except Exception, e:
         message = "No Network Connection, check url or change"
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
      
      currentInInstances = False
      try:
         instanceObjs = self.client.getAvailableInstances()
      except: 
         pass
      else:        
         items = []
         
         for server in instanceObjs:
            items.append(server)
            if server[1] == CURRENT_WEBSERVICES_ROOT:
               currentInInstances = True 
         #items.extend([(x,str(x)+"_server") for x in range(0,4)])
         items.extend([('idigbio', 'http://lifemapper.org')])     
         self.serverListModel.updateList(items)
      return currentInInstances
   
   def signOut(self):
      pass
   
   def initialUrlGroupSettings(self, currentInInstances):
      """
      @summary: resets everything
      """
      if not currentInInstances:
         self.defaultBut.setChecked(False)
      else:
         self.defaultBut.setChecked(True)
      
      self.serverList.setEnabled(False)
      self.addNewBut.setEnabled(False)  
      self.acceptBut.setEnabled(False) 
      self.setCurrentUrlTxt(CURRENT_WEBSERVICES_ROOT)
      
      # sets list to CURRENT_WEBSERVICES_ROOT
      currentUrlIdxList = self.serverListModel.match(self.serverListModel.index(0),
                                                     QtCore.Qt.DisplayRole ,CURRENT_WEBSERVICES_ROOT)
      if len(currentUrlIdxList) > 0:
         currentUrlIdx = currentUrlIdxList[0]
         self.serverList.setCurrentIndex(currentUrlIdx)
         
     
   def changeSettings(self):
      """
      @summary: called from main settings group, sets up Web Services URL change group
      """
      self.setCurrentUrlTxt(CURRENT_WEBSERVICES_ROOT)
      if self.client == None:
            self.buildClient()
      if self.client is not None:
         self.serverListModel = ServerModel([],self)
         self.serverList.setModel(self.serverListModel)
         currentInInstances = self.getInstances()
         self.initialUrlGroupSettings(currentInInstances)
         self.inputGroup.hide()
         self.serverChangeGroup.show()
         
      elif self.client is None:  # this is if they somehow have a bad url so that signIn doesn't work
         
         self.defaultBut.setEnabled(False)
         self.serverList.setEnabled(False)
         self.other.setChecked(True)
         self.addNewBut.setEnabled(True)
         self.inputGroup.hide()
         self.serverChangeGroup.show()  
         
   def writeInit(self):   
      """
      @summary: make changes to CURRENT_WEBSERVICES_ROOT in ini file
      """
      if self.newUrl is not None and CONFIG is not None:
         try:
            
            url = str(self.newUrl)
            
            cfgPath = CONFIG
            sec = SECTION
            k = ITEM
            cfg = ConfigParser.SafeConfigParser()
            cfg.read(cfgPath)
            cfg.set(sec,k,url) 
            print "w url"
            cfg.set(sec,"OGC_SERVICE_URL",os.path.join(url,"ogc"))  
            #if self.bannerPath is not None:
            #   print "w banner"
            #   cfg.set(sec,"BROWSER_BANNER",self.bannerPath)          
            with open(cfgPath, 'wb') as configfile:
               cfg.write(configfile)   
         except Exception, e:
            message = "Could not save changes "+str(e)
            msgBox = QtGui.QMessageBox.warning(self,
                                                "Problem...",
                                                message,
                                                QtGui.QMessageBox.Ok)
         else:
            self.acceptBut.setEnabled(False)
            message = "You will need to restart QGIS for the changes to take effect."
            QtGui.QMessageBox.information(self,
                                          "Changed services URL",
                                          message,
                                          QtGui.QMessageBox.Ok)
         
         
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