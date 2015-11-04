# -*- coding: utf-8 -*-
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
import sys
import types
import zipfile
import numpy as np
from urllib2 import HTTPError
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.tools.ui_listExperimentDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.tools.listPALayers import ListPALayersDialog
from lifemapperTools.tools.uploadLayers import UploadDialog
from lifemapperTools.tools.listBuckets import ListBucketsDialog
from lifemapperTools.common.pluginconstants import ListExperiments
from lifemapperTools.common.pluginconstants import QGISProject,PER_PAGE
from lifemapperTools.common.workspace import Workspace
from LmClient.lmClientLib import LMClient
from lifemapperTools.tools.addSDMLayer import UploadSDMDialog
from lifemapperTools.tools.radTable import RADTable, RADTableModel
from lifemapperTools.common.communicate import Communicate







class ListExperimentDialog(_Controller, QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, items=None, plot=None, pamsumDialog=None):
      
      QDialog.__init__(self) 
      self.setupUi()
      self.plotDialog = plot
      self.pamSumDialog = pamsumDialog
      self.interface = iface
      self.client = client
      self.workspace = Workspace(self.interface,self.client)
      _Controller.__init__(self, iface, initializeWithData=False,outputfunc=self.showTable,
                           requestfunc=self.client.rad.listExperiments, 
                           client = client)
      if items is None:
         try:
            #items = self.client.rad.listExperiments() 
            items = self.listExperiments()
         except:
            self.close()
            message = "There is a problem with the experiment listing service"
            msgBox = QMessageBox.information(self,
                                             "Problem...",
                                             message,
                                             QMessageBox.Ok)
         else:
            self.showTable(items)     
      elif items is not None:
         self.showTable(items)
# ........................................................
   def checkForDialogs(self):
      """
      @summary: checks for plot or pamsum dialogs and if not none and visible, close
      """     
      try: 
         if self.plotDialog is not None:
            if self.plotDialog.isVisible():
               self.plotDialog.close()
      except:
         pass
      try:
         if self.pamSumDialog is not None:
            if self.pamSumDialog.isVisible():
               self.pamSumDialog.close()
      except:
         pass
   
# ..............................................................................
   def getMapUnitsForEPSG(self,epsg):
      crs = QgsCoordinateReferenceSystem()
      crs.createFromOgcWmsCrs('EPSG:%s'% (epsg))
      mapunitscode = crs.mapUnits()
      if mapunitscode == 0:
         mapunits = 'meters'
      elif mapunitscode == 1:
         mapunits = 'feet'
      elif mapunitscode == 2:
         mapunits = 'dd'
      return mapunits
   
   def openOnDoubleClick(self,index):
      self.checkForDialogs()
      expId = index.model().data[index.row()][1]
      self._compareExpId(expId)
# ..............................................................................
   def _getRADGridCount(self, expId):
      
      try:      
         count = self.client.rad.countBuckets(expId)
      except HTTPError,e :
         count = e
      return count
# ..............................................................................      
   def accept(self, action):

      self.checkForDialogs()

      selectedrowindex = self.tableview.tableView.selectionModel().currentIndex().row()
      selModel = self.tableview.tableView.selectionModel()
      if selectedrowindex == -1 or not(selModel.hasSelection()):
         QMessageBox.warning(self,"status: ",
                         "Please select one experiment")
         return 
      selectedrow = self.tableview.tableView.model().data[selectedrowindex]
      experimentName = selectedrow[0]
      expEPSG = str(selectedrow[2])
      mapunits = self.getMapUnitsForEPSG(expEPSG)
      inputs = {'expId': selectedrow[1]}
      expId = selectedrow[1]
      self._compareExpId(selectedrow[1])
      #self.addGridsToMenu()
      #if self.viewBuckets.isChecked():
      if action == 'buckets':
         self.close()  
         gridCount = self._getRADGridCount(expId)
         if not(isinstance(gridCount, HTTPError)):
            if gridCount > 0:
               d = ListBucketsDialog(self.interface, inputs=inputs,
                               client= self.client, epsg = expEPSG,
                               mapunits=mapunits)
               d.exec_()
            else:
               message = "There are no Grids for this experiment, use Construct Grid from the current experiment menu"
               msgBox = QMessageBox.information(QWidget(),
                                             "Info...",
                                             message,
                                             QMessageBox.Ok)
         else:
            message = "There is a problem with Grid Count"
            msgBox = QMessageBox.information(QWidget(),
                                             "Info...",
                                             message,
                                             QMessageBox.Ok)
      #elif self.viewLayers.isChecked():
      elif action == 'viewLyrs':
         self.close()
         d = ListPALayersDialog( self.interface, inputs=inputs, 
                                 client = self.client, epsg = expEPSG,
                                 mapunits=mapunits)
         d.exec_()  
      #elif  self.addLayer.isChecked():
      elif action == 'addLyrs':
         self.close() 
         d =  UploadDialog( self.interface, inputs = inputs,
                            client = self.client, 
                            epsg = expEPSG,experimentname=experimentName,
                            mapunits = mapunits ) 
         d.exec_()
      #elif self.addSDMLayer.isChecked():
      elif action == 'addSDM':
         self.close()
         SDMDialog = UploadSDMDialog( self.interface, inputs=inputs, 
                                 client = self.client,
                                 epsg = expEPSG,
                                 experimentname=experimentName,
                                 mapunits=mapunits )
         
         SDMDialog.exec_()
