
from PyQt4.QtCore import QThread, pyqtSignal

class TaskThread(QThread):
   
   taskFinished = pyqtSignal(bool)   
   
   def __init__(self,parentThread,taskFun):
      QThread.__init__(self,parentThread)
      self.task = taskFun
      
   def run(self):
      res = self.task()
      self.taskFinished.emit(res)  