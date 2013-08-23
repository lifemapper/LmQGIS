def name():
   return "Lifemapper Macroecology Tools"

def description():
   return "Lifemapper web services-based presence absence matrix tools"

def version():
   return "Version 1.0.0"

def qgisMinimumVersion(): 
   return "1.7"

def author():
   return "Jeffery A. Cavner"

def email():
   return "lifemapper@ku.edu"

def classFactory(iface):
   from lifemapperTools.common.metools import MetoolsPlugin
   return MetoolsPlugin(iface)
