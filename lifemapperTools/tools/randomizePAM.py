# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MacroEcoDialog
                                 A QGIS plugin
 Macro Ecology tools for presence absence matrices
                             -------------------
        begin                : 2011-02-21
        copyright            : (C) 2014 by Biodiversity Institute
        email                : jcavner@ku.edu
 ***************************************************************************/

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
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QUrl
from qgis.core import *
from LmCommon.common.lmconstants import RandomizeMethods
from lifemapperTools.tools.ui_randomizePAMDialog import Ui_Dialog
from lifemapperTools.tools.controller import _Controller
from lifemapperTools.common.pluginconstants import GENERIC_REQUEST, EXECUTE_REQUEST


# .............................................................................

class RandomizePAMDialog( _Controller, QDialog, Ui_Dialog):
   
   """
   Randomize Dialog Class, inherits from QDialog,_Controller and Ui_Dialog
   """

# .............................................................................
# Constructor
# .............................................................................
   def __init__(self, iface, RADids=None, inputs=None, client=None):
      """
      @param iface: QGIS interface object
      @param mode: describe process or execute mode
      @param RADids: additional ids passed from previous process
      @param inputs: dictionary with inputs, keys are argument names in the 
      client library
      """
      QDialog.__init__(self)
      #self.setWindowFlags(self.windowFlags() & Qt.WindowMinimizeButtonHint)
      self.setupUi()
      self.client = client
      cc = self.rejectBut
      bok = self.acceptBut
      self.inputs = inputs
      self.expId = inputs['expId']
      _Controller.__init__(self, iface, cancel_close=cc, okayButton=bok, ids=RADids,
                           initializeWithData=False, client=client)
      
# .............................................................................       
   def accept(self):
      valid = self.validate()  
      if valid:   
         self.inputGroup.hide()      
         self.statuslabel.setText('Running Process')
         self.progressbar.reset()
         self.outputGroup.setTitle('Outputs')
         self.outputGroup.show()
         if self.inputs is not None:
            self.keyvalues.update(self.inputs)
         
         self.startThread(EXECUTE_REQUEST,outputfunc = self.verifyRandom, 
                          requestfunc=self.client.rad.randomizeBucket, client=self.client,
                          inputs=self.keyvalues)
      else:
         pass
         
# ............................................................................. 
   def validate(self):
         """
         @summary: Validates the inputs for the dialog
         """
         valid = True
         message = ""
         self.keyvalues = {}
         if self.splotchCheck.isChecked():
            self.keyvalues['method'] = 'splotch'
         elif self.swapCheck.isChecked():
            self.keyvalues['method'] = 'swap'          
            self.keyvalues['numSwaps'] = str(self.iterationsEdit.text())
            if len(self.iterationsEdit.text()) <= 0:
               message = "Please supply number of swaps"
               valid = False
         
         
                   
         
         if not valid:
            msgBox = QMessageBox.information(self,
                                                   "Problem...",
                                                   message,
                                                   QMessageBox.Ok)
         return valid 
# .............................................................................       
   def verifyRandom(self,model,items):
      
      message = "Randomization successful" 
          
      
   
# .............................................................................         
   def help(self):
      self.help = QWidget()
      self.help.setWindowTitle('Lifemapper Help')
      self.help.resize(600, 400)
      self.help.setMinimumSize(600,400)
      self.help.setMaximumSize(1000,1000)
      layout = QVBoxLayout()
      helpDialog = QTextBrowser()
      helpDialog.setOpenExternalLinks(True)
      #helpDialog.setSearchPaths(['documents'])
      helppath = os.path.dirname(os.path.realpath(__file__))+'/documents/help.html'
      helpDialog.setSource(QUrl.fromLocalFile(helppath))
      helpDialog.scrollToAnchor('randomizePAM')
      layout.addWidget(helpDialog)
      self.help.setLayout(layout)
      if self.isModal():
         self.setModal(False)
      self.help.show()       
      
      
      
      
      
      
      
      
      
      
      
      