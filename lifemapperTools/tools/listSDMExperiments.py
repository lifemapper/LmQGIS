# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2011 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

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
import os
import sys
import zipfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.lmClientLib import LMClient
from lifemapperTools.common.workspace import Workspace
from lifemapperTools.tools.ui_listSDMExpsDialog import Ui_Dialog
from lifemapperTools.tools.radTable import RADTable
from lifemapperTools.icons import icons
from lifemapperTools.common.pluginconstants import STATUSLOOKUP,QGISProject, JobStatus,\
                                                   PER_PAGE



class ListSDMExpDialog(QDialog, Ui_Dialog):
   
   
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, inputs=None, client=None, experimentId=None):
      
      QDialog.__init__(self)
      self.setupUi()
      self.interface = iface
      self.client = client
      self.workspace = Workspace(self.interface,self.client)
      self.hasOccMetadata = False
      self.backOneLinkOcc = None
      self.backTwoLinkOcc = None
      self.backOneLinkProj = None
      self.backTwoLinkProj = None
      self.emptyTableView = None
      if experimentId == None:
         self.currentExp = False
         items = self.listExperiments()
         self.showExpTable(items)
      else:
         self.currentExp = True
         self.viewExeprimentInit(experimentId)
      
# ...........................................................................
   def _showNoExpWarning(self):
      """
      @summary: shows a warning if the qgis project file is missing
      """
      
      message = QString("The QGIS project file associated with this experiment is\n"
                        "missing or can't be opened. This does not affect your experiment.\n\n")
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
            print "file name on new experiment ",filename
            if filename == '':
               # if there is no current qgis project and there are layers save as
               if len(QgsMapLayerRegistry.instance().mapLayers().items()) > 0:
                  #self.interface.actionSaveProjectAs().trigger()
                  self.workspace.saveQgsProjectAs(currentId)
            else:
               # if there was  new experiment made, then needs to do a save as?
               if self._comparePathToId():
                  # this saves the old project
                  self.interface.actionSaveProject().trigger()
               
            ####################################################
            
            # store the new id as the current experiment id
            self._storeCurrentExpId(newid)
            # see if there is a path for the new experiment id, if not
            # open a new qgis project, if there is a path, open that
            # qgis project
            newExpPath = self._retrieveRADExpProjPath(newid)
            if newExpPath == QGISProject.NOPROJECT or newExpPath == '':
               self.interface.actionNewProject().trigger()
            else:
               success = self.interface.addProject(newExpPath)
               if not success:
                  self._showNoExpWarning()
         elif int(newid) == int(currentId):
            # if user selects the current exp get the path for the current qgis project
            # and compare to the path stored in the settings for that id
            project = QgsProject.instance()
            filename = str(project.fileName())
            currentExpPath = self._retrieveRADExpProjPath(currentId)
            if filename != currentExpPath:
               # this is specifically for the case of where creating
               # a new experiment activates the current experiment in the menu 
               # then if you were to list experiments and choose the current experiment
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
      """
      @summary: retrieves the project path for an experiment from the settings
      @param id: experiment id
      """
      s = QSettings()
      return str(s.value("RADExpProj_"+str(id),QGISProject.NOPROJECT).toString())

# ...........................................................................         
   def _storeRADExpProjPath(self,id,filename): 
      """
      @summary: stores a project path for an experiment id
      @param filename: path 
      """
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
      """
      @summary: stores the current experiment id
      @param id: current experiment id
      """
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
      """
      @summary: retrieves the current experiment id
      @return: the current exp id
      """
      s = QSettings()
      currentExpId  = s.value("currentExpID",QGISProject.NOEXPID).toInt()[0]
      return currentExpId     
   

# ...........................................................................   
   def listExperiments(self,pageSize=PER_PAGE,page=0):
      """
      @summary: lists sdm experiments
      @return: returns a list of experiment atoms
      """
      items = None
      try:
         items = self.client.sdm.listExperiments(perPage=pageSize,page=page)
      except:
         items = None
         message = "There is a problem with the experiment listing service"
         messageBox = QMessageBox.warning(self,
                                 "Problem...",
                                 message,
                                 QMessageBox.Ok)      
      return items
