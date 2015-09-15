# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2014 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

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
import sys
from urllib2 import HTTPError
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings,QObject,SIGNAL
from PyQt4.QtCore import Qt, QUrl, QDir
from qgis.core import *
from qgis.gui import *
import lifemapperTools as LM
from lifemapperTools.tools.ui_signInDialog import Ui_Dialog
from lifemapperTools.tools.constructGrid import ConstructGridDialog
from lifemapperTools.tools.listExperiments import ListExperimentDialog
from lifemapperTools.tools.newExperiment import NewExperimentDialog
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.common.pluginconstants import PER_PAGE, QGISProject, SIGNUPURL
from LmClient.lmClientLib import LMClient, OutOfDateException
#from lifemapperTools.common.lmClientLib import LMClient, OutOfDateException


class Ui_SubDialog(object):
   
   def setupUi(self):
      
      self.resize(360, 260)
      self.setMinimumSize(360,260)
      self.setMaximumSize(1478,1448)
      self.setSizeGripEnabled(True)
      self.gridLayout = QGridLayout(self) 
      self.verticalLayout = QVBoxLayout()
      self.typeCodeLabel = QLabel("Type Code Name")
      self.typeCodeName = QLineEdit()
      self.typeCodeTitleLabel = QLabel("Type Code Title")
      self.typeCodeTitle = QLineEdit()
      self.typeCodeDescLabel = QLabel("Description")
      self.typeCodeDesc = QTextEdit()
      self.verticalLayout.addWidget(self.typeCodeLabel)
      self.verticalLayout.addWidget(self.typeCodeName)
      self.verticalLayout.addWidget(self.typeCodeTitleLabel)
      self.verticalLayout.addWidget(self.typeCodeTitle)
      self.verticalLayout.addWidget(self.typeCodeDescLabel)
      self.verticalLayout.addWidget(self.typeCodeDesc)
      
      self.acceptBut = QPushButton("Ok")
      self.rejectBut = QPushButton("Close")
      self.helpBut = QPushButton("?")
      self.helpBut.setMaximumSize(30, 30)
      
      self.buttonBox = QDialogButtonBox()
      self.buttonBox.addButton(self.helpBut, QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.rejectBut, QDialogButtonBox.ActionRole)
      self.buttonBox.addButton(self.acceptBut, QDialogButtonBox.ActionRole)
      
      #QObject.connect(self.rejectBut, SIGNAL("clicked()"), self.reject)
      #QObject.connect(self.acceptBut, SIGNAL("clicked()"), self.accept)
      #QObject.connect(self.helpBut, SIGNAL("clicked()"), self.help)
      
      self.rejectBut.clicked.connect(self.reject)
      self.acceptBut.clicked.connect(self.accept)
      self.helpBut.clicked.connect(self.help)
      
      self.gridLayout.addLayout(self.verticalLayout,0,0,1,1)
      self.gridLayout.addWidget(self.buttonBox,     8,0,1,3)
      self.setWindowTitle("Create New Type Code")




class WorkSpaceDialog(QDialog,Ui_SubDialog):
      def __init__(self,client=None,interface=None):
         QDialog.__init__(self)
         self.setupUi()
         self.typeSubmited = False
         self.client = client


class SignInDialog(QDialog, Ui_Dialog):
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, resumeItem=None,newExperimentItem=None,
                signInItem=None, signOutItem=None, radMenu=None, sdmMenu=None,
                uploadEnvLayerItem=None,saveSlot=None,openSlot=None,changeWSItem=None):
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      self.interface = iface
      self.client = None
      self.radMenu = radMenu
      self.sdmMenu = sdmMenu
      self.resumeAction = resumeItem
      self.newExperimentAction = newExperimentItem
      self.signInAction = signInItem
      self.signOutAction = signOutItem
      self.uploadEnvlayerAction = uploadEnvLayerItem
      self.changeWSAction = changeWSItem
      self.saveProjAction = saveSlot
      self.openProjAction = openSlot
      #QObject.connect(QgsProject.instance(),SIGNAL("writeProject(QDomDocument &)"),self.captureSave)
