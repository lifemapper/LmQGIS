import cPickle
import os
from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import * 
from lifemapperTools.common.lmHint import Hint, SpeciesSearchResult
from lifemapperTools.common.lmListModel import LmListModel


class ArchiveComboModel(LmListModel):
   
   
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
         if index.row() == 0 and self.model:
            return "[start typing]"  # this is taken care of against combo with placeholder text
         else:   
            try: 
               return self.listData[index.row()].taxaName
               #return self.listData[index.row()]
            except: 
               return #self.listData[index.row()]
           
      if index.isValid() and role == Qt.UserRole:
         return int(self.listData[index.row()])
      else:
         return 
      
   def updateList(self, newList):
      """
      @summary: Updates the contents of the list
      @param newList: A list of items to use for the new list
      @note: The provided list will replace the old list 
      """
      self.beginRemoveRows(QModelIndex(),0,len(self.listData)-1) # optional
      self.listData = [] # optional
      self.endRemoveRows() # optional
      
      self.beginInsertRows(QModelIndex(), 0, len(newList)-1) #just len makes auto with setIndex work better
      self.listData = newList
      self.endInsertRows()


class SpsSearchResult(object):
   
   """
   @summary: Data structure for species search results (Solr prj objects)
   """
   # .........................................
   def __init__(self, taxaName, species ):
      """
      @summary: Constructor for SpeciesSearchResult object
      @param displayName: The display name for the occurrence set
      @param occurrenceSetId: The Lifemapper occurrence set id
      @param numPoints: The number of points in the occurrence set
      """
      self.taxaName = taxaName
      self.species = species

   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      #return "%s (%s points)" % (self.displayName, self.numPoints)
      return "%s " % (self.taxaName)


class ArchiveHint(Hint):
   
   def __init__(self, client, callBack=None, setModel=True, data=[]):
      Hint.__init__(self, client, callBack=callBack, setModel=setModel)
      self.layers = data
      #self.combo = QComboBox()
      #self.combo.setEditable(True)
      
   def onTextChange(self, text):
      
      noChars = len(text)
      if text == '':  # never getting in here, callback vs. callBack
         self.combo.clear()
         self.combo.clearEditText()
         if self.callback is not None:
            self.callback('')
                  
      if noChars >= 3:
         #if text.count(" ") == 1:  
         #   return
         #if ' ' in text:
         #   text.replace(' ','%20')
         self.searchArchive(text)
         
   def searchArchive(self,searchText=''):
      """
      @summary: calls hint service
      @param    searchText: text to search for
      @todo:    needs a call back, probably set on init
      """
      #print "is this here?"
      # use toUnicode(searchText).encode('utf-8') for search
      try:                                         
         matches = [v for v in self.layers if v.taxaName.startswith(searchText)]    
      except Exception, e:
         print "except in searchArchive ",str(e)
      else:
         if len(matches) > 0:
            self.model.updateList(matches)  #this updates combo
            if self.callback is not None:
               self.callback(self.combo.currentText())  #this only updates listView



class Search(object):
   
   
   def hintBox(self, data=[]):
      
      """
      @summary: sets up the hint service and sets hint attribute
      combo can be added as a widget using self.hint.combo, callback
      adds extra functionality in addition to combo model
      """
      self.folderHint = ArchiveHint(None, callBack=self.callBack, setModel=False,data=data) #, serviceRoot=CURRENT_WEBSERVICES_ROOT
      archiveComboModel = ArchiveComboModel([],None)
      self.folderHint.model = archiveComboModel
      self.folderHint.combo.lineEdit().setPlaceholderText("[Start Typing]")
      self.folderHint.combo.setModel(archiveComboModel)
      self.folderHint.combo.setStyleSheet("""QComboBox::drop-down {width: 0px; border: none;} 
                                   QComboBox::down-arrow {image: url(noimg);}""")
      self.archiveListView()
      self.folderHint.layers = self.getTaxa()
      
      return self.folderHint,self.listView
   
   def callBack(self, currentItem):
      
      self.listView.clear()
      
      if str(currentItem) in self.taxa:
         for res in self.taxa[str(currentItem)]:
            QListWidgetItem(res, self.listView, QListWidgetItem.UserType)
   
   def archiveListView(self):
      
      self.listView = QListWidget()
      self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
      self.listView.setDragEnabled(True)
   
   def getTaxa(self):
      
      taxa = cPickle.load(open(os.path.join("/home/jcavner","taxaLookup.pkl")))
      self.taxa = taxa
      spsByTaxa = [SpsSearchResult(k,taxa[k]) for k in taxa.keys()]
      return spsByTaxa
   
class UserArchiveController(Search):
   
   pass
      