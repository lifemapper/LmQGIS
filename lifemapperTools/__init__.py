"""
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
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LmShared'))
configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.ini')

# # Set the LIFEMAPPER_CONFIG_FILE environment variable
os.environ["LIFEMAPPER_CONFIG_FILE"] = configPath


def name():
   return "Lifemapper Macroecology Tools"

def description():
   return "Lifemapper web services-based presence absence matrix tools"

def version():
   return "Version 2.3.1"

def qgisMinimumVersion(): 
   return "2.6"

def author():
   return "Jeffery A. Cavner"

def email():
   return "lifemapper@ku.edu"

def classFactory(iface):
    
   from lifemapperTools.common.metools import MetoolsPlugin
   return MetoolsPlugin(iface)