# ..............................................................................        
## ..............................................................................        
   def accept(self):
      # somewhere in sigin it needs to check for an existing workspace for that user
      # and then if that path/directory exists
      settings = QSettings()
      valid = self.validate()
      if valid:
         try:
            cl = LMClient()
            cl.login(userId=self.keyvalues["usernameEdit"], 
                     pwd=self.keyvalues["passEdit"])
         except OutOfDateException, e:
            message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
            QMessageBox.warning(self,"Problem...",message,QMessageBox.Ok)
         except HTTPError,e:
            if e.code == 401:
               message = "User password combination does not exist"
            else:
               message = str(e)
            msgBox = QMessageBox.warning(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)  
         except:
            message = "No Network Connection"  
            msgBox = QMessageBox.warning(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)        
         else:
            username = str(self.usernameEdit.text())
            self.client = cl
            try:
               myVersion = LM.version() # test"Version 0.1.2" #
               myVersion = myVersion.strip("Version")
               myVersion = myVersion.strip()
               self.client._cl.checkVersion(clientName="lmQGIS",verStr=myVersion)
            except OutOfDateException, e:
               message = "Your plugin version is out of date, please update from the QGIS python plugin repository."
               self.client.logout()
               msgBox = QMessageBox.warning(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok) 
            else:
               self.workspace = Workspace(self.interface,self.client)
               workspace = self.checkCreateWorkSpace(username)
               if workspace:
                  self.signInAction.setEnabled(False)
                  self.radMenu.setEnabled(True)
                  self.sdmMenu.setEnabled(True)
                  self.resumeAction.setEnabled(True)
                  self.newExperimentAction.setEnabled(True)
                  self.uploadEnvlayerAction.setEnabled(True)
                  self.changeWSAction.setEnabled(True)
                  self.signOutAction.setEnabled(True)
                  # connect writeProject and readProject to slot in plugin main
                  #QObject.connect(QgsProject.instance(),SIGNAL("writeProject(QDomDocument &)"),self.saveProjAction)
                  #QObject.connect(self.interface,SIGNAL("projectRead()"),self.openProjAction)
                  
                  QgsProject.instance().writeProject.connect(self.saveProjAction)
                  self.interface.projectRead.connect(self.openProjAction)
                 
                  #################################
                  # set current user and pwd
                  settings.setValue("currentUser",username)
                  settings.setValue(username+"_pwd", self.keyvalues["passEdit"])              
                  ###################################              
                  
                  self.close()
                  workspace = self.workspace.getWSforUser(user=username)
                  message = "User %s is signed into the Lifemapper system. Using %s's workspace %s " % (username,username,workspace) 
                  msgBox = QMessageBox(QMessageBox.NoIcon,"Signed In",message,
                                       QMessageBox.Ok) 
                  pixMap = QPixmap(":/plugins/lifemapperTools/icons/owlSmall.png")
                  msgBox.setIconPixmap(pixMap)
                  msgBox.exec_() 
               else:
                  self.client.logout()
               
               
# ...........................................................................   
   def checkCreateWorkSpace(self,username):
      
      workspace = self.workspace.getWSforUser(user=username)
      if workspace != QGISProject.NOWS:
         workspace = True
      else:
         message = "Next create a workspace for %s" % username
         msgBox = QMessageBox.information(self,
                                          "Create Workspace",
                                          message,
                                          QMessageBox.Ok)
         workspace = self.openDirectoryDialog(username)
         
      return workspace
# ...........................................................................
   def openDirectoryDialog(self, username, existingWorkSpace=False):
      
      settings = QSettings()
      dirName = settings.value( "UI/lastProjectDir" )
      fileDialog = QgsEncodingFileDialog( self, "Create a directory for %s's workspace" % username, dirName) 
      fileDialog.setFileMode( QFileDialog.DirectoryOnly ) 
      fileDialog.setAcceptMode(QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QFileDialog.Accepted:
         if not existingWorkSpace:
            message = "No Workspace Created, Signing %s Out" % username
            msgBox = QMessageBox.warning(self,
                                             "Problem..",
                                             message,
                                             QMessageBox.Ok)
            workspace = False
         if existingWorkSpace:
            message = "Using current workspace"
            msgBox = QMessageBox.information(self,
                                             "Workspace",
                                             message,
                                             QMessageBox.Ok)
            workspace = True
      else:
         filename = fileDialog.selectedFiles()
         # if they choose an existing workspace, do not make a new directory
         existingUser = self.workspace.checkAllWSDirectories(filename[0])
         if existingUser == QGISProject.NOUSER:
            self.createWorkSpace(filename[0]) 
            settings.setValue("%s_ws" % (username),filename[0])
            workspace = True   
         else:
            # this means the dir chosen already exists as a workspace for existingUser
            if existingUser != username:
               message = "Workspace already exists for user %s" % existingUser
               msgBox = QMessageBox.warning(self,
                                             "Workspace",
                                             message,
                                             QMessageBox.Ok)
               workspace = False
            else:
               workspace = True
         
      return workspace
# ...........................................................................      
   def createWorkSpace(self,directory):
      
      QDir().mkdir(directory)
       
# ..............................................................................            
   def validate(self):
      """
      @summary: Validates the inputs for the dialog
      """
      valid = True
      message = ""
      self.keyvalues = {}
      self.keyvalues[str(self.usernameEdit.objectName())] = self.usernameEdit.text()
      self.keyvalues[str(self.passEdit.objectName())] = self.passEdit.text()
      # probably don't need this
      #self.keyvalues[str(self.emailEdit.objectName())] = self.emailEdit.text()
      usrName = self.usernameEdit.text()   
      password = self.passEdit.text()
      self.email = str(self.emailEdit.text())
      verifyEmail = True
      if len(self.email) > 0:
         verifyEmail = self.verifyEmail(self.email)
      else:
         self.email = None
      if len(usrName) <= 0:
         message = "Please supply a user name"
         valid = False
      elif len(password) <= 0:
         message = "Please supply a password"
         valid = False         
      elif not(verifyEmail):
         message = "Please supply valid email"
         valid = False
      if not valid:
         msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
      return valid 
# ..............................................................................
   def verifyEmail(self,email):
      valid = True 
      if '@' in email:
         atIndex = email.index('@')
         domainsubstring = email[atIndex+1:] 
         if '.' in domainsubstring:
            if domainsubstring.index('.') == 0:
               valid = False
         else:
            valid = False
      else:
         valid = False
      return valid
   
   def signup(self, value):
       
      QDesktopServices().openUrl(QUrl(SIGNUPURL))
# ..............................................................................         
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
      helpDialog.scrollToAnchor('signIn')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()   
      
if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   #d = PostScenarioDialog(match=True,scenarioId=204,client=client)
   d = SignInDialog(None)
   d.show()
   sys.exit(qApp.exec_())
