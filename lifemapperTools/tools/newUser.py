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
import os
import types
import zipfile
from PyQt4.QtGui import *
from qgis.core import *
from lifemapperTools.tools.ui_newUserDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import NewUser
#from LmClient.lmClientLib import LMClient

# .............................................................................

class NewUserDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Grid Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """
   
# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, mode, RADids=None, inputs=None, client=None):
      QDialog.__init__(self)
      self.setupUi()
      #cc = self.buttonBox.button( QDialogButtonBox.Close )
      #bok = self.buttonBox.button( QDialogButtonBox.Ok )
      cc = self.rejectBut
      bok = self.acceptBut
      iG = self.inputGroup
      og = self.outputGroup
      sl = self.statuslabel
      pgbar = self.progressbar
      _Controller.__init__(self, iface, BASE_URL=NewUser.BASE_URL, 
                           STATUS_URL=NewUser.STATUS_URL, 
                           REST_URL=NewUser.REST_URL,
                           cancel_close=cc, 
                           okayButton=bok, ids=RADids )
   # ...........................................................................   
   def cleanInputGridLayout(self):
      
      """@summary:  cleans out the input grid layout"""
     
      if not(self.gridLayout_input.isEmpty()):
         for childindex in range(0,self.gridLayout_input.count()):
            item = self.gridLayout_input.takeAt(0)
            if not(type(item) is types.NoneType):
               item.widget().deleteLater()
              
         self.gridLayout_input.update()  
   # ...........................................................................        
   def setInputGroup(self, parent, *args):
      """
      @summary: sets the inputs in the inputGroups, is called from thread 
      finished for describe Process mode
      @param parent: input group
      @param args: list of input xml elements from the describe process
      document
      """
      
      if args[0] != None:
         self.inputGroup.setTitle('Inputs')
         self.outputGroup.hide()
         self.inputGroup.show()
      #  
      #   self.cleanInputGridLayout()
      #  
      #   for input in args[0]:
      #     
      #      identifier = input.findtext('{http://www.opengis.net/ows/1.1}Identifier')
      #      defaultvalue = input.findtext('LiteralData/DefaultValue')
      #      
      #      #if identifier == 'minx':
      #      #   self.westEdit.setText(defaultvalue)
      #      #  
      #      #if identifier == 'miny':
      #      #   self.southEdit.setText(defaultvalue)   
      #      #  
      #      #if identifier == 'maxx':
      #      #   self.eastEdit.setText(defaultvalue)    
      #      #  
      #      #if identifier == 'maxy':
      #      #   self.northEdit.setText(defaultvalue)
      #      #  
      #      #if identifier == 'cellsize':
      #      #   self.resEdit.setText(defaultvalue)   
      #      #
      #      #if identifier == 'shapename':
      #      #   self.outEdit.setText(defaultvalue)
      #        
         self.buttonOk.setEnabled( True )  
          
   def accept(self):  
      valid = self.validate() 
      if valid:
         #send request
         pass
      else:
         pass
      self.close()
      
   def validate(self):
      """
      @summary: Validates the inputs for the module
      """
      valid = True
      message = ""
      self.keyvalues = {}
      self.keyvalues[str(self.userIdEdit.objectName())] = self.userIdEdit.text()
      self.keyvalues[str(self.emailEdit.objectName())] = self.emailEdit.text()
      self.keyvalues[str(self.passwordEdit.objectName())] = self.passwordEdit.text()
      self.keyvalues[str(self.firstnameEdit.objectName())] = self.firstnameEdit.text()
      self.keyvalues[str(self.lastnameEdit.objectName())] = self.lastnameEdit.text()
      self.keyvalues[str(self.institutionEdit.objectName())] = self.institutionEdit.text()
      self.keyvalues[str(self.address1Edit.objectName())] = self.address1Edit.text()
      self.keyvalues[str(self.address2Edit.objectName())] = self.address2Edit.text()
      self.keyvalues[str(self.address3Edit.objectName())] = self.address3Edit.text()
      self.keyvalues[str(self.address3Edit.objectName())] = self.address3Edit.text()
      self.keyvalues[str(self.phoneEdit.objectName())] = self.phoneEdit.text()
      
      
      
      if len(self.userIdEdit.text()) <= 0:
         message = "Please supply a user id"
         valid = False
      elif len(self.passwordEdit.text()) <= 0:
         message = "Please supply a password"
         valid = False
      
         
      if not valid:
         msgBox = QMessageBox.information(self,
                                                "Problem...",
                                                message,
                                                QMessageBox.Ok)
      return valid
   def processRESTOutputs(self, fileObj, model, url):   
      pass
   
   
      
      