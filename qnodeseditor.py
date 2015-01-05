# Copyright (c) 2014, ALDO HOEBEN
# Copyright (c) 2012, STANISLAW ADASZEWSKI
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of STANISLAW ADASZEWSKI nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL STANISLAW ADASZEWSKI BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from PySide.QtCore import (Qt, QObject, QEvent, QSizeF, QRectF, QPointF)
from PySide.QtGui import (QBrush, QPen, QPainter, QPainterPath, QPixmap)
from PySide.QtGui import (QApplication, QGraphicsView, QGraphicsItem,
    QGraphicsPathItem, QGraphicsSceneMouseEvent)

from qneblock import QNEBlock
from qneport import QNEPort
from qneconnection import QNEConnection

class QNodesEditor(QObject):
    def __init__(self, parent, scene, view):
        super(QNodesEditor, self).__init__(parent)

        self.scene = scene
        self.scene.installEventFilter(self)

        gridSize = 25
        gridMap = QPixmap(gridSize,gridSize)
        gridPainter = QPainter(gridMap)
        gridPainter.fillRect(0,0,gridSize,gridSize, QApplication.palette().window().color().darker(103))
        gridPainter.fillRect(1,1,gridSize-2,gridSize-2, QApplication.palette().window())
        gridPainter.end()
        self.scene.setBackgroundBrush( QBrush(gridMap) )

        originSize = 50
        originItem = QGraphicsPathItem()
        path = QPainterPath()
        path.moveTo(0,-originSize)
        path.lineTo(0,originSize)
        path.moveTo(-originSize,0)
        path.lineTo(originSize,0)
        originItem.setPath(path)
        originItem.setPen(QPen(QApplication.palette().window().color().darker(110),2))
        self.scene.addItem(originItem)

        self.view = view
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.connection = None


    def selectNone(self):
        for item in self.scene.items():
            if item.type() == QNEBlock.Type or item.type() == QNEConnection.Type:
                item.setSelected(False)


    def selectAll(self):
        for item in self.scene.items():
            if item.type() == QNEBlock.Type or item.type() == QNEConnection.Type:
                item.setSelected(True)


    def selectInverse(self):
        for item in self.scene.items():
            if item.type() == QNEBlock.Type or item.type() == QNEConnection.Type:
                item.setSelected(not item.isSelected())


    def deleteSelected(self):
        for item in self.scene.items():
            if (item.isSelected() and item.type() == QNEConnection.Type):
                port1 = item.port1()
                port2 = item.port2()
                if port1.isOutput():
                    self.onRemoveConnection(item, port1, port2)
                else:
                    self.onRemoveConnection(item, port2, port1)
                item.delete()


    def itemAt(self, position):
        items = self.scene.items(QRectF( position - QPointF(2,2) , QSizeF(4,4) ))

        for item in items:
            if item.type() > QGraphicsItem.UserType:
                return item

        return None


    def eventFilter(self, object, event):
        if event.type() == QEvent.GraphicsSceneMousePress:
            self.mousePressOnBlock = False
            self.mouseDragged = False

            if event.button() == Qt.LeftButton:
                item = self.itemAt(event.scenePos())
                if item and item.type() == QNEPort.Type:
                    self.view.setDragMode(QGraphicsView.NoDrag)
                    self.connection = QNEConnection(None)
                    self.scene.addItem(self.connection)

                    self.connection.setPort1(item)
                    self.connection.setPos1(item.scenePos()+QPointF(item.radius(),0))
                    self.connection.setPos2(event.scenePos())
                    self.connection.updatePath()

                    self.selectNone()
                    return True

                elif item and item.type() == QNEBlock.Type:
                    self.mousePressOnBlock = True
                    return False

        elif event.type() == QEvent.GraphicsSceneMouseMove:
            if self.connection:
                self.connection.setPos2(event.scenePos())
                self.connection.updatePath()
                return True

            else:
                self.mouseDragged = True
                return False

        elif event.type() == QEvent.GraphicsSceneMouseRelease:
            if self.connection and event.button() == Qt.LeftButton:
                self.view.setDragMode(QGraphicsView.RubberBandDrag)

                item = self.itemAt(event.scenePos())
                if item and item.type() == QNEPort.Type:
                    port1 = self.connection.port1()
                    port2 = item

                    if port1.block() != port2.block() and port1.isOutput() != port2.isOutput() and not port1.isConnected(port2):

                        self.connection.setPos2(port2.scenePos())
                        self.connection.setPort2(port2)
                        self.connection.updatePath()
                        if port1.isOutput():
                            self.onAddConnection(self.connection, port1, port2)
                        else:
                            self.onAddConnection(self.connection, port2, port1)

                        self.connection = None
                        return True

                self.connection.delete()
                self.connection = None
                return True

            elif event.button() == Qt.LeftButton:
                if self.mousePressOnBlock and self.mouseDragged:
                    for item in self.scene.selectedItems():
                        if item.type() == QNEBlock.Type:
                            self.onBlockMoved(item)


        return super(QNodesEditor, self).eventFilter(object, event)


    def onAddConnection(self, connection, fromPort, toPort):
        print ("Added connection from %s on %s to %s on %s" %
               (fromPort.portName(), fromPort.block().name(), toPort.portName(), toPort.block().name()))
        

    def onRemoveConnection(self, connection, fromPort, toPort):
        print ("Removed connection from %s on %s to %s on %s" % 
               (fromPort.portName(), fromPort.block().name(), toPort.portName(), toPort.block().name()))


    def onBlockMoved(self, block):
        print ("Block %s moved" % block.name())
