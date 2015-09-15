
from qgis.core import *
from qgis.gui import *

uri = 'file:///home/jcavner/Pooka8/WhiteBelliedRat_627/pam.csv?type=csv&skipEmptyFields=Yes&xField=centerX&yField=centerY&spatialIndex=no&subsetIndex=no&watchFile=no'
l = QgsVectorLayer(uri,'fdasfa','delimitedtext')
print l.isValid()