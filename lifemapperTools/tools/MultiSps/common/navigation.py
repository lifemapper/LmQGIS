from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.common.LmQTree import BrowserTreeModel, TreeItem

class NavTreeView(QTreeView):   
   
   def __init__(self, client ,tmpDir = None, parent=None, dialog=None, workspace=None):
         
      QTreeView.__init__(self,parent)
      
      
      self.setRootIsDecorated(True)
      
      self.header().hide()
      self.doubleClicked.connect(self.handleEvent)
      #self.dragEnabled()
      #self.setDragDropMode(QAbstractItemView.DragOnly)
      self.header().setResizeMode(QHeaderView.ResizeToContents)
         
   def handleEvent(self, index):
      
      print "in folder event"
      # will need to get type
      #try:
      childRowIdx = index.row()
      itemData = self.model().nodeFromIndex(index.parent()).child(childRowIdx).itemData
      
   def getDataFromDoubleClick(self, itemIdx):
      """
      @summary: gets data from tree model from selection in view
      """
      
      childRowIdx = itemIdx.row()
      data = self.model().nodeFromIndex(itemIdx.parent()).child(childRowIdx).itemData 
      
      
class NavTreeModel(BrowserTreeModel):
   
   def __init__(self,top='Top'):
      BrowserTreeModel.__init__(self,top=top)
      
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
         
   def flags(self, index):
      defaultFlags = QAbstractItemModel.flags(self, index)
      if not self.hasChildren(index):
         #return Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable
         return Qt.ItemIsEnabled | Qt.ItemIsSelectable
      return defaultFlags
         