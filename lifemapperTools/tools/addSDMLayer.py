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
import time
import types
import sys
import zipfile
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from LmClient.lmClientLib import LMClient
from lifemapperTools.tools.ui_addSDMLayerDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import PER_PAGE                                         
from LmCommon.common.lmconstants import JobStatus

# .............................................................................

class UploadSDMDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   #__metaclass__ = classmaker()
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None, epsg=None,
                experimentname='',mapunits=None, resume=False):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process 
      """
      
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi(experimentname=experimentname)
      if resume:
         iface.addProject(resume)
      cc = self.rejectBut
      bok = self.acceptBut
      self.client = client
      self.algos = self.client.sdm.algos
      self.populateAlgoCombo()
      self.inputs = inputs  
      _Controller.__init__(self, iface, cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, outputfunc=None, 
                           requestfunc=None, client=client )
      self.publicscenarios = None
      self.userscenarios = None
      self.expEPSG = epsg
      if self.expEPSG != "4326":
         self.userRadio.setChecked(True)
         self.publicRadio.setEnabled(False)
      elif self.expEPSG == "4326":
         self.populateScenCombo(epsg=self.expEPSG,public=True)
      self.mapunits = mapunits
# ..............................................................................         
   def populateAlgoCombo(self):
      """
      @summary: populates the algorithm combo
      """
      self.AlgCodeCombo.addItem('All',userData='')
      for alg in self.algos:
         self.AlgCodeCombo.addItem(alg.name,userData=alg.code)
          
# ..............................................................................         
    
   def populateScenCombo(self,epsg=None,public=True):
      """
      @summary: populates the climate scenario combobox, with scenarios
      @param scenarios: list of scenario objects
      """
      
      try:
         if public:
            if self.publicscenarios is None:
               publicscenarios = self.client.sdm.listScenarios(public=public,epsgCode=self.expEPSG) 
               scenarios = publicscenarios
               self.publicscenarios = scenarios
            else:
               scenarios = self.publicscenarios
         else:
            if self.userscenarios is None:
               userscenarios = []
               publicscenarios = []
               userscenarios = self.client.sdm.listScenarios(public=False,epsgCode=epsg)
               if epsg == '4326':
                  publicscenarios = self.client.sdm.listScenarios(public=True,epsgCode=epsg)
               scenarios = userscenarios+publicscenarios
               self.userscenarios = scenarios
            else:
               scenarios = self.userscenarios
      except:
         message = "There is a problem with the scenario service"
         msgBox = QMessageBox.warning(self, "Problem...", message, QMessageBox.Ok)
         
      else:
         self.scenarioCombo.clear()
         self.scenarioCombo.addItem('All',userData='')
         for scen in scenarios:
            try:
               title = scen.title
            except:
               title = scen.id
            self.scenarioCombo.addItem(title,userData=scen.id)
         
         
# .............................................................................. 
   def checkUser(self,checked):
      if checked:
         self.populateScenCombo(epsg=self.expEPSG, public=False)
         self._clearReadOutPageButtons()
         self._clearTable()
      
# .............................................................................. 
   def checkPublic(self,checked):
      if checked:
         self.populateScenCombo(epsg=self.expEPSG,public=True)
         self._clearReadOutPageButtons()
         self._clearTable()
# ..............................................................................  

   def getProjectionCount(self,public,displayName,epsgCode,algorithmCode=None,scenarioId=None):
      try:
         count = self.client.sdm.countProjections(displayName=displayName, epsgCode=epsgCode, 
                                                  algorithmCode=algorithmCode, scenarioId=scenarioId, 
                                                  status=JobStatus.COMPLETE, public=public)
      except:
         count = 0
      return count
# ..............................................................................   
   def _clearReadOutPageButtons(self):
      """
      @summary: resets page readout to 1/1
      """
      readOut = "%s/%s" % ('1','1')
      self.table1.pageReadOut.setText(readOut)
      self.table1.pageBack.setEnabled(False)
      self.table1.pageForward.setEnabled(False)
# ..............................................................................      
   def getNextPage(self,currentPage,forward):
      """
      @summary: connected page forward to page back 
      @param currentPage: current page from the table model
      @param forward: direction to page
      """
      # expDataView = QTableView/ tableview1
      # expTableView = RADTable object/ table1
      if forward:
         page = currentPage + 1  
      else:
         page = currentPage - 1 
      data = []
      nextPage = self.listProjections(page=page)
      if nextPage is None:
         message = "Could not get the next page"
         msgBox = QMessageBox.warning(self, "Problem...", message, QMessageBox.Ok)
      else:
         #if archiveNextPage is not None:  
         for layer in nextPage:
            try:
               layername = layer.title
            except:
               layername = layer.id
            layerid = layer.id
            Alg = layer.algorithmCode
            Scen = layer.scenarioCode
            if self.publicRadio.isChecked():
               data.append([layername, layerid,"<a href='nothing'>view</a>",Alg,Scen,'PUBLIC'])
            if self.userRadio.isChecked():
               data.append([layername, layerid,"<a href='nothing'>view</a>",Alg,Scen,'USER'])
         
         self.tableview1.model().data = data
         self.tableview1.model().setCurrentPage(page)
         # consider just setting the model here against the data view using [view].setModel(model)
         #self.tableview1.model().emit(SIGNAL('dataChanged(const QModelIndex &,const QModelIndex &)'),
         #      QModelIndex(), QModelIndex())
         
         self.tableview1.model().dataChanged.emit(QModelIndex(),QModelIndex())
   
         readOut = "%s/%s" % (str(page+1),str(self.table1.noPages))
         self.table1.pageReadOut.setText(readOut)
         if page == self.table1.noPages - 1:
            self.table1.pageForward.setEnabled(False)
         if page == 0:
            self.table1.pageBack.setEnabled(False)
         if forward:
            self.table1.pageBack.setEnabled(True)
         else:
            self.table1.pageForward.setEnabled(True)
      
# ..............................................................................
   def listProjections(self,pageSize=PER_PAGE,page=0):
      """
      @summary: gets the next page of projections
      @param pageSize: number of records per page
      @param page: page number
      @return: list of Lm Layer objects, full
      """
      
      if self.publicRadio.isChecked(): 
         try:           
            layers = self.client.sdm.listProjections(displayName=self.displayname, perPage=pageSize,
                                               status=JobStatus.COMPLETE,public=True,
                                               scenarioId=self.Scen,algorithmCode=self.Alg,epsgCode=self.expEPSG,
                                               fullObjects=True,page=page) 
         except:
            layers = None 
      if self.userRadio.isChecked():
         try:              
            layers = self.client.sdm.listProjections(displayName=self.displayname, perPage=pageSize,
                                                  status=JobStatus.COMPLETE,public=False,
                                                  scenarioId=self.Scen,algorithmCode=self.Alg,epsgCode=self.expEPSG,
                                                  fullObjects=True,page=page)
         except:
            layers = None      
      return layers
# ..............................................................................
   def showInfoPopUp(self,pos): 
      try:
         index = self.tableview1.indexAt(pos)
         minVal = index.model().data[index.row()][6]
         maxVal = index.model().data[index.row()][7]
         nodataVal = index.model().data[index.row()][8]
         resolution = index.model().data[index.row()][9]
         menu = QMenu() 
         minAction = menu.addAction("minVal: %s" % (minVal)) 
         maxAction = menu.addAction("maxVal: %s" % (maxVal)) 
         nodataAction = menu.addAction("no data val: %s"% (nodataVal)) 
         resAction = menu.addAction("resolution: %s" % (resolution))
         action = menu.exec_(QCursor.pos())
      except:
         pass          
# ..............................................................................         
       
   def searchSpecies(self):
      """
      @summary: lists projections by display name, scen, and alg, needs to filter on 
      epsg and use both public and user, which means two requests. Sets to modeless
      so user can view wms of resulting projections.
      """
      self.setModal(False)
      if self.searchText.text() == '' and self.publicRadio.isChecked():
         QMessageBox.warning(self,"problem: ",
                         "Please enter a species name, partial names will return all species that match") 
      else:
         
         self._clearTable()
         self._clearReadOutPageButtons()
         currentAlidx = self.AlgCodeCombo.currentIndex()
         currentScenidx = self.scenarioCombo.currentIndex()
         self.Alg = self.AlgCodeCombo.itemData(currentAlidx, role=Qt.UserRole)
         if self.Alg == '':
            self.Alg = None         
         self.Scen = self.scenarioCombo.itemData(currentScenidx, role=Qt.UserRole)
         if self.Scen == '':
            self.Scen = None
         self.displayname = self.searchText.text()
         archiveLayers = []
         userLayers = []
         if self.publicRadio.isChecked():
            try:
               count = self.getProjectionCount(True, self.displayname, self.expEPSG, algorithmCode=self.Alg, scenarioId=self.Scen)  
               archiveLayers = self.client.sdm.listProjections(displayName=self.displayname, perPage=PER_PAGE,
                                                     status=JobStatus.COMPLETE,public=True,
                                                     scenarioId=self.Scen,algorithmCode=self.Alg,epsgCode=self.expEPSG,
                                                     fullObjects=True)
            except:
               message = "problem with the projection services"
               msgBox = QMessageBox.warning(self, "Problem...", message, QMessageBox.Ok)
               return
         if self.userRadio.isChecked():
            if self.displayname == '':
               self.diplayname = None
            try:  
               count = self.getProjectionCount(False, self.displayname, self.expEPSG, algorithmCode=self.Alg, scenarioId=self.Scen)      
               userLayers = self.client.sdm.listProjections(displayName=self.displayname, perPage=PER_PAGE,
                                                  status=JobStatus.COMPLETE,public=False,
                                                  scenarioId=self.Scen,algorithmCode=self.Alg,epsgCode=self.expEPSG,
                                                  fullObjects=True)
            except:
               message = "problem with the projection services"
               msgBox = QMessageBox.warning(self, "Problem...", message, QMessageBox.Ok)
               return
         self.projectionCount = count
         layers = archiveLayers + userLayers
         if len(layers) > 0:
            if len(archiveLayers) > 0:
               
               self.addLayersToResultsTable(archiveLayers,userLayers=False)
            if len(userLayers) > 0:
               self.addLayersToResultsTable(userLayers,userLayers=True)
         else:
            QMessageBox.warning(self,"Info: ",
                         "No Species Models match your query parameters ") 
         #self.populateTree(layers)
# ..............................................................................         
    
   def _clearTable(self):
      """
      @summary: clears the contents of the search results table
      """
      layercount = len(self.table1.tableView.model().data)
      data = [record for record in self.table1.tableView.model().data]
      emptyrow = ['' for x in range(0,len(self.table1.tableView.model().data[0]))]
      if not(self.table1.tableView.model().data[0]) == emptyrow:
         for idx in range(0,layercount-1):
               self.table1.tableView.model().removeRow(data[idx])
         self.table1.tableView.model().data[0] = emptyrow
# ..............................................................................         
    
   def checkNames(self):
      renameList = []
      idList = []
      for record in enumerate(self.table2.tableView.model().data):
         name = str(record[1][0])
         try:
            layerCount = self.client.rad.countLayers(layerName=name,epsgCode=self.expEPSG)
         except Exception, e:
            message = "can't count layers, uploading layers may not work %s" % (str(e))
            QMessageBox.warning(self,"status: ", message)
         else:
            if layerCount > 0:
               try:
                  layer = self.client.rad.listLayers(layerName=name,epsgCode=self.expEPSG)
               except Exception, e:
                  message = "can't retrieve duplicate layer's id, uploading layers may not work %s" % (str(e))
                  QMessageBox.warning(self,"status: ", message)
               else:
                  renameList.append(name)
                  idList.append(layer[0].id)
      return renameList, idList
   
# ..............................................................................         
    
   def checkForEmpties(self):
      for record in self.tableview2.model().data:
         for field in record:
            if field == '' :
               return True
      return False 
# ..............................................................................         
    
   def addUpload(self, names, ids, record, skipUpload=False):
      #self.progressbar.reset()
      if not skipUpload:  
         upload = False  
         try:            
            if record[1][6] == 'PUBLIC':
               postresponse = self.client.rad.postRaster(**{'layerUrl':record[1][1],
                                               'name':record[1][0],
                                               'epsgCode':self.expEPSG,
                                               'mapUnits':self.mapunits})
            elif record[1][6] == 'USER':
               prjId = int(record[1][7])
               tiffStream = self.client.sdm.getProjectionTiff(prjId)
               postresponse = self.client.rad.postRaster(**{'layerContent':tiffStream,
                                               'name':record[1][0],
                                               'epsgCode':self.expEPSG,
                                               'mapUnits':self.mapunits})
         except Exception,e:
            message = 'Could not upload layer %s' % (str(record[1][0]))
            QMessageBox.warning(self,"status: ", message)
         else:
            layerId = postresponse.id
            upload = True
      else:
         index = names.index(record[1][0])
         layerId = ids[index]
         upload = True
      addresponse = False   
      try:   
         inputs = {'attrPresence':record[1][2],'minPresence':record[1][3],
                   'maxPresence':record[1][4], 'percentPresence':record[1][5]}
         # this adds the expId
         inputs.update(self.inputs) 
         inputs.update({'lyrId':layerId}) 
         addresponse = self.client.rad.addPALayer(**inputs)
         
      except:
         message = 'Could not add layer %s to experiment' % (str(record[1][0]))
         QMessageBox.warning(self,"status: ", message)
         success = False
      else:
         if upload and addresponse:
            success = True
         else:
            success = False                                                  
      #self.progressbar.setValue(100)
      #time.sleep(.28)
      return success
# ..............................................................................         
    
   def removeRows(self, successrecords, layercount, successcount):
      
      if layercount == successcount:
         # number of times to go through loop is layercount-1, because we don't want to remove the 
         # last record
         for i in range(0,layercount-1):
            self.table2.tableView.model().removeRow(successrecords[i][1])
         emptyrow = ['' for x in range(0,len(self.table2.tableView.model().data[0]))]
         self.table2.tableView.model().data[0] = emptyrow
               
      elif successcount < layercount:
         # number of times to go through loop is everything in successrecords
         for oldrecord in successrecords:              
            self.table2.tableView.model().removeRow(oldrecord[1])   
      
   
# ..............................................................................         
          
   def accept(self):
      empties = self.checkForEmpties()
      if empties:
         message = "There are empty fields in your data"
         QMessageBox.information(self,"error: ", message)
         return
      layercount = len(self.table2.tableView.model().data)
      if layercount == 1 and self.table2.tableView.model().data[0][0] == '':
         message = "No layers to upload"
         QMessageBox.warning(self,"status: ", message)
      else:
         #self.setAllGroup.hide()      
         #self.statuslabel.setText('Uploading') 
         self.outputGroup.setTitle('Outputs')
         self.outputGroup.show()
         names, ids = self.checkNames()    
         successcount = 0
         addedAndUploadedrecords = []
         self.progressbar.reset()
         self.progressbar.setMinimum(0)
         self.progressbar.setMaximum(layercount)
         for record in enumerate(self.table2.tableView.model().data):
            if record[1][0] not in names:
               if self.addUpload(names, ids, record, skipUpload=False):
                  addedAndUploadedrecords.append(record)
                  successcount += 1
               self.progressbar.setValue(record[0]+1)
         self.removeRows(addedAndUploadedrecords,layercount,successcount)            
         if successcount == layercount: 
            self.acceptBut.setEnabled(False)
         message = 'Uploaded and Added '+str(successcount) +" of "+ str(layercount) +" layers"
         QMessageBox.information(self,"status: ", message)
         
         if len(names) > 0:
            namesString = ''
            for layer in names:
               namesString = namesString + layer + '\n'
            namesString = ''
            message =  """Some layers already exist by name for this user,
                       if you wish to upload again click No on this dialog, rename
                       the remaining layers and submit again, or click Yes to skip
                       uploading the actual data and just add the existing data for
                       these layers to the current experiment with the new parameters.""" + namesString
            #
            reply = QMessageBox.question(self, 'Layers exist',
                                                  message, QMessageBox.Yes | 
                                                  QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
               successcount = 0
               layercount = len(self.table2.tableView.model().data)
               addedrecords = []
               self.progressbar.reset()
               self.progressbar.setMinimum(0)
               self.progressbar.setMaximum(layercount)
               for record in enumerate(self.table2.tableView.model().data):
                  if record[1][0] in names:
                     if self.addUpload(names, ids, record, skipUpload=True):
                        addedrecords.append(record)
                        successcount += 1  
                  self.progressbar.setValue(record[0]+1)             
               self.removeRows(addedrecords,layercount,successcount)
               self.acceptBut.setEnabled(False)
               message = 'Added %s of %s layers' % (str(successcount),str(layercount))
               QMessageBox.information(self,"status: ", message)
         self.outputGroup.hide()
            
# ..............................................................................         
             
   def populateTree(self, species):
      selected = None
      self.treeWidget.clear()
      self.treeWidget.setColumnCount(2)
      self.treeWidget.setHeaderLabels(["Species/Scenario/Algorithm", "Preview"])
      self.treeWidget.setItemsExpandable(True)
      for critter in species:
         ancestor = QTreeWidgetItem(self.treeWidget, [critter.title])
         for scenario in ['A1B1','B1','B2']:
            scenario = QTreeWidgetItem(ancestor, [scenario])
            for proj in ['proj1','proj2','proj3']:
               # this will really next to list projection for each scenario
               preview = "<a href='nothing'>view</a>"
               proj = QTreeWidgetItem(scenario, [proj, preview])
               
         
  
# ..............................................................................         
          
   def getGuid(self,projid):
      try:
         projObj = self.client.sdm.getProjection(projid) 
         
         guid = self.client.sdm.getOgcEndpoint(projObj)
        
      except Exception, e:
         guid = None
      return guid
# ..............................................................................         
        
   def addWMS(self,index):
      
      if index.column() in self.table1.tableModel.controlIndexes and \
      not(index.model().data[index.row()][index.column()] == ''):  
               
         projid = index.model().data[index.row()][1] 
         
         guid = self.getGuid(projid)
         print "GUID ",guid
         if guid is not None:
                                     
            try:
               params = []
        
               requestserviceversion = "request=GetMap&service=WMS&version=1.1.0&TRANSPARENT=true"
               params.append(requestserviceversion)
               ################
               # section for new key values
               #######################
               urlWithLyrs = guid.replace("&amp;","&")   # this should have the GetMap behind the ?, replacing
               # encoding for &amp, since this is a string now, it will also have the layers key/value pair
               url = urlWithLyrs.split('&')[0]
               params.append("url="+url)
               
               lyrs = urlWithLyrs.split('&')[1]
               params.append(lyrs)
               
               imgformat = 'format=image/png'
               params.append(imgformat)
               
               crs = 'crs=EPSG:%s' % self.expEPSG
               params.append(crs)
               
               styles = 'styles=default'  # need to see if this is plural or singular???
               params.append(styles)
               
               basename = lyrs.split("=")[1]
               # # !!!!! CHECK HERE http://lists.osgeo.org/pipermail/qgis-developer/2013-October/028756.html
               
               url = '&'.join(params)
            except:
               # try new style 
               # "http://sporks.nhm.ku.edu/services/sdm/projections/702191/ogc?layers=prj_702191&request=GetMap&version=1.1.0&service=WMS&srs=EPSG:4326&TRANSPARENT=true&format=image/png&srs=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=-400&HEIGHT=400"            
               # guid should be http://sporks.nhm.ku.edu/services/sdm/projections/702191/ogc?layers=prj_702191
               if 'projections' in guid:
                  try:
                     params = [] 
                     requestserviceversion = "request=GetMap&service=WMS&version=1.1.0&TRANSPARENT=true"
                     params.append(requestserviceversion) 
                     params.append("url=%s" % (guid.split("?")[0]))     
                     lyrs = guid.split('?')[1]
                     params.append(lyrs) 
                     imgformat = 'format=image/png'
                     params.append(imgformat) 
                     crs = 'crs=EPSG:%s' % self.expEPSG
                     params.append(crs)               
                     styles = 'styles=default'  # need to see if this is plural or singular???
                     params.append(styles)
                     basename = lyrs.split("=")[1] 
                     url = '&'.join(params)
                  except:
                     url = ''
                     basname = ''
               else:
                  # punt
                  url = ''
                  basename = ''
            
            try:
               rlayer = QgsRasterLayer(url, basename,'wms')
               if not rlayer.isValid():
                  pass
               QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            except Exception,e:
               print str(e)
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
      helpDialog.scrollToAnchor('addSDMLayer')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show() 
      
if __name__ == "__main__":
#  
   client =  LMClient(userId='blank', pwd='blank')
   qApp = QApplication(sys.argv)
   d = UploadSDMDialog(None, inputs={'expId':447}, client=client, epsg='4326',
                       experimentname='',mapunits='dd')
   d.show()
   sys.exit(qApp.exec_())
         
      