from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lifemapperTools.common.LmQTree import BrowserTreeModel, TreeItem



class NavigationListItem(QListWidgetItem):
   
   def __init__(self,result,parent,reds=[],blues=[],rowIdx=0,page=None):
      QListWidgetItem.__init__(self,result[0],parent,QListWidgetItem.UserType)
      
      
      self.page = result[1]
      #if self.pathId in reds:
      #   self.setBackground(Qt.red) # sets red backdround
      #   #parent.setItemDelegateForRow(rowIdx,SelectedDelegate(Qt.red))  # doesn't work right now
      #if self.pathId in blues:
      #   self.setBackground(Qt.cyan)

class NavTreeItem(TreeItem):
   
   def __init__(self, data, name, parent=None, type = None,page=None,stackedWidget=None,hide=None,open=None):
      TreeItem.__init__(self, data,name,parent=parent)
      self.page = page
      self.type = type
      self.hide = hide
      self.open = open
      

class NavTreeView(QTreeView):   
   
   def __init__(self, client ,tmpDir = None, parent=None, dialog=None, workspace=None,stackedWidget=None):
         
      QTreeView.__init__(self,parent)
      
      self.stackedWidget = stackedWidget
      self.setRootIsDecorated(True)
      
      self.header().hide()
      self.doubleClicked.connect(self.handleEvent)
      #self.dragEnabled()
      #self.setDragDropMode(QAbstractItemView.DragOnly)
      self.header().setResizeMode(QHeaderView.ResizeToContents)
         
   def handleEvent(self, index):
      
      #pass
      #print "in folder event"
      ## will need to get type
      self.stackedWidget.setCurrentWidget(self.model().nodeFromIndex(index).page)
      #hide = self.model().nodeFromIndex(index).hide
      #print "hide ",hide
      #if hide is not None:
      #   for h in hide:
      #      print h
      #      h.setEnabled(False)
      ##try:
      #childRowIdx = index.row()
      #itemData = self.model().nodeFromIndex(index.parent()).child(childRowIdx).itemData
      
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
         