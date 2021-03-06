import os, sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.common.lmListModel import LmListModel, EnterTextEventHandler


def toUnicode(value, encoding='utf-8'):
   """
   @summary: Encodes a value for a element's text
   @param value: The object to make text
   @param encoding: (optional) The encoding of the text
   @todo: Encoding should be a constant
   """
   if isinstance(value, basestring):
      if not isinstance(value, unicode):
         value = unicode(value, encoding)
   else:
      value = unicode(str(value), encoding)
   return value
      
def fromUnicode(uItem, encoding="utf-8"):
   """
   @summary: Converts a unicode string to text for display
   @param uItem: A unicode object
   @param encoding: (optional) The encoding to use
   """
   return uItem.encode("utf-8")

class LmCombo(QComboBox):
   # maybe init was causing seg fault
   #def __init__(self, hit):
   #   
   #   self.hit = hit
   #   QComboBox.__init__(self)
      
   def showPopup(self, *args, **kwargs):
      return None

class HintModel(LmListModel):
   
   def __init__(self,data,parent):
      
      LmListModel.__init__(self, data, parent = parent)
   
   def data(self, index, role):
      """
      @summary: Gets data at the selected index
      @param index: The index to return
      @param role: The role of the item
      @return: The requested item
      @rtype: QtCore.QVariant
      """
      if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
         if index.row() == 1 and self.model:
            return "build new model"
         else:   
            try: return self.listData[index.row()].customData()
            except: return self.listData[index.row()]
           
      if index.isValid() and role == Qt.UserRole:
         return int(self.listData[index.row()])
      else:
         return 

class Hint:
   
   def __init__(self, client , parent = None, callBack = None, setModel=True, serviceRoot="http://svc.lifemapper.org"):
      
      self.client = client
      
      # need to initialize a LmListModel
      self.serviceRoot = serviceRoot
      self.parent = parent
      self.model = None
      self.namedTuples = None
      ######## combo #######
      self.combo = LmCombo()
      #self.combo = QLineEdit()
      #self.combo.setStyleSheet("""QComboBox::drop-down {width: 0px; border: none;} 
      #                           QComboBox::down-arrow {image: url(noimg);}""")
      self.combo.setAutoCompletion(True)
      self.combo.setEditable(True)
      
      if setModel:
         self.model = HintModel([],parent)
         self.combo.setModel(self.model)
      
      ######### QLineEdit with Completer ###############
      #self.combo = QLineEdit()
      #self.completer = QCompleter()
      #self.completer.setModel(self.model)
      #self.combo.setCompleter(self.completer)
      self.callback = callBack
      
      #self.combo.textChanged.connect(self.onTextChange) # linux, mac
      self.combo.editTextChanged.connect(self.onTextChange)  # windows
   
      
   
   def searchOccSets(self,searchText=''):
      """
      @summary: calls hint service
      @param    searchText: text to search for
      @todo:    needs a call back, probably set on init
      """
      root = self.serviceRoot
      try:
         #self.namedTuples = self.client.sdm.hint(toUnicode(searchText).encode('utf-8'),
         #                                        maxReturned=60,serviceRoot=root)   
         self.namedTuples = self.client.sdm.searchArchive(toUnicode(searchText).encode('utf-8'))    
      except Exception, e:
         #print "or is throwing except ", e 
         pass
      else:
         items = []
         if self.namedTuples is not None:
            if len(self.namedTuples) > 0:
               for species in self.namedTuples:
                  
                  items.append(SpeciesSearchResult(species.displayName,species.occurrenceSetId,
                                                   numPoints=species.numPoints,models=species.models
                                                   )) 
                  # species.name,species.id, downloadUrl=species.downloadUrl, numModels=species.numModels
            else:  # added this Sept. 29
               items.append(SpeciesSearchResult('', '', '',''))
         else:  
            items.append(SpeciesSearchResult('', '', '',''))
            
         self.model.updateList(items) #uncomment when gong back to combo from lineEdit
         if self.callback is not None:
            self.callback(items)
         
         
   def getIdxFromTuples(self,currentText):
      """
      @summary: gets index of chosen item from combo box after results returned from callback
      """
      idx = 0
      if self.namedTuples is not None:
         for sH in self.namedTuples: 
            # probably will need to change this inside of Qgis        
            #if sH.name.lower() in unicode(currentText).lower():
            #if sH.name.lower() in currentText.lower():
            if sH.displayName.lower() in currentText.lower():
               break
            idx += 1         
      return idx
   
   def onTextChange_try(self, text): # no set index, would work for lineEdit too, try with model indexes (beginRemove (-1)
      
      noChars = len(text)
      if noChars >= 3:
         if text.count(" ") == 1:
            # just rely on built-in autocompleter on combo
            return
         if ' ' in text:
               text.replace(' ','%20')
         self.searchOccSets(text)
   

   def onTextChange(self, text):
      """
      @summary: stock handler for text change
      @param text: string from search box, usually a modified combo box
      """
      noChars = len(text)
      if text == '':
         self.combo.clear()
         self.combo.clearEditText()
         if self.callback is not None:
            self.callback([SpeciesSearchResult('', '', '','','')])
            
            
      if noChars >= 3:
         
         if text.count(" ") == 1:
            currText = self.combo.currentText()
            idx = self.getIdxFromTuples(currText)
            self.combo.setCurrentIndex(idx) 
            return
         if ' ' in text:
            text.replace(' ','%20')
         self.searchOccSets(text)
         
class SolrSearchResult(object): # deprecated
   """
   @summary: Data structure for species search results (occurrence sets)
   """
   # .........................................
   def __init__(self, displayName, occObj, models):
      
      self.displayName = displayName
      self.occurrenceSetId = occObj.id  
      self.numPoints = occObj.numPoints
      self.models = models
      
   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      return "%s (%s points)" % (self.displayName, self.numPoints)
   

class SpeciesSearchResult(object):
   """
   @summary: Data structure for species search results (Solr prj objects)
   """
   # .........................................
   def __init__(self, displayName, occurrenceSetId, numPoints=None, 
                numModels=None, downloadUrl=None,models=None):
      """
      @summary: Constructor for SpeciesSearchResult object
      @param displayName: The display name for the occurrence set
      @param occurrenceSetId: The Lifemapper occurrence set id
      @param numPoints: The number of points in the occurrence set
      """
      self.displayName = displayName
      self.occurrenceSetId = occurrenceSetId
      self.numPoints = numPoints
      self.numModels = numModels
      self.downloadUrl = downloadUrl
      self.models = models

   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      return "%s (%s points)" % (self.displayName, self.numPoints)
   
   