# ...........................................................................   
   def getOccSet(self, occId):
      occSet = None
      try:
         occSet = self.client.sdm.getOccurrenceSet(occId)
      except Exception,e:
         
         message = "There is a problem with the species points for this experiment, "+str(e)
         messageBox = QMessageBox.warning(self,
                                 "Problem...",
                                 message,
                                 QMessageBox.Ok)              
      return occSet
# ........................................................................... 
   def getExperiment(self,expId):
      try:
         experiment = self.client.sdm.getExperiment(expId)
      except:
         experiment = None
         QMessageBox.warning(self,"Error: ",
              "Problem with retrieving the experiment")
      return experiment
# ...........................................................................      
   def switchView(self, hide, show):
      hide.hide()
      show.show()
# ...........................................................................      
   def switchtoExpTableFromDetails(self):
      self.setWindowTitle("Spatial Distribution Modeling Experiments")      
      self.switchView(self.viewExpGroup,self.expTableView)
# ...........................................................................     
   def switchtoExpTableFromProj(self):
      self.setWindowTitle("Spatial Distribution Modeling Experiments")
      self.backOneLinkProj.hide()
      self.backTwoLinkProj.hide()
      try:
         self.switchView(self.projsTableView, self.expTableView) 
      except:
         try:
            self.switchView(self.emptyTableView, self.expTableView)
         except:
            pass
# ...........................................................................                 
      
   def switchtoExpViewFromProj(self):
      self.setWindowTitle("Experiment Details")      
      self.backOneLinkProj.hide()
      if not self.currentExp:
         self.backTwoLinkProj.hide()
      try:
         self.switchView(self.projsTableView, self.viewExpGroup)
      except:
         try:
            self.switchView(self.emptyTableView, self.viewExpGroup)
         except:
            pass
# ...........................................................................      
   def switchtoExpTableFromOcc(self):
      self.setWindowTitle("Spatial Distribution Modeling Experiments")
      self.backOneLinkOcc.hide()
      self.backTwoLinkOcc.hide()
      try:
         #self.switchView(self.occTableView, self.expTableView) 
         self.switchView(self.viewOccSetGroup, self.expTableView)
      except:
         try:
            self.switchView(self.emptyTableView, self.expTableView)
         except:
            pass             
# ...........................................................................      
   def switchtoExpViewFromOcc(self):  
      self.setWindowTitle("Experiment Details")    
      self.backOneLinkOcc.hide()
      if not self.currentExp:
         self.backTwoLinkOcc.hide()
      try:
         #self.switchView(self.occTableView, self.viewExpGroup)
         self.switchView(self.viewOccSetGroup, self.viewExpGroup)
      except:
         try:
            self.switchView(self.emptyTableView, self.viewExpGroup)
         except:
            pass
         
   def openOnDoubleClick(self,index):
      expId = index.model().data[index.row()][1]
      self._compareExpId(expId)
# ...........................................................................         
   def viewExeprimentInit(self,expId):
      
      """
      @summary: retrieves an experiment for the current exp action in the menu
      @param expId: experiment id
      """   
         
      experiment = self.getExperiment(expId) 
      if experiment is not None: 
         self._compareExpId(expId) 
         self.expId = expId   
         expDisplayName = experiment.model.occurrenceSet.displayName
         self.occId = experiment.model.occurrenceSet.id
         occMetadataUrl = experiment.model.occurrenceSet.metadataUrl
         expStatus = experiment.model.status
         if int(expStatus) >= JobStatus.GENERAL_ERROR:
            statusDisplay = 'error'
         elif int(expStatus) == JobStatus.RETRIEVE_COMPLETE:
            statusDisplay = STATUSLOOKUP[int(expStatus)]
         else:
            statusDisplay = "running"
         expAlgoCode = experiment.model.algorithmCode 
         try:
            self.projections = list(experiment.projections)
         except:
            self.projections = None
         self.displayName.setText(expDisplayName)
         self.status.setText(statusDisplay)
         self.algoCode.setText(expAlgoCode)
         self.occSetLink.setText('<a href="%s">Details</a>' % (occMetadataUrl))
         
         # hide table, and show self.viewExpGroup
         self.setWindowTitle("Experiment Details")
         
         self.viewExpGroup.show()
         self.backLink.hide()
         
