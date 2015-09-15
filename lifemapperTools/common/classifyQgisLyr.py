 # -*- coding: utf-8 -*-
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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from lifemapperTools.common.colorramps import HOTCOLD
from lifemapperTools.common.colorpalette import ColorPalette
from lifemapperTools.common.pluginconstants import Renderers
from matplotlib import pyplot as plt
import matplotlib.colors as col
import math





#cmp2 = col.LinearSegmentedColormap.from_list('heat2',['#66FFFF','#E6E600','#CC2900'])


class Classify(object):
   
      GEOMETRY_POINT = 0
      GEOMETRY_POLY = 2
      """
      basic class for different types of classification
      """
      def __init__(self,layer):
         
         self.layer = layer
         self.typeRenderer = Renderers.GRADUATED
         self._noClasses = None
         self._colormap   = None
# .......................................................................................          
      @property
      def noClasses(self):
         return self._noClasses
# .......................................................................................          
      @noClasses.setter
      def noClasses(self, noClasses):
         if self.typeRenderer == Renderers.GRADUATED:
            self._noClasses = noClasses
         else:
            raise Exception("not type graduated")
# .......................................................................................          
      def buildRanges(self, geometryType, minimum, maximum, invert=False, colorramp = None):
         """
         @summary: builds a list of QgsRendererRangeV2 objects
         """
         #if minimum > 1 or maximum > 1:  # this won't work, if user enters .09 and 1.2
         #   # need something that pairs them as either both below 1.0 or both above 1.0
         #   minimum = minimum/float(maximum)
         #   maximum = 1.0
         if colorramp is None:
            colormap = self.matplotHeat
         ranges = []       
         for i in range(0,self.noClasses):
            
            lower = minimum + ( maximum - minimum ) / self.noClasses * i
            upper = minimum + ( maximum - minimum ) / self.noClasses * ( i + 1 )
            if i == 0:
               lower = math.floor(lower * 10000) / 10000
            if i == self.noClasses - 1:
               upper = math.ceil(upper * 10000) / 10000
            middle = ((upper - lower) / 2) + lower 
            
            r,g,b,a = map(lambda x: x*255,colormap(float(i)/self.noClasses))
            
            color = QColor(r,g,b)            
            symbol = QgsSymbolV2.defaultSymbol(geometryType)              
            if geometryType == self.GEOMETRY_POLY:
               sL = QgsSimpleFillSymbolLayerV2(borderStyle=Qt.NoPen)
               symbol.changeSymbolLayer(0,sL)               
            symbol.setColor(color)
            
            if geometryType == self.GEOMETRY_POINT:
               symbol.setSize(1.4)
            lower = ('%.*f' % (6, lower ) )
            upper = ('%.*f' % (6, upper ) )
            label = "%s - %s" % (lower, upper)
            #print label
            newrange = QgsRendererRangeV2(
                                       float(lower),
                                       float(upper),
                                       symbol,
                                       label)
            ranges.append(newrange)
         return ranges
# ......................................................................................
      def buildRuleBasedRenderer(self,symbol):
         
         renderer = QgsRuleBasedRendererV2(symbol)
         return renderer
# ......................................................................................
      def buildEqualIntervalRenderer(self,ranges,fieldName = None):
         """
         @summary: return equal interval renderer with ranges, but no Class Attribute set
         """   
         if fieldName is None:
            field = ''  
         else:
            field = fieldName    
         renderer = QgsGraduatedSymbolRendererV2(field,ranges)
         renderer.setMode(
                  QgsGraduatedSymbolRendererV2.EqualInterval)
         return renderer
# .......................................................................................
      def attrMinMax(self,fieldName):
         """
         @summary: given a field name return min and max for that attribute 
         for the layer, this will not work on joined fields
         """
         fieldIndex = self.layer.fieldNameIndex(fieldName)
         provider = self.layer.dataProvider()
         minimum = float(provider.minimumValue( fieldIndex ))
         maximum = float(provider.maximumValue( fieldIndex ))
         
         return minimum, maximum
         
# .......................................................................................       
      @property            
      def matplotHeat(self):
         if self._colormap is not None:
            return self._colormap
         else:
            self.setmatplotHeat()
            return self._colormap
      
# .......................................................................................       
      def setmatplotHeat(self,cMapName='heat'):
         
         self._colormap = col.LinearSegmentedColormap.from_list(cMapName,
                                                                ['#66FFFF','#E6E600','#CC2900'])   
# .......................................................................................          
      def heatRGB(self, minimum, maximum, value):
         #  this is isn't as pretty
         minimum, maximum = float(minimum), float(maximum)
         halfmax = (minimum + maximum) / 2
         b = int(max(0, 255*(1 - value/halfmax)))
         r = int(max(0, 255*(value/halfmax - 1)))
         g = 255 - b - r
         return r, g, b


         
         
         
         
         
         
         
         