# ...........................................................................
   def _showNoExpWarning(self):
      
      message = """The QGIS project file associated with this experiment is
                        missing or can't be opened. This does not affect your experiment."""
      QMessageBox.warning(self,"Warning: ",
      message)
# ...........................................................................      
   def _comparePathToId(self):
      # is the current Id currentExpId = self.retrieveCurrentExpId() the key for 
      # the current QgisProject instance path?
      project = QgsProject.instance()
      filename = str(project.fileName())
      s = QSettings()
      currentExpId = self._retrieveCurrentExpId()
      currentPath = self._retrieveRADExpProjPath(currentExpId)
      if filename != currentPath:
         return False
      else:
         return True      
# ...........................................................................      
   def _compareExpId(self,newid):
      """
      @summary: compares a new exp id with the current experiment
      @param newid: new exp id [integer]
      """
      s = QSettings()
      currentId = self._retrieveCurrentExpId()
      if currentId != QGISProject.NOEXPID:
         if int(newid) != int(currentId):
            project = QgsProject.instance()
            filename = project.fileName()
            # this next section is just saving the current project
            if filename == '':
               if len(QgsMapLayerRegistry.instance().mapLayers().items()) > 0:
                  # wrapping the save as in the workspace allows us
                  # to do a save as without using a file dialog
                  self.workspace.saveQgsProjectAs(currentId)
            else:
               # if there is a qgis project opened
               # if there was  new experiment made, then needs to do a save as?
               if self._comparePathToId():
                  # this saves the old project
                  self.interface.actionSaveProject().trigger()
            
            ############################################
            self._storeCurrentExpId(newid)
            newExpPath = self._retrieveRADExpProjPath(newid)
            if newExpPath == QGISProject.NOPROJECT or newExpPath == '':
               self.interface.actionNewProject().trigger()
               self.workspace.saveQgsProjectAs(newid) 
            else:
               success = self.interface.addProject(newExpPath)
               if not success:
                  self._showNoExpWarning()
         elif int(newid) == int(currentId):
            project = QgsProject.instance()
            filename = str(project.fileName())  # this will be an empty string if there is no
            # project
            currentExpPath = self._retrieveRADExpProjPath(currentId)
            if filename != currentExpPath:
               if currentExpPath != QGISProject.NOPROJECT and filename == '':
                  # open project for currentExpPath
                  success = self.interface.addProject(currentExpPath)
                  if not success:
                     self._showNoExpWarning()                                 
      else:
         self._storeCurrentExpId(newid)
         newExpPath = self._retrieveRADExpProjPath(newid)
         if newExpPath != QGISProject.NOPROJECT and newExpPath != '' :                 
            success = self.interface.addProject(newExpPath)
            if not success:
               self._showNoExpWarning()
         elif newExpPath == QGISProject.NOPROJECT or newExpPath == '':
            self.interface.actionNewProject().trigger()
            self.workspace.saveQgsProjectAs(newid)
            
# ...........................................................................  
   def _retrieveRADExpProjPath(self,id):
      s = QSettings()
      return str(s.value("RADExpProj_"+str(id),QGISProject.NOPROJECT))

# ...........................................................................         
   def _storeRADExpProjPath(self,id,filename): 
      try:
         s = QSettings()
         s.setValue("RADExpProj_"+str(id), filename)
      except:
         QMessageBox.warning(self,"status: ",
                         "Could not save expId to settings") 
      else:
         return True    
# ...........................................................................         
   def _storeCurrentExpId(self,id):
      try:
         s = QSettings()
         s.setValue("currentExpID", id)
      except:
         QMessageBox.warning(self,"status: ",
                         "Could not save expId to settings") 
      else:
         return True
# ...........................................................................         
   def _retrieveCurrentExpId(self):
      s = QSettings()
      currentExpId  = s.value("currentExpID",QGISProject.NOEXPID,type=int)
      return currentExpId     
   

                 