# ...........................................................................    
   def viewExperiment(self,index):
      """
      @summary: retrieves an experiment
      @param index: index from the table view of the experiment to be retrieved [QModelIndex]
      """
      if index.column() in self.expTableView.tableModel.controlIndexes:
         expId = str(index.model().data[index.row()][1])
         experiment = self.getExperiment(expId) 
         if experiment is not None:  
            self.expId = expId
            self._compareExpId(expId)  # UNCOMMENT when in QGIS
            QgsProject.instance().emit( SIGNAL( "ActivateSDMExp(PyQt_PyObject)" ), expId)     
            expDisplayName = experiment.model.occurrenceSet.displayName
            self.occId = experiment.model.occurrenceSet.id
            occMetadataUrl = experiment.model.occurrenceSet.metadataUrl
            expStatus = experiment.model.status
            if int(expStatus) >= JobStatus.GENERAL_ERROR:
               statusDisplay = 'error'
            elif int(expStatus) == JobStatus.RETRIEVE_COMPLETE:
               statusDisplay = STATUSLOOKUP[int(expStatus)]
            else:
               statusDisplay = "running"
            expAlgoCode = experiment.model.algorithmCode 
            try:
               self.projections = list(experiment.projections)
            except:
               self.projections = None
            self.displayName.setText(expDisplayName)
            self.status.setText(statusDisplay)
            self.algoCode.setText(expAlgoCode)
            self.occSetLink.setText('<a href="%s">Details</a>' % (occMetadataUrl))
            
            # hide table, and show self.viewExpGroup
            self.setWindowTitle("Experiment Details")
            self.expTableView.hide()
            self.viewExpGroup.show()
# ...........................................................................      
   def addWMS(self, guid, id, tocName):
      """
      @summary: adds a wms layer to the qgis canvas
      @param guid: unique map prefix
      @param id: projection id [integer]
      @param tocName: name to present in the toc
      """
      layer = 'prj_'+str(id)      
      requestserviceversion = "&request=GetMap&service=WMS&version=1.1.0&"
      url = guid+requestserviceversion   
      layers = [layer]
      styles = [ '' ]
      format = 'image/png'
      crs = 'EPSG:4326'
      rlayer = QgsRasterLayer(0, url, tocName, 'wms', layers, styles, format, crs)
      if not rlayer.isValid():
         pass
      QgsMapLayerRegistry.instance().addMapLayer(rlayer)
# ...........................................................................
        
   def openFileDialog(self,defaultfilename,caption,filter,suffix):
      settings = QSettings()
      shpPath = settings.value( "/UI/lastShapefileDir" ).toString()
      if not os.path.exists(shpPath):
         shpPath = settings.value("UI/lastProjectDir").toString()     
      dirName = shpPath +"/"+defaultfilename.replace(' ','_')
      fileDialog = QgsEncodingFileDialog( self, caption, dirName,filter)
      fileDialog.setDefaultSuffix( QString(suffix) )
      fileDialog.setFileMode( QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )    
      if not fileDialog.exec_() == QFileDialog.Accepted:
         return ''
      filename = fileDialog.selectedFiles() 
      return str(filename.first())
# .............................................................................. 
   def addTiffToCanvas(self, path, tocName):
     
      fileInfo = QFileInfo(path)
      baseName = fileInfo.baseName()
      rasterLayer = QgsRasterLayer(path,tocName)  
      if not rasterLayer.isValid():
         QMessageBox.warning(self,"status: ",
           "not a valid layer")           
      else:
         lyrs = QgsMapLayerRegistry.instance().mapLayers()
         for id in lyrs.keys():
            if str(lyrs[id].name()) == tocName:
               QgsMapLayerRegistry.instance().removeMapLayer(id)
            
      
         QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)   
# ..............................................................................        
   def downLoadProjectionTiff(self, index):
      """
      @summary: called from viewDownloadProjection, gets projection id from the 
      table model, opens a file dialog to get a filename and calls getProjecctionTiff
      in the sdm client library
      @param index: index of item in table view [QModelIndex]
      """
      prjId = index.model().data[index.row()][1]
      scenName = index.model().data[index.row()][0]
      projName = index.model().data[index.row()][4]
      tocName = projName+"_"+scenName
      #filename = self.openFileDialog(projName,"Save .tif File","tif Files (*.tif)","tif")
      expFolder = self.workspace.getExpFolder(self.expId)
      if not expFolder:
         expFolder = self.workspace.createProjectFolder(self.expId)
      tifFile = projName+".tif"
      filename = os.path.join(expFolder,tifFile)
      if filename != '':
         try:
            self.client.sdm.getProjectionTiff(prjId,filename=filename)
         except Exception,e:
            QMessageBox.warning(self,"Error: ",
           "Problem with the Tiff service "+str(e)) 
         else:
            self.addTiffToCanvas(filename, tocName)
