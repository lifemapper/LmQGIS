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
from matplotlib.figure import Figure
from matplotlib.backend_bases import cursors
from matplotlib.widgets import Lasso
from matplotlib.path import Path
from matplotlib.backends.backend_qt4agg import \
 FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QTAgg as NavigationToolbar
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, pyqtSignal
from qgis.core import *
from qgis.gui import *
import sys
import numpy as np
import lifemapperTools.icons.icons
from lifemapperTools.common.communicate import Communicate
try:
   import matplotlib.nxutils as nx
except:
   pass

cursord = {
    cursors.MOVE          : QtCore.Qt.SizeAllCursor,
    cursors.HAND          : QtCore.Qt.PointingHandCursor,
    cursors.POINTER       : QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION : QtCore.Qt.CrossCursor,
    }
   
class QtMplCanvas(FigureCanvas):
   
   def __init__(self, xvector,yvector,xlegend,ylegend,title,ids=[],window=None):
      self.fig = Figure(figsize=(10.2, 8)) # possible args figsize=(width, height), dpi=dpi
      self.fig.set_facecolor([.89,.89,.89])
      self.axes = self.fig.add_subplot(111)
      self.axes.set_xlabel(xlegend)
      self.axes.set_ylabel(ylegend)
      xmax = max(xvector)
      ymax = max(yvector)
      xmin = min(xvector)
      ymin = min(yvector)
      self.axes.set_xlim(left=xmin,right=xmax)
      self.axes.set_ylim(bottom=ymin,top=ymax)
      self.axes.set_title(title)
      self.selected = {}
      self.ctrl = False
      self.tableids = ids
      self.speciesIds = None
      self.allDatabyID = None
      self.parentWindow = window
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
      if len(self.tableids) == 0:     
         for x,y in zip(xvector,yvector):
            l.append((x,y))  
      else:
         
         allDatabyID = []
         for id,x,y in zip(self.tableids,xvector,yvector):
            l.append((x,y)) 
            allDatabyID.append((id,x,y))
         self.allDatabyID = np.array(allDatabyID)   
      return np.array(l) 
   

      
   def onpick(self, event):
      """
      @summary pick event for plot canvas
      """
      
      selectedPoints = [False for x in range(0, len(self.tableids))]
      ind = event.ind   # position in the data array
      if self.allDatabyID is None:
         x,y = self.searchIn[event.ind][0]
         if (x,y) in self.selected:
            markers = self.selected[(x,y)]
            for m in markers:
               m.set_visible(not m.get_visible())
             
         else:
            t = self.axes.text(x,y,'')
            m = self.axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
            self.selected[(x,y)] =(t,m)
         
      else:  # all this has to do is loop through the event.ind !
         for pos in event.ind:
            id,x,y = self.allDatabyID[pos]
            if self.ctrl:
               if id in self.selected:
                  markers = self.selected[id]
                  if not markers[0].get_visible():
                     selectedPoints[pos] = True
                     for m in markers:
                        m.set_visible(True)   
               else:
                  t = self.axes.text(x,y,'')
                  m = self.axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
                  self.selected[id] =(t,m)          
                  selectedPoints[pos] = True 
            else:
               for key in self.selected.keys():
                  markers = self.selected[key]
                  if markers[0].get_visible():
                     for m in markers:
                        m.set_visible(False)
                  self.selected.pop(key,None)
                  
               t = self.axes.text(x,y,'')
               m = self.axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
               self.selected[id] =(t,m)          
               selectedPoints[pos] = True 
                  
               
               
      self.draw()
      selectedPoints = np.array(selectedPoints)
      
      
      Communicate.instance().RADSpsSelectFromPlot.emit(self.tableids,list(selectedPoints),[], self.ctrl)     
      self.parentWindow.selectSitesinMap(selectedPoints,self.tableids,self.ctrl)
      self.parentWindow.bar.fromPlot = False
      
      #Communicate.instance().RADSitesSelected.emit(selectedPoints,self.tableids,self.ctrl)
      #Communicate.instance().RADSpeciesSelected.emit(selectedPoints,self.tableids,self.ctrl)
      

      
