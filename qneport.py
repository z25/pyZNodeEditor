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


from PySide.QtCore import (Qt, QSize)
from PySide.QtGui import (QBrush, QColor, QPainter, QPainterPath, QPen,
    QFontMetrics)
from PySide.QtGui import (QApplication, QGraphicsItem, QGraphicsPathItem, 
    QGraphicsTextItem)

from qnevalue import QNEValue

class QNEPort(QGraphicsPathItem):
    (NamePort, TypePort) = (1, 2)
    (Type) = (QGraphicsItem.UserType +1)

    def __init__(self, parent):
        super(QNEPort, self).__init__(parent)

        self.label = QGraphicsTextItem(self)
        self.radius_ = 4
        self.margin = 3
        self.widgetWidth = 50

        self.setPen(QPen(QApplication.palette().text().color(), 1))
        self.setBrush(QApplication.palette().highlight())
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        
        self.valueText = QNEValue(self)
        self.valueText.setPort(self)

        self.outputPort = QNEOutputPort(self)

        self.m_portFlags = 0
        self.hasInput_ = False
        self.hasOutput_ = False

        self.m_block = None
        self.m_connections = []


    def __del__(self):
        #print("Del QNEPort %s" % self.name)
        pass


    def delete(self):
        for connection in self.m_connections:
            connection.delete()
        if self.scene():
            self.scene().removeItem(self)
        self.m_block = None
        self.m_connections = []


    def setName(self, name):
        self.name = name
        self.label.setPlainText(name)
        self.label.setPos(self.radius_ + self.margin, -self.label.boundingRect().height()/2)


    def setValue(self, value):
        self.value = value
        self.valueText.showValue(value)


    def setAccess(self, access):
        self.valueText.setAccess(access)


    def setCanConnect(self, hasInput, hasOutput):
        self.hasInput_ = hasInput
        self.hasOutput_ = hasOutput

        if self.hasOutput_:
            self.outputPort.setVisible(True)
        else:
            self.outputPort.setVisible(False)

        path = QPainterPath()
        if self.hasInput_:
            path.addEllipse(0, -self.radius_, 2*self.radius_, 2*self.radius_)
        else:
            pass
        self.setPath(path)


    def setWidth(self, width):
        self.outputPort.setPos(width, 0)
        self.valueText.setPos(width - self.widgetWidth - self.radius_ - self.margin,
                              -self.valueText.boundingRect().height()/2)

        
    def setNEBlock(self, block):
        self.m_block = block


    def setPortFlags(self, flags):
        self.m_portFlags = flags

        if self.m_portFlags & self.TypePort:
            font = self.scene().font()
            font.setItalic(True)
            self.label.setFont(font)
            self.valueText.setVisible(False)
            self.setPath(QPainterPath())
        elif self.m_portFlags & self.NamePort:
            font = self.scene().font()
            font.setBold(True)
            self.label.setFont(font)
            self.valueText.setVisible(False)
            self.setPath(QPainterPath())


    def innerSize(self):
        fontmetrics = QFontMetrics(self.scene().font())
        height = fontmetrics.height()
        width = fontmetrics.width(self.name)

        if self.m_portFlags == 0:
            width = width + self.widgetWidth

        return QSize(width, height)


    def type(self):
        return self.Type


    def radius(self):
        return self.radius_


    def portName(self):
        return self.name


    def hasInput(self):
        return self.hasInput_


    def hasOutput(self):
        return self.hasOutput_


    def isInput(self):
        return True


    def isOutput(self):
        return False


    def block(self):
        return self.m_block


    def portFlags(self):
        return self.m_portFlags
	

    def addConnection(self, connection):
        self.m_connections.append(connection)


    def removeConnection(self, connection):
        try:
            self.m_connections.remove(connection)
        except: pass


    def connections(self):
        return self.m_connections


    def isConnected(self, other):
        for connection in self.m_connections:
            if connection.port1() == other or connection.port2() == other:
                return True

        return False


    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            for connection in self.m_connections:
                connection.updatePosFromPorts()
                connection.updatePath()

        return value


class QNEOutputPort(QGraphicsPathItem):
    (Type) = (QGraphicsItem.UserType +1)

    def __init__(self, parent):
        super(QNEOutputPort, self).__init__(parent)
        self.parent = parent
        
        self.setPen(self.parent.pen())
        self.setBrush(self.parent.brush())
        
        radius_ = parent.radius_
        
        path = QPainterPath()
        path.addEllipse(0, -radius_, 2*radius_, 2*radius_)
        self.setPath(path)


    def type(self):
        return self.Type


    def addConnection(self, connection):
        self.parent.addConnection(connection)


    def removeConnection(self, connection):
        self.parent.removeConnection(connection)


    def isInput(self):
        return False


    def isOutput(self):
        return True


    def hasInput(self):
        return self.parent.hasInput()


    def hasOutput(self):
        return self.parent.hasInput()


    def block(self):
        return self.parent.block()


    def isConnected(self, other):
        return self.parent.isConnected(other)


    def radius(self):
        return self.parent.radius()


    def portName(self):
        return self.parent.portName()
