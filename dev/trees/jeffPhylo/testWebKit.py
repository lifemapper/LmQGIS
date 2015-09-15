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
import sys
import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import simplejson




class WebPage(QWebPage):
   """
   Makes it possible to use a Python logger to print javascript console messages
   """
   def __init__(self, logger=None, parent=None):
      super(WebPage, self).__init__(parent)
      if not logger:
         logger = logging
      self.logger = logger
        

   def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
      self.logger.warning("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))
        
class NodeClass(QObject):  
   """Simple class with two slots """  
   
   def __init__(self):
      QObject.__init__(self)
      
 
   @pyqtSlot(str,str)  #QWebElement
   def showMessage(self, json, domElement):  
      """Open a message box and display the specified message."""  
      #QMessageBox.information(None, "Info", msg) 
      print json
      
      self.selectedNode = simplejson.loads(str(json))
      
   @pyqtSlot(str)
   def processLeafJSON(self, d):
      #pass
      print d
           
   @pyqtSlot(str)
   def selectSps(self, leafs):
      """
      @param leafs: json for the leaves of the tree 
      """
      
      print leafs

class Window(QWidget):
   def __init__(self):
      super(Window, self).__init__()
      
      self.view = QWebView(self)
      self.view.setPage(WebPage())
      self.view.page().settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,True)
      
      #url = "file:///var/www/collapse2.html"
      url = "file:///home/jcavner/workspace/lm3/src/LmClient/LmQGIS/trees/collapse.html"
      self.view.load(QUrl(url)) 
      
      
      self.node = NodeClass()
      self.view.page().mainFrame().addToJavaScriptWindowObject("pyObj", self.node)
      
      self.setWindowTitle('Phylo View')
      
      button = QPushButton("Load Map")
      QObject.connect(button,SIGNAL("clicked()"), self.talkToJS)
      
      rootbutton = QPushButton("Root")
      QObject.connect(rootbutton,SIGNAL("clicked()"), self.rootToJS)
      
      layout = QVBoxLayout(self)
      layout.setMargin(0)
      layout.addWidget(self.view)
      layout.addWidget(button)
      layout.addWidget(rootbutton)
      
   def rootToJS(self):
      self.view.page().mainFrame().evaluateJavaScript('goToRoot();')
      
   def talkToJS(self):
      #self.view.page().mainFrame().evaluateJavaScript('svg.selectAll("circle").style("fill", "#fff");') # for flare.html
      self.view.page().mainFrame().evaluateJavaScript('reportLeafs();') # for collapse
def main():
   app = QApplication(sys.argv)
   window = Window()
   
   window.show()
   #window.view.setHtml(html.html)
   app.exec_()



      
if __name__ == "__main__":
   main()

      