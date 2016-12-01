from PyQt4 import QtCore, QtGui

ICON_VALUES = {'server':'SERVER'}

class ClickableLabel(QtGui.QLabel):
   
   clicked = QtCore.pyqtSignal(str)
   
   def __init__(self):
      
      QtGui.QLabel.__init__(self)
      #super(ClickableLabel, self).__init__()
      pixmap = QtGui.QPixmap(":/plugins/lifemapperTools/icons/server.png") # in QGIS
      #pixmap = QtGui.QPixmap("../icons/server.png") # in eclipse
      self.setPixmap(pixmap)
      self.setObjectName(ICON_VALUES['server'])
   
   def mousePressEvent(self, event):
      self.clicked.emit(self.objectName())