# ..............................................................................        
   def setInputGroup(self,*args):
      """
      @summary: sets the inputs in the inputGroups, is called from thread 
      finished for describe Process mode
      @param parent: input group
      @param args: list of input xml elements from the describe process
      document
      """
      
      
      pass
   
   def tablerowselected(self,itemselectionSelected,itemselectionDeselected):
      
      expId = itemselectionSelected.indexes()[1].data()
      expEPSG = str(itemselectionSelected.indexes()[2].data())
      mapunits = self.getMapUnitsForEPSG(expEPSG)
      #QgsProject.instance().emit( SIGNAL( "ActivateExp(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)" ), expId, expEPSG, mapunits)
      Communicate.instance().activateRADExp.emit(expId,expEPSG,mapunits)

   def getExpCount(self):
      try:
         count = self.client.rad.countExperiments()
      except:
         count = None
      return count
   
   def getNextPage(self,currentPage,forward):
      
      if forward:
         page = currentPage + 1  
      else:
         page = currentPage - 1  
      nextPage = self.listExperiments(page=page)
      if nextPage is not None:
         data = []
         for o in nextPage:
            row = [o.title,int(o.id),o.epsgcode,o.modTime]
            try:
               row.append(o.description)
            except:
               row.append('')
            data.append(row)
         self.expDataView.model().data = data
         self.expDataView.model().setCurrentPage(page)
         #self.expDataView.model().emit(SIGNAL('dataChanged(const QModelIndex &,const QModelIndex &)'),
         #      QModelIndex(), QModelIndex())
         self.expDataView.model().dataChanged.emit(QModelIndex(),QModelIndex())

         readOut = "%s/%s" % (str(page+1),str(self.tableview.noPages))
         self.tableview.pageReadOut.setText(readOut)
         if page == self.tableview.noPages - 1:
            self.tableview.pageForward.setEnabled(False)
         if page == 0:
            self.tableview.pageBack.setEnabled(False)
         if forward:
            self.tableview.pageBack.setEnabled(True)
         else:
            self.tableview.pageForward.setEnabled(True)
      else:
         message = "Could not get the next page"
         msgBox = QMessageBox.warning(self,
                                                  "Problem...",
                                                  message,
                                                  QMessageBox.Ok)
# ..............................................................................         
   def listExperiments(self,pageSize=PER_PAGE,page=0):
      """
      @summary: lists rad experiments
      @return: returns a list of experiment atoms
      """
      items = None
      try:
         items = self.client.rad.listExperiments(perPage=pageSize,page=page)
      except:
         items = None
         message = "There is a problem with the experiment listing service"
         messageBox = QMessageBox.warning(self,
                                 "Problem...",
                                 message,
                                 QMessageBox.Ok)      
      return items      
# ..............................................................................         
   def showTable(self, items, model=None):
      # needs to check for no experiments similar to the way listBuckets work
      expCount = self.getExpCount()
      try:
         if len(items) == 0:
            raise Exception, "No Experiments"
         data = []
         for o in items:
            row = [o.title,int(o.id),o.epsgcode,o.modTime]
            try:
               row.append(o.description)
            except:
               row.append('')
            data.append(row)
         #data = [[o.title,int(o.id),o.epsgcode,o.modTime,desc] for o in items]
         self.tableview =  RADTable(data, totalCount=expCount)
         header = ['   Experiment name   ', '  Exp id  ','  EPSG Code  ', 'ModTime','Description']
         self.expDataView = self.tableview.createTable(header,toolTips=[4])
         #QObject.connect(self.expDataView.model(),SIGNAL("getMore(PyQt_PyObject,PyQt_PyObject)"),self.getNextPage)
         self.expDataView.model().getNext.connect(self.getNextPage)
         if self.expDataView.model().noPages == 1:
               self.tableview.pageForward.setEnabled(False)
               
         
         
         self.expDataView.selectionModel().selectionChanged.connect(self.tablerowselected)
         self.expDataView.doubleClicked.connect(self.openOnDoubleClick)
            
         self.expDataView.setSelectionBehavior(QAbstractItemView.SelectRows)
         self.expDataView.setSelectionMode(QAbstractItemView.SingleSelection)
         #self.tableview.sortByColumn(3) # for non paginated tables sort has to be done like this,
         # even though the data is coming back sorted, http://www.qtforum.org/article/26898/how-to-sort-data-by-column-in-a-table-view-model-set-for-table-view-is-qsqlquerymodel-if-click-to-headerview.html
         # sort() had to be reimplemented in TableModel, to allow for setSortingEnabled on view
         self.gridLayout_input.addWidget(self.tableview,1,1,1,1)
         #self.acceptBut.setEnabled( True )
      except Exception,e:
         
         self.viewLayers.setEnabled(False)
         self.addLayer.setEnabled(False)
         self.viewBuckets.setEnabled(False)
         self.addSDMLayer.setEnabled(False)
         #self.acceptBut.setEnabled(False)
         
         message = "There are no experiments for this user"
         msgBox = QMessageBox.information(self,
                                             "No experiments...",
                                             message,
                                             QMessageBox.Ok)
      
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
      helpDialog.scrollToAnchor('listRADExperiments')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
      
      
if __name__ == "__main__":
#  
   client =  LMClient()
   client.login(userId='', pwd='')
   qApp = QApplication(sys.argv)
   d = ListExperimentDialog(None,client=client)#,experimentId=596106
   d.show()
   sys.exit(qApp.exec_())   
      
      