# ...........................................................................         
   def viewDownloadProjection(self, index):
      """
      @summary: connected to click signal on projections table, checks for status,
      and either adds a WMS or downloads and adds tiff
      @param index: index of item in table view [QModelIndex]
      """
     
      if index.model().data[index.row()][5] == str(JobStatus.RETRIEVE_COMPLETE):
         if index.column() in self.projsTable.tableModel.controlIndexes:
            if index.column() == 2:
               self.downLoadProjectionTiff(index)
                    
# ...........................................................................       
   def showEmptyTable(self, header, error):
      """
      @summary: shows an empty table with appropriate message
      """
      data = [[error]]
      self.emptyTable =  RADTable(data)
      headerList = [header]    
      self.emptyTableView = self.emptyTable.createTable(headerList)           
      self.tableGrid.addWidget(self.emptyTableView,1,1,1,1) 
# ........................................................................... 
   def showProjTable(self):
      success = self.buildProjsTable(self.projections)     
      if self.backOneLinkProj is None:
         self.backOneLinkProj = QLabel('<a href="www.fake.com">Back to experiment details</a>')
         QObject.connect(self.backOneLinkProj, SIGNAL("linkActivated(const QString &)"), self.switchtoExpViewFromProj)
         if not self.currentExp:
            self.backTwoLinkProj = QLabel('<a href="www.fake.com">Back to experiments</a>')       
            QObject.connect(self.backTwoLinkProj, SIGNAL("linkActivated(const QString &)"), self.switchtoExpTableFromProj)
            self.gridLayout.addWidget(self.backTwoLinkProj,8,0,1,1)
         self.tableGrid.addWidget(self.backOneLinkProj,2,0,1,2)
         
      else:
         self.backOneLinkProj.show()
         if not self.currentExp:
            self.backTwoLinkProj.show()
      self.setWindowTitle("Experiment Projections")
      if success:
         self.switchView(self.viewExpGroup, self.projsTableView)
      else:
         self.switchView(self.viewExpGroup, self.emptyTableView)
# ..........................................................................
   def clearOccSetColumns(self,layout):
     
      if layout is not None:
         while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
               widget.deleteLater()
            else:
               self.clearOccSetColumns(item.layout())
# ..........................................................................
   def downloadOccShape(self,occSetId):
      
      #filename = self.openFileDialog(str(occSetId), "save species points","zip files (*.zip)","zip")
      expFolder = self.workspace.getExpFolder(self.expId)
      if not expFolder:
         expFolder = self.workspace.createProjectFolder(self.expId)
      zipName = self.occSetDisplayName.replace(' ','_')
      filename = os.path.join(expFolder,zipName)
      if filename != '':
         try:
            self.client.sdm.getOccurrenceSetShapefile(occSetId,filename)
         except:
            QMessageBox.warning(self,"Error: ",
               "Problem with the shapefile service") 
         else:
            self.addToCanvas(filename)
      
# ..........................................................................      
   def addToCanvas(self,path):
     
      zippath = os.path.dirname(str(path))                         
      z = zipfile.ZipFile(str(path),'r')
      for name in z.namelist():
         f,e = os.path.splitext(name)
         if e == '.shp':
            shapename = name
         z.extract(name,str(zippath))
      vectorpath = os.path.join(zippath,shapename)
      vectorLayer = QgsVectorLayer(vectorpath,shapename.replace('.shp',''),'ogr')
      warningname = shapename    
      if not vectorLayer.isValid():
         QMessageBox.warning(self,"status: ",
           warningname)           
      else:
         lyrs = QgsMapLayerRegistry.instance().mapLayers()
         for id in lyrs.keys():
            if str(lyrs[id].name()) == shapename.replace('.shp',''):
               QgsMapLayerRegistry.instance().removeMapLayer(id)
            
      
         QgsMapLayerRegistry.instance().addMapLayer(vectorLayer)
