from PyQt4.QtGui import *
from PyQt4.QtCore import *

class BrowserTreeModel(QAbstractItemModel):
   """
   @summary: Folder/Browser model for QT tree data model
   """
   def __init__(self,top='Archive'):
      """
      @summary: constructor
      @param top: top element string
      """
      QAbstractItemModel.__init__(self)
      self.headers = ['','','']
      self.columns = 3
      self.root = TreeItem("Root", "Root", parent = None)
      self.provider = TreeItem(top,top,self.root)
      
   
   # ----------  change data
   def emitDataChanged(self):
      # deprecated
      self.dataChanged.emit(QModelIndex(), QModelIndex())
      
   def insertRow(self, row, parent):
      return self.insertRows(row, 1, parent)


   def insertRows(self, row, count, parent):
      try:
         self.beginInsertRows(parent, row, (row + (count - 1)))
         self.endInsertRows()
      except:
         print "in insert rows"
      return True


   def removeRow(self, row, parentIndex):
      return self.removeRows(row, 1, parentIndex)


   def removeRows(self, row, count, parentIndex):
      
      self.beginRemoveRows(parentIndex, row, row)
      node = self.nodeFromIndex(parentIndex)
      node.removeChild(row)
      self.endRemoveRows()
   
      return True
   # ----------  end change data
   
   # ---------- new update data, Sept 14, 2015
   def updateList(self,newList): #deprecated
      
      self.beginInsertRows(QModelIndex(), 0, len(newList))
      self.data = newList
      self.endInsertRows()   
      
   # -----------
   
   def headerData(self, section, orientation, role):
      if orientation == Qt.Horizontal and role == Qt.DisplayRole:
         return self.headers[section]
      return 
   
   def flags(self, index):
      defaultFlags = QAbstractItemModel.flags(self, index)
      if not self.hasChildren(index):
         #return Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable
      return defaultFlags
   
   def index(self, row, column, parentIndex):
      node = self.nodeFromIndex(parentIndex)
      return self.createIndex(row, column, node.child(row))
   
   def nodeFromIndex(self, index):
      
      return index.internalPointer() if index.isValid() else self.root
   
   def parent(self, child):
      # get parent from child index
      if not child.isValid():
         return QModelIndex()
      
      node = self.nodeFromIndex(child)
      
      if node is None:
         return QModelIndex()
      try:
         parent = node.parent
      except:
         return QModelIndex()
         
      if parent is None:
         return QModelIndex()
      
      
      grandparent = parent.parent  # attribute on item instance
      if grandparent is None:
         return QModelIndex()
      row = grandparent.rowOfChild(parent)
      
      if row != - 1:  #  
         return self.createIndex(row, 0, parent)
      else:
         return QModelIndex()
      
      #if not index.isValid():
      #      return QModelIndex()
      #
      #childItem = index.internalPointer()
      #parentItem = childItem.parent()
      #
      #if parentItem == self.rootItem:
      #   return QtCore.QModelIndex()
      #
      #return self.createIndex(parentItem.row(), 0, parentItem)
   
   def columnCount(self, parent):
      return self.columns


   def rowCount(self, parent):
      node = self.nodeFromIndex(parent)
      if node is None:
         print "Returning 0 in rowCount in Tree model"
         return 0
      try:
         return len(node)
      except:
         return 0
   
   def data(self, index, role):
      
      if role == Qt.DecorationRole:
         
         return 
             
      if role == Qt.TextAlignmentRole:
         return int(Qt.AlignTop | Qt.AlignLeft)
      
      if role != Qt.DisplayRole:
         return 
      
              
      node = self.nodeFromIndex(index)
      #
      if index.column() == 0:
      
         try:
            return node.name
         except Exception, e:
            # might just want to return an empty sting here
            return 
      


class TreeItem(object):
   
   # --- class for tree items
   
   def __init__(self, data, name, parent=None, hit=None, type=None):
      
      self.name = name
      self.parentItem = parent
      self.itemData = data  # this usually means an id
      self.type = type
      self.childItems = []
      self.setParent(parent)
      self.hit = hit
   # ..........................................   
   def setParent(self, parent):
      if parent != None:
         self.parent = parent
         self.parent.appendChild(self)
      else:
         self.parent = None
   # ..........................................   
   def appendChild(self, item):
      self.childItems.append(item)
   
   # ---------- from, http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/itemviews/simpletreemodel/simpletreemodel.py
   def child(self, row):
      # get called from index() in model
      try:
         return self.childItems[row]
      except Exception, e:
         #print "exception in child in TreeItem ",str(e)
         pass
   # ..........................................
   def childCount(self):
      return len(self.childItems)
   
   def data(self, column):
      # not using this, doesn't need it for single data
      # attached to instance of item
      try:
         return self.itemData[column]  # not a list, but could be
      #except IndexError:
      except Exception, e:
         print "returning None from data in TreeItem ",str(e)
         return None
   
   def getParent(self):  # changed this because "parent" was both a method and attribute
      return self.parentItem
   
   def row(self):
      if self.parentItem:
         return self.parentItem.childItems.index(self)   
      print "returning zero from row in TreeItem"
      return 0
   # ---------------- end 
   
   def childAtRow(self, row):
      # !!!!!!! same as child
      return self.childItems[row]
   
   def rowOfChild(self, child):       
      for i, item in enumerate(self.childItems):
         if item == child:
               return i
      print "returning -1 from rowOfChild (Tree Item)"
      return -1
   
   def removeChild(self, row):
      try:
         value = self.childItems[row]
         self.childItems.remove(value)
      except Exception, e:
         print "in removeChild (Tree Item) except ",str(e)
         pass
   
   def __len__(self):
      return len(self.childItems)