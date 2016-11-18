Lifemappers tools is the core package when installed (prepared for distribution must be the top directory)


COMMON FOLDER -- shared libraries just GERMANE to Qt and QGIS, for shared class factory required for QGIS, communication between dialogs using PyQt signals,
color ramps, QListModel subclasses, matplotlib module for range diversity plots, model module for modle in Model View Controller used
for WPS and normal http calls to client library, allows threading against LmClient library where calls can provide some feedback to user, mostly for certain types
of asychronous call, slowly being phased out, QT Tree (tree folder, not phyo trees) item models and data model, and workspace module, and hint service module. Local pluginconstansts just germaine to plugin

CONFIG FOLDER -- config stuff, used mainly for preferences

ICONS  -- compiled resource files using pyrcc4 per Qt requirement, images for resources

LmShared -- LmClient and LmCommon

Tools -- all dialog code. dialog code is all MVC,  View modules (ui visual components only)  all begin with ui_*.  With a few exceptions where
ui components were small and could be easily exist in a separate class in the controller module. All ui code uses PyQT for Qt4.x. The controller code itself are non ui_* prefixed.
Every controller module inherits from its appropriate ui. This follows normal QGIS plugin protocols and conventions. The controller code works with the data
model to inform the view in the ui view modules.  Communication between dialogs is achieved through signals and the communication module which also ties
the menu system in common/metools.  treeWeb.html is d3 javascript for achieiving fluid tree visualization communication between it
and python in the MVC is achieved with a built in bridge kit in Qt.

metadata.txt -- required metadata for QGIS plugin repository and installation using plugin maganager in QGIS.

New experiment MultiSps folder in tools directory is a new organizational strucure for all MultiSps functionality in one dialog but still 
follows MVC code pattern.

