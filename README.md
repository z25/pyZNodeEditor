pyZNodeEditor
=============
A monitor/editor for ZOCP nodes, implemented in PySide (Python/Qt4). 
ZOCP is the Z25 Orchestration Control Protocol, currently in 
development at z25.org. For more information see https://github.com/z25/pyZOCP


Installation Notes
------------------
pyZNodeEditor has a submodule for saving/loading network configurations named pyZConfigManager. Make sure the zconfigmanager folder contains the required files.
If you are cloning a copy from git, be sure to add the --recursive option:
```
git clone --recursive https://github.com/z25/pyZNodeEditor.git
```
If you have previously checked out a copy of the editor, you can add the files by executing the following commands in the pyZNodeEditor folder:
```
git submodule init
git submodule update
```

pyZNodeEditor depends on the python implementation of ZOCP. You must first install pyZOCP:
https://github.com/z25/pyZOCP/blob/master/README.textile
To get the pyNodeEditor up and running you need to install the following:

* PySide (https://github.com/PySide/pyside-setup)

The instructions below all assume you have Python 3 and pyZOCP already installed.


Installation on Debian/Ubuntu
-----------------------------
1. Install PySide:
```
sudo apt-get install python3-pyside
```

Installation on Windows
-----------------------
1. Install PySide:
```
pip install PySide
```

Installation on OSX
-------------------
To use PySide on OSX you also need to install QT version 4.6 or better (Qt 5.x is currently not supported)

1. Download and install QT (http://download.qt.io/archive/qt/4.8/4.8.6/)
2. Install PySide:
```
pip3 install PySide
```


Running pyZNodeEditor
---------------------
```
python3 zne.py
```
Note: the node editor is useless by itself. It needs to run alongside one or more ZOCP nodes. ZOCP nodes can not be created using the editor.


pyQNodesEditor
--------------
pyZNodeEditor is based on a Python port of ALGOholic's QNodesEditor
See ALGOholic for more information:
http://algoholic.eu/qnodeseditor-qt-nodesports-based-data-processing-flow-editor/
The original port can be found here:
https://github.com/fieldOfView/pyQNodesEditor
