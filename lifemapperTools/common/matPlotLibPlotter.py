"""
@license: gpl2
@copyright: Copyright (C) 2013, University of Kansas Center for Research

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
from matplotlib.figure import Figure
from matplotlib.backend_bases import cursors
import matplotlib.nxutils as nx
from matplotlib.backends.backend_qt4agg import \
 FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QTAgg as NavigationToolbar
#from  matplotlib.backends.qt4_compat import _getSaveFileName
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import sys
import numpy as np
import lifemapperTools.icons.icons

cursord = {
    cursors.MOVE          : QtCore.Qt.SizeAllCursor,
    cursors.HAND          : QtCore.Qt.PointingHandCursor,
    cursors.POINTER       : QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION : QtCore.Qt.CrossCursor,
    }
   
class QtMplCanvas(FigureCanvas):
   
   def __init__(self, xvector,yvector,xlegend,ylegend,title):
      self.fig = Figure(figsize=(10.2, 8)) # possible args figsize=(width, height), dpi=dpi
      self.fig.set_facecolor([.89,.89,.89])
      self.axes = self.fig.add_subplot(111)
      self.axes.set_xlabel(xlegend)
      self.axes.set_ylabel(ylegend)
      xmax = max(xvector)
      ymax = max(yvector)
      self.axes.set_xlim(left=0,right=xmax)
      self.axes.set_ylim(bottom=0,top=ymax)
      self.axes.set_title(title)
      self.selected = {}
      self.ctrl = False

      self.searchIn = self.buildSearchIn(xvector, yvector)
      self.axes.scatter(xvector,yvector,marker='o',c='g',s=47,picker=True)
      
      FigureCanvas.__init__(self,self.fig)
      
      self.mpl_connect('pick_event',self.onpick) 
      self.mpl_connect('key_press_event',self.keyPress)
      self.mpl_connect('key_release_event',self.keyRelease)
      self.setFocusPolicy( QtCore.Qt.ClickFocus )
      self.setFocus()

   def keyPress(self,event):
      if event.key == 'control':
         self.ctrl = True
   def keyRelease(self,event):
      if event.key == 'control':
         self.ctrl = False
   
   def buildSearchIn(self,xvector,yvector):     
      l = []
      for x,y in zip(xvector,yvector):
         p = []
         p.append(x)
         p.append(y)
         l.append(p)      
      return np.array(l) 
   

      
   def onpick(self, event):
      """
      @summary pick event for plot canvas, needs to be reworked for scatter canvas
      """
      
      ind = event.ind   # position in the data array
      x,y = self.searchIn[event.ind][0]
      if (x,y) in self.selected:
         markers = self.selected[(x,y)]
         for m in markers:
            m.set_visible(not m.get_visible())
          
      else:
         t = self.axes.text(x,y,'')
         m = self.axes.scatter([x],[y], s=47, marker='o', c='r', zorder=100)
         self.selected[(x,y)] =(t,m)
      self.draw()
   
      
class RadNavigationToolBar(NavigationToolbar):
   
   def __init__(self, plotCanvas,parentwindow,saveDir):
      
      NavigationToolbar.__init__(self, plotCanvas, parentwindow) 
      self.canvas = plotCanvas
      self._ids_select = []
      self.saveDir = saveDir
      selectIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/selectbyrect.png")
      panIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/pan.png")
      zoomLastIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/zoomlast.png")
      zoomNextIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/zoomnext.png")
      zoomInIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/zoomin.png")
      
      self.removeAction(self.actions()[7])
      self.removeAction(self.actions()[7])
      
      self.removeAction(self.actions()[1])
      self.removeAction(self.actions()[1])
      
      self.removeAction(self.actions()[2])
      self.removeAction(self.actions()[2])
      
      self.panAction = QtGui.QAction(panIcon,'',self)
      self.panAction.setToolTip('Pan axes with left mouse, zoom with right')
      
      self.zoomInAction = QtGui.QAction(zoomInIcon,'',self)
      self.zoomInAction.setToolTip('Zoom to rectangle')
      
      self.zoomNextAction = QtGui.QAction(zoomNextIcon,'',self)
      self.zoomNextAction.setToolTip('Forward to next view')
      
      self.zoomLastAction = QtGui.QAction(zoomLastIcon,'',self)
      self.zoomLastAction.setToolTip('Back to previous view')
      
      self.selectAction = QtGui.QAction(selectIcon,'',self)
      self.selectAction.setToolTip("Select Data Points by dragging rectangle")
      
      # try this alignToolAct.triggered.connect(self.align) instead of connect below
      QtCore.QObject.connect(self.selectAction, QtCore.SIGNAL("triggered()"), self.select)
      QtCore.QObject.connect(self.panAction, QtCore.SIGNAL("triggered()"), self.pan)
      QtCore.QObject.connect(self.zoomInAction, QtCore.SIGNAL("triggered()"), self.zoom)
      QtCore.QObject.connect(self.zoomNextAction, QtCore.SIGNAL("triggered()"), self.forward)
      QtCore.QObject.connect(self.zoomLastAction, QtCore.SIGNAL("triggered()"), self.back)
      
      self.insertAction(self.actions()[2],self.zoomNextAction)
      self.insertAction(self.actions()[2],self.zoomLastAction)   
      self.insertAction(self.actions()[2],self.zoomInAction)
      self.insertAction(self.actions()[2],self.panAction)
      self.insertAction(self.actions()[-1],self.selectAction)
      

   def save_figure(self, *args):
      """
      @summary: over ride this in our tool bar so that we can set the start 
      path for the file dialog to the users workspace and project directory,
      or if we want to do just a save, gut this all except self.canvas.print_figure( unicode(fname) )
      and just send a file name with no dialog
      """
      filetypes = self.canvas.get_supported_filetypes_grouped()
      sorted_filetypes = filetypes.items()
      sorted_filetypes.sort()
      default_filetype = self.canvas.get_default_filetype()
   
      start = self.saveDir
      filters = []
      selectedFilter = None
      for name, exts in sorted_filetypes:
         exts_list = " ".join(['*.%s' % ext for ext in exts])
         filter = '%s (%s)' % (name, exts_list)
         if default_filetype in exts:
            selectedFilter = filter
         filters.append(filter)
      filters = ';;'.join(filters)
   
      #fname = _getSaveFileName(self, "Choose a filename to save to",
      #                                start, filters, selectedFilter)
      fname = QtGui.QFileDialog.getSaveFileName(
            self, "Choose a filename to save to",
                                      start, filters, selectedFilter)
      if fname:
         try:
            self.canvas.print_figure( unicode(fname) )
         except Exception, e:
            QtGui.QMessageBox.critical(
                 self, "Error saving file", str(e),
                 QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
   
      
   def select(self, *args):
      'activate select to rect mode'
      
      if self._active == 'SELECT':
         self._active = None
         self.set_cursor(cursors.POINTER)
      else:
         self._active = 'SELECT'
         self.set_cursor(cursors.SELECT_REGION)

      if self._idPress is not None:
         self._idPress=self.canvas.mpl_disconnect(self._idPress)
         self.mode = ''

      if self._idRelease is not None:
         self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
         self.mode = ''

      if  self._active:
         self._idPress = self.canvas.mpl_connect('button_press_event', self.press_select)
         self._idRelease = self.canvas.mpl_connect('button_release_event', self.release_select)
         self.mode = 'select rect'
         self.canvas.widgetlock(self)
      else:
         self.canvas.widgetlock.release(self)

      for a in self.canvas.figure.get_axes():
         a.set_navigate_mode(self._active)

      self.set_message('select w/ rect')
      

   def press_select(self, event):
      'the press mouse button in zoom to rect mode callback'
      if event.button == 1:
         self._button_pressed=1
      elif  event.button == 3:
         self._button_pressed=3
      else:
         self._button_pressed=None
         return

      x, y = event.x, event.y

      # push the current view to define home if stack is empty
      if self._views.empty(): self.push_current()

      self._xypress=[]
      for i, a in enumerate(self.canvas.figure.get_axes()):
         if (x is not None and y is not None and a.in_axes(event) and
            a.get_navigate() and a.can_zoom()) :
            self._xypress.append(( x, y, a, i, a.viewLim.frozen(),
                                     a.transData.frozen() ))

      id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_select)

      id2 = self.canvas.mpl_connect('key_press_event',
                                    self._switch_on_select_mode)
      id3 = self.canvas.mpl_connect('key_release_event',
                                    self._switch_off_select_mode)

      self._ids_select = id1, id2, id3

      self._select_mode = event.key


      self.press(event)
      
      
   def drawSelected(self, axes, allData, selectedPoints):
      """
      Draw the annotation on the plot
      """
      if self.canvas.ctrl:
         for xy,selected in zip(allData,selectedPoints):
            x = xy[0]
            y = xy[1]
            if selected:
               if (x,y) in self.canvas.selected:
                  markers = self.canvas.selected[(x,y)]
                  if not markers[0].get_visible():
                     for m in markers:
                        m.set_visible(True)               
               else:   
                  t = axes.text(x,y,'')
                  m = axes.scatter([x],[y], s=47, marker='o', c='r', zorder=100)
                  self.canvas.selected[(x,y)] =(t,m)
      else:
         for key in self.canvas.selected.keys():
            markers = self.canvas.selected[key]
            if markers[0].get_visible():
               for m in markers:
                  m.set_visible(False)
            self.canvas.selected.pop(key,None)
                  
         for xy,selected in zip(allData,selectedPoints):
            x = xy[0]
            y = xy[1]
            if selected:               
               t = axes.text(x,y,'')
               m = axes.scatter([x],[y], s=47, marker='o', c='r', zorder=100)
               self.canvas.selected[(x,y)] =(t,m)
               
                  
         
      self.canvas.axes.figure.canvas.draw()
      
   def release_select(self, event):
      
      'the release mouse button callback in select to rect mode'
      for select_id in self._ids_select:
         self.canvas.mpl_disconnect(select_id)
      self._ids_select = []
   
      if not self._xypress: return
   
      last_a = []
   
      for cur_xypress in self._xypress:
         x, y = event.x, event.y
         lastx, lasty, a, ind, lim, trans = cur_xypress
         # ignore singular clicks - 5 pixels is a threshold
         if abs(x-lastx)<5 or abs(y-lasty)<5:
            self._xypress = None
            self.release(event)
            self.draw()
            return
   
         x0, y0, x1, y1 = lim.extents
   
         # select to rect
         inverse = a.transData.inverted()
         lastx, lasty = inverse.transform_point( (lastx, lasty) )
         x, y = inverse.transform_point( (x, y) )
         Xmin,Xmax=a.get_xlim()
         Ymin,Ymax=a.get_ylim()
   
         # detect twinx,y axes and avoid double selecting
         twinx, twiny = False, False
         if last_a:
            for la in last_a:
               if a.get_shared_x_axes().joined(a,la): twinx=True
               if a.get_shared_y_axes().joined(a,la): twiny=True
         last_a.append(a)
   
         if twinx:
            x0, x1 = Xmin, Xmax
         else:
            if Xmin < Xmax:
               if x<lastx:  x0, x1 = x, lastx
               else: x0, x1 = lastx, x
               if x0 < Xmin: x0=Xmin
               if x1 > Xmax: x1=Xmax
            else:
               if x>lastx:  x0, x1 = x, lastx
               else: x0, x1 = lastx, x
               if x0 > Xmin: x0=Xmin
               if x1 < Xmax: x1=Xmax
   
         if twiny:
            y0, y1 = Ymin, Ymax
         else:
            if Ymin < Ymax:
               if y<lasty:  y0, y1 = y, lasty
               else: y0, y1 = lasty, y
               if y0 < Ymin: y0=Ymin
               if y1 > Ymax: y1=Ymax
            else:
               if y>lasty:  y0, y1 = y, lasty
               else: y0, y1 = lasty, y
               if y0 > Ymin: y0=Ymin
               if y1 < Ymax: y1=Ymax
               
         searchin = self.canvas.searchIn
         bbox = np.array([ [x0,y0], [x0, y1], [x1, y1], [x1,y0]], float)
         selectedList = nx.points_inside_poly(searchin,bbox)       
         axes = self.canvas.axes
         self.drawSelected(axes, searchin, selectedList)
      
      self.draw()
      self._xypress = None
      self._button_pressed = None
   
      self._select_mode = None

      self.release(event)
      
   def drag_select(self, event):
      'the drag callback in select mode'
   
      if self._xypress:
         x, y = event.x, event.y
         lastx, lasty, a, ind, lim, trans = self._xypress[0]
   
         # adjust x, last, y, last
         x1, y1, x2, y2 = a.bbox.extents
         x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
         y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)
   
         if self._select_mode == "x":
            x1, y1, x2, y2 = a.bbox.extents
            y, lasty = y1, y2
         elif self._select_mode == "y":
            x1, y1, x2, y2 = a.bbox.extents
            x, lastx = x1, x2
   
         self.draw_rubberband(event, x, y, lastx, lasty)
         
   def _switch_on_select_mode(self, event):
      self._select_mode = event.key
      self.mouse_move(event)

   def _switch_off_select_mode(self, event):
      self._select_mode = None
      self.mouse_move(event)
        
class PlotWindow(QtGui.QMainWindow):
   def __init__(self, xvector, yvector,xlegend,ylegend,title,saveDir):
      QtGui.QMainWindow.__init__(self)
      self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
      self.setWindowTitle("Range Diversity Plot")
      self.main_widget = QtGui.QWidget(self)
      l = QtGui.QVBoxLayout(self.main_widget)  
      sc = QtMplCanvas(xvector,yvector,xlegend,ylegend,title) #width=5, height=3, dpi=100
      l.addWidget(sc)
      bar = RadNavigationToolBar(sc,self,saveDir)
      l.addWidget(bar) 
      self.main_widget.setFocus()
      self.setCentralWidget(self.main_widget)
           
class EnterPlot(QObject):
   
   def eventFilter(self,object,event):
      print event
      return QtGui.QWidget.eventFilter(self, object, event)      
#      
if __name__ == "__main__":
   
   qApp = QtGui.QApplication(sys.argv)
   X = np.random.rand(700, 1000)
   xs = np.mean(X, axis=1)
   ys = np.std(X, axis=1)
   aw = PlotWindow(xs,ys,'dfas','hh','etertera','/home/jcavner')
   aw.show()
   sys.exit(qApp.exec_())