# ...........................................................................
   def addToOccColumn(self,metadata, occSetId=None):
      if occSetId == None:
         metadataElement= QLabel(metadata)
         self.occMetaCol.addWidget(metadataElement)   
      else:
         hLayout = QHBoxLayout()
         hLayout.addWidget(QLabel(metadata))
         pointIcon = QIcon(":/plugins/lifemapperTools/icons/addPointLayer.png")
         downloadbutton = QPushButton(pointIcon,"")
         QObject.connect(downloadbutton, SIGNAL("clicked()"),lambda: self.downloadOccShape(occSetId))
         downloadbutton.setMaximumSize(26, 26)   
         hLayout.addWidget(downloadbutton)
         hLayout.addSpacing(350)
         self.occMetaCol.addLayout(hLayout)
# ...........................................................................
   def processOccSet(self):
      if self.hasOccMetadata:
         self.clearOccSetColumns(self.occMetaCol)
      occSet = self.getOccSet(self.occId)                
      if occSet is not None:
         self.occSetDisplayName = occSet.displayName 
         self.hasOccMetadata = True
         success = True
         if occSet.displayName is not None and occSet.displayName != '':
            self.addToOccColumn('Display Name:      %s' % (occSet.displayName))
         if occSet.id is not None and occSet.id != '':
            self.addToOccColumn('Occurrence Set Id:      %s' % (occSet.id))
            self.addToOccColumn('Download:     ',occSetId=occSet.id)
         if occSet.count is not None and occSet.count != '':
            self.addToOccColumn('Count:     %s' % (occSet.count))         
         if occSet.bbox is not None and occSet.bbox != '':
            bboxList = map(lambda x: x.replace('(','').replace(')',''), occSet.bbox.split(','))
            minX = '%.4f' % (float(bboxList[0]))
            minY = '%.4f' % (float(bboxList[1]))
            maxX = '%.4f' % (float(bboxList[2]))
            maxY = '%.4f' % (float(bboxList[3]))
            bbox = "(%s , %s , %s , %s)" % (minX,minY,maxX,maxY)
            self.addToOccColumn('BBOX:     %s' % (bbox)) 
         if occSet.epsgcode is not None and occSet.epsgcode != '':
            self.addToOccColumn('EPSG Code:      %s' % (occSet.epsgcode))
         if occSet.mapUnits is not None and occSet.mapUnits != '':
            self.addToOccColumn('Map Units:      %s' % (occSet.mapUnits))
      else:
         success = False
      self.backOneLinkOcc = QLabel('<a href="www.fake.com">Back to experiment details</a>')
      QObject.connect(self.backOneLinkOcc, SIGNAL("linkActivated(const QString &)"), self.switchtoExpViewFromOcc)
      if not self.currentExp:
         self.backTwoLinkOcc = QLabel('<a href="www.fake.com">Back to experiments</a>') 
         QObject.connect(self.backTwoLinkOcc, SIGNAL("linkActivated(const QString &)"), self.switchtoExpTableFromOcc)
      self.setWindowTitle("Experiment Species Points")
      if success:        
         self.switchView(self.viewExpGroup, self.viewOccSetGroup)
         self.occMetaCol.addWidget(self.backOneLinkOcc)
         if not self.currentExp:
            self.occMetaCol.addWidget(self.backTwoLinkOcc)
               

# ...........................................................................         
   def buildProjsTable(self, items):      
      if items is not None: 
         try:
            data = []
            for o in items:
               if int(o.status) == JobStatus.RETRIEVE_COMPLETE:
                  status = STATUSLOOKUP[int(o.status)]
                  download = "<a href='www.fake.fake'>download</a>"
               elif int(o.status) < JobStatus.GENERAL_ERROR:
                  status = "running"
                  download = 'not ready'
               if int(o.status) >= JobStatus.GENERAL_ERROR:
                  status = 'error' 
                  download = "unavailable"
               data.append([o.scenarioCode,o.id,download,status,o.title,o.status,o.mapPrefix])
            self.projsTable =  RADTable(data)
            header = ['  Scenario Code    ','Id','  Download    ','Status','','','']    
            self.projsTableView = self.projsTable.createTable(header,hiddencolumns=[4,5,6],
                                                              editsIndexList=[999],
                                                              controlsIndexList=[2],
                                                              htmlIndexList=[2]) 
            QObject.connect(self.projsTableView, SIGNAL("clicked(const QModelIndex &)"), self.viewDownloadProjection)                    
            self.tableGrid.addWidget(self.projsTableView,1,1,1,1)             
         except Exception, e:
            self.showEmptyTable('No Projections', '')
            return False
         else:
            return True
      else:
         self.showEmptyTable('ERROR','problem with projections for this experiment')  
         return False    
      

