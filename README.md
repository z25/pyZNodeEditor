pyZNodeEditor
=============
A monitor/editor for ZOCP nodes, implemented in PySide (Python/Qt4). 
ZOCP is the Z25 Orchestration Control Protocol, currently in 
development at z25.org

pyQNodesEditor
--------------
pyZNodeEditor is based on a Python port of ALGOholic's QNodesEditor  
See ALGOholic for more information:  
http://algoholic.eu/qnodeseditor-qt-nodesports-based-data-processing-flow-editor/  
The original port can be found here:  
https://github.com/fieldOfView/pyQNodesEditor  

Installing
----------

pyZNodeEditor is based on a special branch of ZOCP, which will be merged
in the near future. For now you need the special branch.
Depending on wheter you installed ZOCP through git, or with pip,
do the following. Note that you may also need to update pyre,
since that changed a lot over the past few weeks.

If you previously installed ZOCP through git, do the following
in the folder you cloned pyZOCP into:
```
> git remote add fieldofview https://github.com/fieldOfView/pyZOCP.git
> git checkout -b feature_subscribe
> git pull fieldofview feature_subscribe
```
Now you should be able to use ZOCP as before, but you will notice
some new examples in the examples folder. If you want to go back
to the "normal" version of ZOCP without my changes, do the
following:
```
> git checkout master
```

If you previously used pip to install ZOCP, upgrade to my special
branch like so:
```
> sudo pip3 install -- upgrade https://github.com/fieldOfView/pyZOCP/archive/feature_subscribe.zip
```
Switching back to the normal ZOCP is done as follows:
```
> sudo pip3 install -- upgrade https://github.com/z25/pyZOCP/archive/master.zip
```

Next, clone pyZNodeEditor somewhere:
```
> git clone https://github.com/fieldOfView/pyZNodeEditor.git
```
Or just download it here:
https://github.com/fieldOfView/pyZNodeEditor/archive/master.zip

pyZNodeEditor requires PySide and Python3. On linux you can install
PySide for Python3 as follows:
```
> sudo apt-get install python3-pyside
```
