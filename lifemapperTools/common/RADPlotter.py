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
import random
import sys
#from PyQt4.QtCore import QEvent
from PyQt4 import Qt,QtGui
from PyQt4 import QtCore
#import PyQt4.Qwt5 as Qwt
#from PyQt4.Qwt5.anynumpy import *


class DataPlot():
   def __init__(self):
      pass

#class DataPlot(Qwt.QwtPlot):
#
#   def __init__(self, xvector, yvector, xLegend, yLegend, curveTitle, *args):
#      Qwt.QwtPlot.__init__(self, *args)
#      self.xLegend = xLegend
#      self.yLegend = yLegend
#      self.setCanvasBackground(Qt.Qt.white)
#      
#      #will deal with aligning the scales latter
#      #self.alignScales()
#      
#      if 'prop' in xLegend and 'prop' in yLegend:
#         self.setAxisScale(Qwt.QwtPlot.xBottom,0.0,1.0)
#         self.setAxisScale(Qwt.QwtPlot.yLeft,0.0,1.0)
#      # Initialize data
#      
#      self.x = xvector
#      self.y = yvector
#      
#      self.setTitle("Range Diversity Plot")
#      self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);
#      
#      
#      self.curve = Qwt.QwtPlotCurve(curveTitle)
#      
#      
#      self.curve.setStyle(Qwt.QwtPlotCurve.NoCurve)
#      self.curve.attach(self)
#      self.curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
#                                      Qt.QBrush(),
#                                      Qt.QPen(Qt.Qt.red),
#                                      Qt.QSize(7, 7)))
#      
#      self.setStyleSheet("QwtPlot { padding: 45px }") # this provides enough room
#      # for buttons in the legends
#      self.flipButton = QtGui.QPushButton("Flip Axis",parent=self.legend().contentsWidget())
#      QtCore.QObject.connect(self.flipButton, QtCore.SIGNAL("clicked()"), self.flipAxis)
#      
#      
#      # probably will need to set a zoom button against a new legend, or completely rethink
#      #zoomLegend = Qwt.QwtLegend()
#      #self.insertLegend(zoomLegend,Qwt.QwtPlot.{not bottom!!})
#      #self.zoomButton = QtGui.QPushButton("Zoom",parent=zoomLegend.contentsWidget())
#      
#      
#      self.setAxisTitle(Qwt.QwtPlot.xBottom, xLegend)
#      self.setAxisTitle(Qwt.QwtPlot.yLeft, yLegend)
#      
#      self.curve.setData(self.x, self.y)
#      
#      
#   def flipAxis(self):
#      # need to make this so it will toggle back and forth
#      # copy x and y vectors locally
#      copyY = list(self.y)
#      copyX = list(self.x)
#      self.x = copyY
#      self.y = copyX
#      copyYLegend = self.yLegend
#      copyXLegend = self.xLegend
#      self.xLegend = copyYLegend
#      self.yLegend = copyXLegend
#      self.setAxisTitle(Qwt.QwtPlot.xBottom, self.xLegend)
#      self.setAxisTitle(Qwt.QwtPlot.yLeft, self.yLegend)
#      
#      self.curve.setData(self.x, self.y)
#      self.replot()
#      print "flip Axis"
#      
#class Picker(Qwt.QwtPlotPicker):
#   def __init__(self, plot):
#      #Qwt.QwtPlotPicker.__init__(self, *args)
#      self.canvas = plot.canvas()
#      Qwt.QwtPlotPicker.__init__(self, plot.xBottom,
#                            plot.yLeft,
#                            Qwt.QwtPlotPicker.RectSelection,
#                            Qwt.QwtPlotPicker.RectRubberBand,
#                            Qwt.QwtPlotPicker.AlwaysOn,
#                            self.canvas)
#      #self.connect(
#      #  self, Qt.SIGNAL('selected(const QwtPolygon&)'), self.mySlot)
#      #self.connect(
#      #   self, Qt.SIGNAL('appended(const QwtDoublePoint&)'), self.mySlot2)
#      #self.setAxis(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yLeft)
#      #self.setRubberBand(Qwt.QwtPicker.VLineRubberBand)
#      #self.setTrackerMode(Qwt.QwtPicker.AlwaysOn)
#      #self.setSelectionFlags(Qwt.QwtPicker.PointSelection)
#   def mySlot(self, poly):
#      print poly
#       
#   def mySlot2(self, poly):
#      print '2'
#      print poly
#      #print QtCore.Qt.KeyboardModifiers(e.modifiers()).__int__()
#   def eventFilter(self, o, e):
#      #print e
#      if e.type() == QtCore.QEvent.MouseButtonPress:
#         button = e.button()
#         modifiersCode = QtCore.Qt.KeyboardModifiers(e.modifiers()).__int__()
#         if (button == QtCore.Qt.LeftButton
#             and modifiersCode == QtCore.Qt.ShiftModifier):
#            print "shift and left"
#            self.emit(QtCore.SIGNAL('selected(const QwtPolygon&)'),'asdfa')
#             
#            #self.m_left_k_shift_press_event(e)
#         elif (button == QtCore.Qt.LeftButton and
#               modifiersCode == QtCore.Qt.ControlModifier):
#             
#            self.m_left_k_ctrl_press_event(e)
#         elif (button == QtCore.Qt.RightButton and
#               modifiersCode == QtCore.Qt.NoModifier):
#             
#            self.m_right_press_event(e)
#         elif (button == QtCore.Qt.RightButton and
#               modifiersCode == QtCore.Qt.ControlModifier):
#             
#            self.m_right_k_ctrl_press_event(e)
#         elif e.type() == QtCore.QEvent.MouseButtonRelease:
#            button = e.button()
#            modifiersCode = QtCore.Qt.KeyboardModifiers(e.modifiers()).__int__()
#            if button == QtCore.Qt.LeftButton and modifiersCode == QtCore.Qt.ShiftModifier:
#               self.m_left_k_shift_release_event(e)
#      return False
#  
#   def m_left_k_shift_press_event(self, mouseEvent):
#      x = round(self.plot().invTransform(self.plot().xBottom, mouseEvent.pos().x()), 0)
#      self.emit(QtCore.SIGNAL("m_left_k_shift_pressed"), x)
#  
#   def m_left_k_ctrl_press_event(self, mouseEvent):
#      pos_x = mouseEvent.pos().x()
#      self.emit(QtCore.SIGNAL("m_left_k_ctrl_pressed"),
#                  round(self.plot().invTransform(self.plot().xBottom, pos_x), 0))
#  
#   def m_right_press_event(self, mouseEvent):
#      pos = mouseEvent.pos()
#      self.emit(QtCore.SIGNAL("m_right_pressed"), pos)
#  
#   def m_right_k_ctrl_press_event(self, mouseEvent):
#      x = round(self.plot().invTransform(self.plot().xBottom, mouseEvent.pos().x()), 0)
#      self.emit(QtCore.SIGNAL("m_right_k_ctrl_pressed"), x)
#  
#   def m_left_k_shift_release_event(self, mouseEvent):
#      pos = mouseEvent.pos()
#      self.emit(QtCore.SIGNAL("m_left_k_shift_released"), pos)
#        
#              
#class CanvasPicker(Qwt.QwtPlotPicker):
#   
#   def __init__(self, plot):
#      self.canvas = plot.canvas()
#      Qwt.QwtPlotPicker.__init__(self, plot.xBottom,
#                              plot.yLeft,
#                              Qwt.QwtPlotPicker.RectSelection,
#                              Qwt.QwtPlotPicker.RectRubberBand,
#                              Qwt.QwtPlotPicker.AlwaysOn,
#                              self.canvas)
#      
#      self.connect(self, Qt.SIGNAL('selected(const QwtPolygon&)'), self.mySlot)
#      #self.installEventFilter(self)
#   def mySlot(self,poly):
#      
#      print poly
#      
#   #def eventFilter(self, object, event):
#   #   print event
#   #   if event.type() == Qt.QEvent.KeyPress:
#   #      return True
#   #   return False
#   
#class RADCanvas(Qt.QObject): 
# 
#   def __init__(self, plot):
#      Qt.QObject.__init__(self, plot)
#      self.__selectedCurve = None
#      self.__selectedPoint = -1
#      self.__plot = plot
#      self.__selectedpoints = []
#   
#      self.canvas = plot.canvas()
#      #self.picker = Picker(self.__plot)
#      #self.canvas.installEventFilter(self)
#      self.picker = Qwt.QwtPlotPicker(plot.xBottom,
#                              plot.yLeft,
#                              Qwt.QwtPlotPicker.RectSelection,
#                              Qwt.QwtPlotPicker.RectRubberBand,
#                              Qwt.QwtPlotPicker.AlwaysOn,
#                              self.canvas)
#      
#      self.picker.connect(
#           self.picker, Qt.SIGNAL('selected(const QwtDoubleRect&)'), self.pickerSlot)
#      #
#      # We want the focus, but no focus rect.
#      # The selected point will be highlighted instead.
#      self.canvas.setFocusPolicy(Qt.Qt.StrongFocus)
#      # this accepts focus by both tabbing and clicking
#      self.canvas.setCursor(Qt.Qt.PointingHandCursor)
#      self.canvas.setFocusIndicator(Qwt.QwtPlotCanvas.ItemFocusIndicator)
#      self.canvas.setFocus() 
##...............................................................................       
#   def pickerSlot(self,poly):
#      """
#      @summary: slot connected to PlotPicker object, takes QwtDoubleRect polygon
#      object as a single argument.
#      @param poly: select polygon from the canvas
#      """
#      
#      #print poly
#      #print self.picker.selection()  # this is just the polygon object
#      #print self.canvas.keyPressEvent()
#      
#      minx = poly.getCoords()[0]
#      maxy = poly.getCoords()[1]
#      maxx = poly.getCoords()[2]
#      miny = poly.getCoords()[3]     
#      newpoly = Qt.QPolygonF([Qt.QPointF(minx, miny), Qt.QPointF(maxx,miny),
#               Qt.QPointF(maxx, maxy), Qt.QPointF(minx, maxy),
#               Qt.QPointF(minx, miny)])      
#      self.selectUnselect(-1, False)       
#      for point in range(0,self.__plot.curve.data().size()):         
#         x =  self.__plot.curve.data().x(point)         
#         y =  self.__plot.curve.data().y(point)         
#         if newpoly.containsPoint(Qt.QPointF(x,y),0):            
#            self.selectUnselect(point, True)                
##...............................................................................      
#   def selectUnselect(self, point, brush):
#      """
#      @summary: receives points within the select polygon and if brush
#      is set to True, draws a point over that point with a new symbol
#      @param point: point that falls within the select polygon
#      @param brush: flag for selecting or un-selecting
#      """ 
#      
#      symbol = Qwt.QwtSymbol(self.__plot.curve.symbol())
#      newSymbol = Qwt.QwtSymbol(symbol)
#      
#      if brush:
#         newSymbol.setBrush(symbol.brush().color().dark(150))
#      
#         #doReplot = self.__plot.autoReplot()
#         
#         
#         #self.__plot.setAutoReplot(False)
#         self.__plot.curve.setSymbol(newSymbol)
#         self.__plot.curve.draw(point, point)
#         
#         self.__plot.curve.setSymbol(symbol)
#         #self.__plot.setAutoReplot(doReplot) 
#      
#      else:
#         self.__plot.setAutoReplot(True)
#         self.__plot.autoRefresh()
#         self.__plot.setAutoReplot(False)
#         #print 'its here'
#         #self.__plot.curve.setSymbol(newSymbol)
#         #self.__plot.curve.draw(point, point)
#      
#             
#   def eventFilter(self, object, event):
#      
#      if event.type() == Qt.QEvent.KeyPress:
#            
#            key = event.key()
#            print key
#            if key == Qt.Qt.Key_Shift:
#               print key
#               return True
#      return False
#   def __showCursor(self,showIt):
#      
#      curve = self.__selectedCurve
#      if not curve:
#         return
#   
#      
#      symbol = Qwt.QwtSymbol(curve.symbol())
#      newSymbol = Qwt.QwtSymbol(symbol)
#      if showIt:
#         newSymbol.setBrush(symbol.brush().color().dark(150))
#   
#      doReplot = self.__plot.autoReplot()
#   
#      self.__plot.setAutoReplot(False)
#      curve.setSymbol(newSymbol)
#   
#      curve.draw(self.__selectedPoint, self.__selectedPoint)
#      
#      curve.setSymbol(symbol)
#      self.__plot.setAutoReplot(doReplot)
#   
#   def __select(self,position):
#      
#      found, distance, point = None, 1e100, -1
#   
#      for curve in self.__plot.itemList():
#         if isinstance(curve, Qwt.QwtPlotCurve):
#            i, d = curve.closestPoint(position)
#            #print i,d
#            if d < distance:
#               found = curve
#               point = i
#               distance = d
#   
#      self.__showCursor(False)
#      self.__selectedCurve = None
#      self.__selectedPoint = -1
#   
#      if found and distance < 10:
#         self.__selectedCurve = found
#         self.__selectedPoint = point
#         self.__showCursor(True)
#      