class RadNavigationToolBar(NavigationToolbar):
   
   def __init__(self, plotCanvas, parentwindow, saveDir, lman = None):
      
      NavigationToolbar.__init__(self, plotCanvas, parentwindow) 
      self.canvas = plotCanvas
      self.lman = lman
      self.lman.tool = self
      self._ids_select = []
      self.cid = None # lasso
      self.saveDir = saveDir
      lassoIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/lasso.png")
      selectIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/selectbyrect.png")
      panIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/pan.png")
      zoomLastIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/zoomlast.png")
      zoomNextIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/zoomnext.png")
      zoomInIcon = QtGui.QIcon(":/plugins/lifemapperTools/icons/zoomin.png")
      
      self.parentWindow = parentwindow
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
      
      self.lassoAction = QtGui.QAction(lassoIcon,'',self)
      self.lassoAction.setToolTip("Select Data Points with lasso")
      
      # try this alignToolAct.triggered.connect(self.align) instead of connect below
      #QtCore.QObject.connect(self.selectAction, QtCore.SIGNAL("triggered()"), self.select)
      #QtCore.QObject.connect(self.panAction, QtCore.SIGNAL("triggered()"), self.pan)
      #QtCore.QObject.connect(self.zoomInAction, QtCore.SIGNAL("triggered()"), self.zoom)
      #QtCore.QObject.connect(self.zoomNextAction, QtCore.SIGNAL("triggered()"), self.forward)
      #QtCore.QObject.connect(self.zoomLastAction, QtCore.SIGNAL("triggered()"), self.back)
      
      Communicate.instance().RADSpsSelectedFromTree.connect(self.selectSpsInPlot)
      
      self.lassoAction.triggered.connect(self.lass)
      
      self.selectAction.triggered.connect(self.select)
      self.panAction.triggered.connect(self.pan)
      self.zoomInAction.triggered.connect(self.zoom)
      self.zoomNextAction.triggered.connect(self.forward)
      self.zoomLastAction.triggered.connect(self.back)
      
      self.insertAction(self.actions()[2],self.zoomNextAction)
      self.insertAction(self.actions()[2],self.zoomLastAction)   
      self.insertAction(self.actions()[2],self.zoomInAction)
      self.insertAction(self.actions()[2],self.panAction)
      self.insertAction(self.actions()[-1],self.selectAction)
      self.insertAction(self.actions()[-2],self.lassoAction)
      
      ##############
      self.fromPlot = False
      ##############
   
   def lass(self, *args):
      #"called when lasso button is clicked"
      #print "_active in lass ", self._active
      #if self._active == 'LASSOSELECT':
      #   self._active = None
      #   #self._select_mode = None  # not sure about this
      #   #self.canvas.widgetlock.release(self.lman.lasso)
      #   self.canvas.mpl_disconnect(self.cid)
      #   self.set_cursor(cursors.POINTER)
      #else:
      #   self._active = 'LASSOSELECT'
      #   self.set_cursor(cursors.SELECT_REGION)
      #
      #   self.cid = self.canvas.mpl_connect('button_press_event',self.lman.onpress)
      
      'activate select to rect mode'
      if self._active == 'LASSOSELECT':
         self._active = None
         self.set_cursor(cursors.POINTER)
      else:
         self._active = 'LASSOSELECT'
         self.set_cursor(cursors.SELECT_REGION)

      if self._idPress is not None:
         self._idPress=self.canvas.mpl_disconnect(self._idPress)
         self.mode = ''

      if self._idRelease is not None:
         self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
         self.mode = ''
      
      if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
      
      if  self._active:
         self._idPress = self.canvas.mpl_connect('button_press_event', self.lman.onpress)
         #self._idRelease = self.canvas.mpl_connect('button_release_event', self.release_select)
         self.mode = 'select lasso'
         self.canvas.widgetlock(self)
      else:
         self.canvas.widgetlock.release(self)

      for a in self.canvas.figure.get_axes():
         a.set_navigate_mode(self._active)

      self.set_message('select w/ lasso')
      
   def selectSpsInPlot(self, selectedIds ):
      """
      @summary: connected to signal emitted from tree
      """
      
      selectedMaskList = [True if mtrxId in selectedIds else False for mtrxId in self.canvas.tableids]
      selectedMaskArray = np.array(selectedMaskList)
      self.drawSelected(self.canvas.axes, self.canvas.searchIn, selectedMaskArray,fromTree = True)
      
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
   
      fileDialog = QgsEncodingFileDialog( self, "Choose a filename to save to", start,selectedFilter)
      fileDialog.setDefaultSuffix(  "png"  )
      fileDialog.setFileMode( QtGui.QFileDialog.AnyFile ) 
      fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptSave )
      fileDialog.setConfirmOverwrite( True )
     
      if not fileDialog.exec_() == QtGui.QFileDialog.Accepted:
         return
      filename = fileDialog.selectedFiles()
      fname = filename[0]
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
      
      if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
      
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
      'this fires when cursor is in canvas and is pressed'
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
                
         
   def drawSelected(self, axes, allData, selectedPoints,fromTree = False, deselected = [], event=None):
      """
      @summary: Draw the annotation on the plot
      @param allData:  self.canvas.searchIn
      @param selectedPoints: list of boolean
      """
      
      if self.canvas.allDatabyID is None:
         
         try:
            if event is not None:
               if event.key == "control":
                  control = True
               else:
                  control = False
            else:
               control = False
         except:
            control = False
         if control or self.canvas.ctrl:
            control = True
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
                     m = axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
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
                  m = axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
                  self.canvas.selected[(x,y)] =(t,m)
      else:
         try:
            if event is not None:
               if event.key == "control":
                  control = True
               else:
                  control = False
            else:
               control = False
         except:
            control = False
         if control or self.canvas.ctrl:
            control = True
            #print "is it in ctrl?"
            for idxy,selected in zip(self.canvas.allDatabyID,selectedPoints):
               id = idxy[0]
               x = idxy[1]
               y = idxy[2]
               if selected:
                  if id in self.canvas.selected:                    
                     markers = self.canvas.selected[id]
                     if not markers[0].get_visible():
                        for m in markers:
                           m.set_visible(True)                         
                                 
                  else:   
                     t = axes.text(x,y,'')
                     m = axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
                     self.canvas.selected[id] =(t,m)
               else:
                  if id in self.canvas.selected and id in deselected:
                     marker = self.canvas.selected[id]
                     if marker[0].get_visible():
                        for m in marker:
                           m.set_visible(False)
                     
         else:
            for key in self.canvas.selected.keys():
               markers = self.canvas.selected[key]
               if markers[0].get_visible():
                  for m in markers:
                     m.set_visible(False)
               self.canvas.selected.pop(key,None)
                     
            for idxy,selected in zip(self.canvas.allDatabyID,selectedPoints):
               id = idxy[0]
               x = idxy[1]
               y = idxy[2]
               if selected:               
                  t = axes.text(x,y,'')
                  m = axes.scatter([x],[y], s=47, marker='o', c='#EEEE00', zorder=100)
                  self.canvas.selected[id] =(t,m)
      
      try: 
         self.canvas.axes.figure.canvas.draw()
      except:
         pass
      #Communicate.instance().RADSitesSelected.emit(selectedPoints,self.canvas.tableids,self.canvas.ctrl)
      #Communicate.instance().RADSpeciesSelected.emit(selectedPoints,self.canvas.tableids,self.canvas.ctrl)
      # if  this, i.e. draw selected is getting called from treeWindow, then skip they call to selectSitesinMap????
      
      try:
         if not fromTree:    
            if self.parentWindow.typePlot == 'Sites':        
               self.parentWindow.selectSitesinMap(selectedPoints,self.canvas.tableids,control)
            if self.parentWindow.typePlot == 'Species': ## this goes to the tree, fromTree = True, keeps it from cycling
               Communicate.instance().RADSpsSelectFromPlot.emit(self.canvas.tableids,list(selectedPoints),[],control)
      except Exception, e:
         pass
      
      self.fromPlot = False
      #if fromTree:
         #print "from Tree" # maybe do nothing and therefore get rid of this condition, still is this going to circle round

      
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
         
         try:
            selectedList = nx.points_inside_poly(searchin,bbox)
         except:
            try:
               selectedList = Path([ [x0,y0], [x0, y1], [x1, y1], [x1,y0], [x0,y0]]).contains_points(searchin)   
            except Exception, e:
               print str(e)
            
         axes = self.canvas.axes
        
       
         #self.selectThread = PlotSelectThread(self.canvas,searchin,selectedList,
         #                                     allDatabyID=self.canvas.allDatabyID,parent=self.parentWindow)
         #self.selectThread.start()
         
         self.drawSelected(axes, searchin, selectedList,event=event)  # this slows down the selection
         # in the map, 
      
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

