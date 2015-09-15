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
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QDialog
from qgis.core import QgsVectorLayer
from LmCommon.common.lmAttObject import LmAttObj 
import numpy
 
# in somemodule.py
_instance = None 
class Communicate(QObject):
   
   setPamSumExist = pyqtSignal(QDialog)
   
   activateSDMExp = pyqtSignal(str)
   activateRADExp = pyqtSignal(int,str,str)
   activateGrid = pyqtSignal(int,int,int,int,str,str,LmAttObj)
   
   postScenarioFailed  = pyqtSignal(bool)
   postedScenario      = pyqtSignal(str,bool)
   postedOccurrenceSet = pyqtSignal(str,str,int)
   
   
   RADSpsSelectedFromTree = pyqtSignal(list)
   RADSpsSelectFromPlot = pyqtSignal(list,list,list,bool)
   
   
   def __init__(self):
      super(Communicate, self).__init__()
      
   @staticmethod
   def instance():
      global _instance
      if not _instance:
         _instance = Communicate()
      return _instance
 