# ...........................................................................
   def getExpCount(self):
      try:
         count = self.client.sdm.countExperiments()
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
         desc = "A sample description, which I am trying to make fairly long to test the table"
         data = [[o.title,o.id,o.epsgcode,"<a href='%s'>details</a>"  % o.url, o.modTime,desc] for o in nextPage]
         self.expDataView.model().data = data
         self.expDataView.model().setCurrentPage(page)
         # consider just setting the model here against the data view using [view].setModel(model)
         self.expDataView.model().emit(SIGNAL('dataChanged(const QModelIndex &,const QModelIndex &)'),
               QModelIndex(), QModelIndex())

         readOut = "%s/%s" % (str(page+1),str(self.expTableView.noPages))
         self.expTableView.pageReadOut.setText(readOut)
         if page == self.expTableView.noPages - 1:
            self.expTableView.pageForward.setEnabled(False)
         if page == 0:
            self.expTableView.pageBack.setEnabled(False)
         if forward:
            self.expTableView.pageBack.setEnabled(True)
         else:
            self.expTableView.pageForward.setEnabled(True)
      else:
         message = "Could not get the next page"
         msgBox = QMessageBox.warning(self,
                                                  "Problem...",
                                                  message,
                                                  QMessageBox.Ok)
         
#   def showInfoPopUp(self,pos):
#      index = self.expDataView.indexAt(pos)
#      if index.column() == 5:
#         menu = QMenu()
#         descAtion = menu.addAction(index.model().data[index.row()][index.column()])
#         action = menu.exec_(QCursor.pos())
# ...........................................................................         
   def showExpTable(self, items):
      # maybe it needs to get the status too
      expCount = self.getExpCount()
      if items is not None: 
         try:
            if items == []:
               raise "no data"
            desc = "A sample description, which I am trying to make fairly long to test the table.  And here in another sentence to see what the length limit is on tool tips."
            data = [[o.title,o.id,o.epsgcode,"<a href='%s'>details</a>"  % o.url, o.modTime,desc] for o in items]
            self.expTableView =  RADTable(data,totalCount=expCount)
            
            header = ['Title', 'Id','EPSG','Details','Modified','Description']    
            self.expDataView = self.expTableView.createTable(header,editsIndexList=[999],
                                                    controlsIndexList=[3],
                                                    htmlIndexList=[3],toolTips=[5])
            QObject.connect(self.expDataView.model(),SIGNAL("getMore(PyQt_PyObject,PyQt_PyObject)"),self.getNextPage)
            if self.expDataView.model().noPages == 1:
               self.expTableView.pageForward.setEnabled(False)
            #self.expDataView.sortByColumn(2) only want to sort if not paginated, othewise rely on database ORDER BY
            QObject.connect(self.expDataView, SIGNAL("clicked(const QModelIndex &)"), self.viewExperiment)   
            QObject.connect(self.expDataView, SIGNAL("doubleClicked(const QModelIndex &)"), self.openOnDoubleClick)  
            #self.expDataView.setContextMenuPolicy(Qt.CustomContextMenu)
            #self.expDataView.customContextMenuRequested.connect(self.showInfoPopUp)     
            self.tableGrid.addWidget(self.expTableView,1,1,1,1) 
            
         except Exception, e:
            print str(e),"THIS IS THE ERROR"
            self.showEmptyTable('No Experiments', '')
            message = "There are no experiments for this user"
            msgBox = QMessageBox.warning(self,
                                                  "Problem...",
                                                  message,
                                                  QMessageBox.Ok)
      else:
         self.showEmptyTable('ERROR','problem with experiment listing service')
         
 
# ...........................................................................       
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(QStringList('documents'))
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('listSDMExperiments')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
             
if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   d = ListSDMExpDialog(None,client=client)#,experimentId=596106
   d.show()
   sys.exit(qApp.exec_())   
      
      