class LassoManager(object):
   
   def __init__(self, ax, data):
      self.canvas= ax.figure.canvas
      self.axes = ax
      self.data = data
      self.tool = None # toolbar, big question here
      
      
   def callback(self, verts):
      if self.tool._active == 'LASSOSELECT':
         
         searchin = self.canvas.searchIn
         try:
            selectedList =nx.points_inside_poly(searchin, verts)
         except:
            try:
               selectedList = Path(verts).contains_points(searchin)   
            except Exception, e:
               print str(e)
         self.tool.drawSelected(self.axes, searchin, selectedList, event=self.lassoEvent) 
         
         self.canvas.draw_idle()
         self.canvas.widgetlock.release(self.tool)
         
      else:
         pass
      
   def onpress(self, event):
      self.lassoEvent = event
      
      if self.tool._active == 'LASSOSELECT':
         self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
         #try:
         self.canvas.widgetlock(self.tool)
         #except:
         #   pass
      else:
         #self.canvas.widgetlock.release(self.lasso)
         self._select_mode = None  # need to really check if this is necesarry
         #del self.lasso
      
      
        
class PlotWindow(QtGui.QDialog):
   def __init__(self, xvector, yvector, xlegend, ylegend, title, saveDir, ids=[], activeLyr=None, typePlot=None):
      QtGui.QDialog.__init__(self)
      self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
      self.setWindowTitle("Range Diversity Plot")
      #self.main_widget = QtGui.QWidget(self)
      self.typePlot = typePlot
      self.activeLyr = activeLyr
      if self.activeLyr is not None:
         self.activeLyr.selectionChanged.connect(self.featuresSelectedInMap)
      self.selectedFIDs = []
      l = QtGui.QVBoxLayout(self)  
      sc = QtMplCanvas(xvector,yvector,xlegend,ylegend,title,ids=ids,window=self) #width=5, height=3, dpi=100
      self.canvas = sc
      lman = LassoManager(sc.axes, (xvector,yvector))
      l.addWidget(sc)
      bar = RadNavigationToolBar(sc,self,saveDir,lman)
      self.bar = bar
      l.addWidget(bar) 
      
      
   def featuresSelectedInMap(self,selected,deselected,clearAndSelect):
      #print 'selected ',selected," delselected ",deselected," CS ",clearAndSelect
      if not clearAndSelect:      
         self.canvas.ctrl = True
      else:
         "is it getting in here from just plot select?"
         self.canvas.ctrl = False
      # features select in map, so select them in plot if not from plot (self.fromPlot = True)
      if not self.bar.fromPlot:
         selectedMaskList = [True if FID in selected else False for FID in self.canvas.tableids]
         selectedMaskArray = np.array(selectedMaskList)
         # not really from tree but keeps it from cycling on just from map select
         self.bar.drawSelected(self.canvas.axes, self.canvas.searchIn, selectedMaskArray ,fromTree = True, deselected = deselected)
     
   def selectSitesinMap(self,sitesSelected,fids,ctrl):
      """
      @summary: connected to signal emitted in matplotlib
      @param sitesSelected: a one dimensional numpy array of booleans indicating if sites
      were selected, e.g. [True, True, False,...], returned in the order matching the order
      of the values in the table.
      @param fids: list of fids originally from the table
      """
      #if self.activeLyr is not None:
      self.bar.fromPlot = True
      if self.activeLyr is not None:
         sitesSelectedList = list(sitesSelected)
         #selectLyr = self.interface.mapCanvas().currentLayer()
         selectLyr = self.activeLyr
         if not ctrl:
            self.selectedFIDs = [fid for fid,selected in zip(fids,sitesSelectedList) if selected]   
            selectLyr.setSelectedFeatures(self.selectedFIDs) # using just select, gives the option of 
            # not emiting selectionChanged signal, in 2.0, setSelectedFeatures sends args to slot for
            # selectionChanged
         else:
            if len(self.selectedFIDs) > 0:
               added = [fid for fid,selected in zip(fids,sitesSelectedList) if selected]
               self.selectedFIDs = list(set(added + self.selectedFIDs))
               selectLyr.setSelectedFeatures(self.selectedFIDs)
            else:
               self.selectedFIDs = [fid for fid,selected in zip(fids,sitesSelectedList) if selected]   
               selectLyr.setSelectedFeatures(self.selectedFIDs) 
           
class EnterPlot(QObject):
   
   def eventFilter(self,object,event):
      
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