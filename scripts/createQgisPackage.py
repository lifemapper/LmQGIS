"""
@summary: This module creates a zip file for a plugin that can be uploaded to 
             the QGIS repository.
@author: CJ Grady
@status: alpha
@version: 1.0
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
import fnmatch
import os
import re
from zipfile import ZipFile
import ConfigParser
import itertools
import StringIO
from LmCommon.common.config import Config

# Jeff: Change these to the locations on your system
IN_DIR = "/home/jcavner/workspace/lm3/components/LmClient/LmQGIS/V2/"
OUT_LOCATION = "/home/jcavner/plugin/V2/lifemapperTools_Testdfsdf2.zip"
#CONFIG_LOCATION = "/home/jcavner/workspace/lm3/components/config/lmconfigfile.jeff"
#SITE_CONFIG = "/home/jcavner/workspace/lm3/components/config/config.site.ini"
SECTIONS = ['LmClient - contact','LmCommon - common','LmClient - Open Tree of Life','SiteConfig']
EXCLUDES = ['.svn', '*.pyc','*.ini']

# .............................................................................
def getFilenames(inDir):
   """
   @summary: Gets all of the files and directories in the input directory that
                don't match the exclude patterns
   @param inDir: The input directory to find files in
   """
   excludes = r'|'.join([fnmatch.translate(x) for x in EXCLUDES]) or r'$.'

   matches = []
   for root, dirnames, fns in os.walk(inDir, topdown=True, followlinks=True):
      dirnames[:] = [d for d in dirnames if d not in excludes]
      
      files = [os.path.join(root, f) for f in fns]
      files = [f for f in files if not re.match(excludes, f)]
      matches.extend(files)
   return matches

# .............................................................................
def createZipFile(matches, inDir, outFn, configStrIO):
   """
   @summary: Creates a zip file containing all of the files in matches
   @param matches: Files to include in the zip file
   @param inDir: The base directory for these files.  The zip file will store
                    the directory structure under this location
   @param outFn: The output zip file name to use
   """
   with ZipFile(outFn, mode='w') as zf:
      for fn in matches:
         zf.write(fn, fn[len(inDir):])
      zf.writestr('lifemapperTools/config/config.ini', configStrIO.getvalue())
      
def getConfigSections():
   #config = ConfigParser.SafeConfigParser()
   config = Config().config
   #config.read(CONFIG_LOCATION)
   #config.read(SITE_CONFIG)
   allSec = {}
   for sec in SECTIONS:
      allSec[sec] = config.items(sec)
   
   return allSec
      
def createNewConfig(sections):
   newConfig = ConfigParser.SafeConfigParser()
   for key in sections.keys():
      newConfig.add_section(key)
      for  k,v in sections[key]:
         newConfig.set(key,k,v)  
   output = StringIO.StringIO()
   newConfig.write(output)
   return output
   
# .............................................................................
if __name__ == "__main__":
   
   #print Config().config
   
   filenames = getFilenames(IN_DIR)
   sections = getConfigSections()
   configStr = createNewConfig(sections)
   createZipFile(filenames, IN_DIR, OUT_LOCATION,configStr)
   
