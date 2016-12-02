Lifemappers tools is the core package when installed in QGIS (prepared for distribution must be the top directory)

OverView of code by folder
==========================


Common Folder
------------------
Shared libraries just germane to Qt and QGIS, for shared class factory required for QGIS, communication between dialogs using PyQt signals,
color ramps, QListModel subclasses, matplotlib module for range diversity plots, model module for modle in Model View Controller used
for WPS and normal http calls to client library, allows threading against LmClient library where calls can provide some feedback to user, mostly for certain types
of asychronous call, slowly being phased out, QT Tree (tree folder, not phyo trees) item models and data model, and workspace module, and hint service module. Local pluginconstansts just germaine to plugin

Config Folder
------------------
config stuff, used mainly for preferences

Icons 
--------
compiled resource files using pyrcc4 per Qt requirement, images for resources
 
LmShared 
-------- 
LmClient and LmCommon

Tools 
--------

all dialog code. dialog code is all MVC,  View modules (ui visual components only)  all begin with ui_*.  With a few exceptions where
ui components were small and could be easily exist in a separate class in the controller module. All ui code uses PyQT for Qt4.x. The controller code itself are non ui_* prefixed.
Every controller module inherits from its appropriate ui. This follows normal QGIS plugin protocols and conventions. The controller code works with the data
model to inform the view in the ui view modules.  Communication between dialogs is achieved through signals for 
the menu system in common/metools.  treeWeb.html is d3 javascript for achieiving fluid tree visualization communication between it
and python in the MVC is achieved with a built in bridge kit in Qt.

Metadata.txt
------------------
required metadata for QGIS plugin repository and installation using plugin maganager in QGIS.


MultiSps Folder
------------------
New experiment MultiSps folder in tools directory is a new organizational strucure for all MultiSps functionality in one dialog but still 
follows MVC code pattern.  This will replace close to 1/3 or more of existing code.  It is organized by "page" of 
functionality, e.g. (Stats subfolder) will contain both controller and ui for access to stats outputs. 


Operational Details
===================

Menu System
------------------

The module metools.py in common is the core plugin instance, in so far as the main __init__.py at the top level of the plugin has a required classFactory method that takes the QGIS iface object as an arg and returns an instance of MetoolsPlugin from metools. The MetoolsPlugin class initializes the Qmenu GUI and assigns Qt actions to items and subitems in submenus.  These actions initialize dialogs and open them either as modal or non-modal depending on whether or not the user needs to complete dialog inputs before moving on or whether they need to be able to interact with QGIS.  Upon initialization of the main menu GUI
several custom PyQT signals from the Communicate module in common are connected to methods. These signals and their methods send communication from state changes from dialogs, like changes to current experiment information, to the menu system, and as the user opens experiments and their constituent parts the main menuing system evolves (enables different functionality) so that a user can use new menu items to get back to important parts of the current experiment. This helps to control the workflow and gives easy access directly to data once an experiment is opened and it's grids (buckets) are opened, rather than have to go back through the bucket listing tool.  

**iface QGIS object**

The iface QGIS object `https://qgis.org/api/classQgisInterface.html#details <http://>`_
is the instance of the QgisInterface Class made available to plugins. Only QGIS functionality exposed by QgisInterface can be used in plugins. It is provided automatically to the class factory by the plugin manager, and is passed to the instance of the MetoolsPlugin and from there to the dialogs for interaction with QGIS.


Dialogs and their connections
-----------------------------

**Overview**

Dialogs are initially opened from menu items.  If the workflow requires an additional dialog, 
the current dialog will spawn the new dialog for those actions.  The naming convention for controllesr vs
(Views), i.e. ui components is mentioned above.  Other naming conventions for controllers are controllers
starting with "list" are dialogs that use the listing services. Listing dialogs can have other functions
then just listing, for example listing RAD experiments is the way that select a Grid (Bucket) and get the
listing dialog for the buckets in that experiment, and from there by selecting a bucket the buckets listing
can  get the stats dialog for that bucket.  For RAD most of this is going away and should be duplicated in
the MultiSps structure mentioned above. All of the functionality for a stock SDM experiment is contained
in the postSDMExp.py controller and it's ui is called ui_postSDMExp.py.






