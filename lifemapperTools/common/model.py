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
import urllib2
import xml.etree.ElementTree as ET
from PyQt4.QtCore import QObject
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import time
from types import NoneType, ListType
import os

# ..............................................................................
# ..............................................................................

# ..............................................................................
class _Model(QObject):
# ..............................................................................   
   """Superclass for all data models"""
# ..............................................................................
# Constructor

   HTTPError = pyqtSignal(str,str)
   DocumentError = pyqtSignal(str)
# ..............................................................................   
   def __init__(self, urlEndPoint=None, statusurl=None, client=None):
      
      QObject.__init__(self)
      if client:
         self.client = client
      

   
   def getResource(self,url):
           
      """
      @summary: Gets a resource output
      @param url: 
      @return: 
      """
      
      try:
         req = urllib2.Request(url)
         ret = urllib2.urlopen(req)
      except Exception, e:
         #self.emit(SIGNAL("HTTPError"), url,str(e))
         self.HTTPError.emit(url,str(e))
          
      return ret
        
   def getXML(self, url):
      
      """
      @summary: Gets an XML document
      @param url: 
      @return: returns the rootElement
      """
      
      try:
         req = urllib2.Request(url)
         ret = urllib2.urlopen(req)
      except Exception, e:
         #self.emit(SIGNAL("HTTPError"), url,str(e))
         self.HTTPError.emit(url,str(e))
         return 'error'
     
     
      else:
         xml = ''.join(ret.readlines())
         rootElement = ET.fromstring(xml)
        
        
      #self.compareData(rootElement)
      return rootElement
     

class RequestModel(_Model):
   
   """Subclass of _Model. Model based on the Describe Process XML."""
   
   
   def __init__(self, url=None, getStatusUrl=None, client=None):
      
      _Model.__init__(self, urlEndPoint=url, statusurl=getStatusUrl, 
                      client=client)
      
# .............................................................................        
   def makeRequest(self, requestfunc=None, inputs=None):
      
      """
      @summary: Gets an Describe Process document
      @param rquestfunc: the function that makes the request
      @param inputs: inputs to the request, a dictionary of key value pairs
      for keyword arguments
      @return: two lists of dictionaries containing inputs and outputs
      @todo: needs to check for exception report
      """
      
      try:
         outputs = requestfunc(**inputs)

         status = "success"
         self.status = status
         self.outputs = outputs          
      except Exception, e:
         #self.emit(SIGNAL("HTTPError"), "",str(e))
         self.HTTPError.emit("",str(e))
         return 'Failed'        
      else:
         return  self.outputs, self.status
# ..............................................................................
   def getStatus(self, requestfunc=None):
      """
      @summary: wrapper for the getStatus function in parent class
      """
      
      
      try:
         status, stage = requestfunc()
      except Exception, e:
         #self.emit(SIGNAL("HTTPError"), 'getStatus',str(e))
         self.HTTPError.emit('getStatus',str(e))
         return 'Failed','Failed'
          
      else:
         return status, stage
         


               
# ..............................................................................
   def executeRequest(self, requestfunc=None, inputs=None):
      
      try:
         statusFunction = requestfunc(**inputs)
         if not(statusFunction):
            raise Exception('status function not returned')
      except Exception, e:
         #self.emit(SIGNAL("HTTPError"), 'executeRequest', str(e))
         self.HTTPError.emit('executeRequest',str(e))
         return "error"
      
      else:
        
         return statusFunction      

              
 
      
