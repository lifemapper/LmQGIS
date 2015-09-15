import os, sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.common.lmListModel import LmListModel, EnterTextEventHandler
from lifemapperTools.tools.radTable import RADTableModel


class TableModel(RADTableModel):
   
   def __init__(self,model,headers):
      
      RADTableModel.__init__(self, model,headers,[],[])



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
   # subclassed this to override pop up
   def __init__(self):
      
      QComboBox.__init__(self)
      
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
   
   def __init__(self, client , parent = None, callBack = None):
      
      self.client = client
      # need to initialize a LmListModel
      self.parent = parent
      self.model = HintModel([],parent)
      
      ######## combo #######
      self.combo = LmCombo()
      self.combo.setStyleSheet("""QComboBox::drop-down {width: 0px; border: none;} 
                                 QComboBox::down-arrow {image: url(noimg);}""")
      self.combo.setAutoCompletion(True)
      self.combo.setEditable(True)
      self.combo.setModel(self.model)
      
      ######### QLineEdit with Completer ###############
      #self.combo = QLineEdit()
      #self.completer = QCompleter()
      #self.completer.setModel(self.model)
      #self.combo.setCompleter(self.completer)
      self.callback = callBack
      
      self.combo.textChanged.connect(self.onTextChange)
      
   
   def searchOccSets(self,searchText=''):
      """
      @summary: calls hint service
      @param    searchText: text to search for
      @todo:    needs a call back, probably set on init
      """
      try:
         self.namedTuples = self.client.sdm.hint(searchText,maxReturned=60)         
      except Exception, e:
         print "or is throwing except ",str(e) 
      else:
         items = []
         tableItems = []
         if len(self.namedTuples) > 0:
            for species in self.namedTuples:
               items.append(SpeciesSearchResult(species.name,species.id,
                                                numPoints=species.numPoints, numModels=species.numModels))
         else:
            items.append(SpeciesSearchResult('', '', '',''))
         self.model.updateList(items)
         if self.callback is not None:
            self.callback(items)
         
         
   def getIdxFromTuples(self,currentText):
      
      idx = 0
      for sH in self.namedTuples: 
         # probably will need to change this inside of Qgis        
         if sH.name.lower() in unicode(currentText).lower():
            break
         idx += 1         
      return idx
   
   def onTextChange(self, text):

      #displayName = self.searchText.text()
      
      noChars = len(text)
      # %20
      #occurrenceSetId = None
      if text == '':
         self.combo.clear()
         if self.callback is not None:
            self.callback([SpeciesSearchResult('', '', '','',)])
      if noChars >= 3:
         if  "points)" in text:
           
            currText = self.combo.currentText()
            idx = self.getIdxFromTuples(currText)
            self.combo.setCurrentIndex(idx) 
            #currentIdx = self.combo.currentIndex()                       
            #occurrenceSetId = self.model.listData[currentIdx].occurrenceSetId
            #displayName = self.model.listData[currentIdx].displayName
            
            return
         if ' ' in text:
            text.replace(' ','%20')
        
         self.searchOccSets(text)

class SpeciesSearchResult(object):
   """
   @summary: Data structure for species search results (occurrence sets)
   """
   # .........................................
   def __init__(self, displayName, occurrenceSetId, numPoints=None, numModels=None):
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

   # .........................................
   def customData(self):
      """
      @summary: Creates a string representation of the SpeciesSearchResult 
                   object
      """
      
      return "%s (%s points)" % (self.displayName, self.numPoints)
   
   
