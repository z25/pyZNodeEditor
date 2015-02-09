pyZNodeEditor
=============
A monitor/editor for ZOCP nodes, implemented in PySide (Python/Qt4). 
ZOCP is the Z25 Orchestration Control Protocol, currently in 
development at z25.org see for more infromation: https://github.com/z25/pyZOCP

pyQNodesEditor
--------------
pyZNodeEditor is based on a Python port of ALGOholic's QNodesEditor  
See ALGOholic for more information:  
http://algoholic.eu/qnodeseditor-qt-nodesports-based-data-processing-flow-editor/  
The original port can be found here:  
https://github.com/fieldOfView/pyQNodesEditor 


Installation Notes
--------------
To get the pyNodeEditor up and running you need to install the following:

* PySide (https://github.com/PySide/pyside-setup)

Note: If you want to install PySide on OSX you will also need to install QT version 4.6 or better (Qt 5.x is currently not supported)

Quick Instalaltion on OSX
--------------
assuming you have python 3 installed..

1. Download and install QT (http://download.qt.io/archive/qt/4.8/4.8.6/)
2. Install PySide
```
pip3 install PySide
```