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
import numpy as np
from collections import namedtuple
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings, Qt, QUrl, QDir
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.pluginconstants import ListExperiments, GENERIC_REQUEST 
from lifemapperTools.common.pluginconstants import QGISProject


class Workspace:
   
   def __init__(self,iface, client):
      self.interface = iface
      self.client = client
# ...........................................................................      
   def setWSforUser(self, dirPath,user=None):
      s = QSettings()
      currentUsr = str(s.value("currentUser",QGISProject.NOUSER))
      if currentUsr != QGISProject.NOUSER:
         s.setValue("%s_ws" % (currentUsr),dirPath)

   def checkAllWSDirectories(self, dirPath):
      """
      @summary: given a path, does it exist as a workspace for an existing user
      """

      user = QGISProject.NOUSER
      s = QSettings()
      for key in s.allKeys():
         if "_ws" in key:
            value = str(s.value(key))
            if value == dirPath:
               user = key.split('_')[0]
      return user
# ...........................................................................      
   def getWSforUser(self,user=None):
      s = QSettings()
      if user is not None:
         currentUsr = user
      else:
         currentUsr = str(s.value("currentUser",QGISProject.NOUSER))
      if currentUsr != QGISProject.NOUSER:
         ws = str(s.value("%s_ws" % (currentUsr),QGISProject.NOWS))
         if not os.path.exists(ws):
            ws = QGISProject.NOWS
      else:
         ws = QGISProject.NOWS
      return ws
# ...........................................................................   
   def createTreeFolder(self,expId):
      
      expDir = self.getExpFolder(expId)
      if expDir:
         directory = os.path.join(expDir,'tree')
         created = QDir().mkdir(directory)
         if created:
            return directory
         else: return False
# ...........................................................................
   def createOccFolder(self):
      ws = self.getWSforUser()
      directory = False
      if ws != QGISProject.NOWS:
         directory = os.path.join(ws,'occSetsPreviews')
         QDir().mkdir(directory)
      return directory
   
   def getTreeFolder(self,expId):
      directory = False
      expDir = self.getExpFolder(expId)
      if expDir:
         if os.path.exists(os.path.join(expDir,'tree')):
            directory = os.path.join(expDir,'tree')
      return directory
# ...........................................................................
   def getOccSetFolder(self):
      occFolder = False
      ws = self.getWSforUser()
      if ws != QGISProject.NOWS:
         if os.path.exists(os.path.join(ws,'occSetsPreviews')):
            occFolder = os.path.join(ws,'occSetsPreviews')          
      return occFolder
# ...........................................................................   
   def getExpFolder(self,expId):
      directory = False
      ws = self.getWSforUser()
      if ws != QGISProject.NOWS:
         dirs = os.walk(ws).next()[1]
         for folder in dirs:
            if folder.endswith("_"+str(expId)):
               directory = os.path.join(ws,folder)
               break
      return directory
# ...........................................................................   
   def getExpTitleforId(self, expId):
      """
      @summary: gets the experiment type and experiment name for a Lm experiment expId
      @param expId: Lm experiment expId
      """
      title = False
      try:
         exp = self.client.rad.getExperiment(expId)
      except Exception, e:
         try:
            exp = self.client.sdm.getExperiment(expId)
         except:
            title = False
         else:
            title = exp.model.name
            #title = exp.model.occurrenceSet.displayName
      else:
         title = exp.name
      return title
# ...........................................................................   
   def createProjectFolder(self,expId):
      ws = self.getWSforUser()
      directory = False
      if ws != QGISProject.NOWS:
         expName = self.getExpTitleforId(expId)
         prjName = "%s_%s" % (expName,expId)
         directory = os.path.join(ws,prjName)
         QDir().mkdir(directory)
      return directory
# ...........................................................................   
   def saveQgsProjectAs(self, expId):
      """
      @summary: sets the new filename for an existing experiment with an empty project and does
      a save vs. a save as, since the filename gets set before saving
      """
      prj = QgsProject.instance()
      expName = self.getExpTitleforId(expId)  
      ws = self.getWSforUser()
      # what happens if ws is QGISProject.NOWS, in the case of the workspace having been deleted
      # or renamed?
      if expName:
         prjDirName = "%s_%s" % (expName,expId)
         if ws != QGISProject.NOWS:
            if not self.getExpFolder(expId):
               QDir().mkdir(os.path.join(ws,prjDirName))
            filepath = os.path.join(ws,prjDirName,'%s.qgs' % expName)
            prj.setFileName(filepath)
         else:
            print "path doesn't exist"
      else:
         if ws != QGISProject.NOWS:
            prj.setFileName(os.path.join(ws,'%s.qgs' % expId))
      #if filepath: # one last check for dir before it saves
      #   if not os.path.exists(os.path.join(ws,prjDirName)):
      #      QDir().mkdir(os.path.join(ws,prjDirName))
      self.interface.actionSaveProject().trigger()

      