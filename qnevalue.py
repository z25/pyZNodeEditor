# Copyright (c) 2015, ALDO HOEBEN
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

class QNEValue(QGraphicsTextItem):
    (Type) = (QGraphicsItem.UserType +4)

    def __init__(self, parent):
        super(QNEValue, self).__init__(parent)

        self.setTextWidth(-1)
        self.setZValue(1)

        self.port = None
        self.value = None


    def __del__(self):
        #print("Del QNEValue %s" % self.name)
        pass


    def setPort(self, port):
        self.port = port


    def setAccess(self, access):
        if 'r' in access:
            self.setVisible(True)
        else:
            self.setVisible(False)

        if 'w' in access:
            self.setTabChangesFocus(True)
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
        else:
            self.setTabChangesFocus(False)
            self.setTextInteractionFlags(Qt.NoTextInteraction)


    def port(self):
        return self.port


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.clearFocus()
        else:
            super(QNEValue, self).keyPressEvent(event)


    def focusInEvent(self, event):
        super(QNEValue, self).focusInEvent(event)
        self.setPlainText(self.value)


    def focusOutEvent(self, event):
        super(QNEValue, self).focusOutEvent(event)
        value = self.toPlainText()
        if self.value != value:
            port = self.port;
            block = self.port.block()
            block.nodeEditor().onChangeValue(block, port, value)
        self.showValue(self.value)


    def showValue(self, value):
        self.value = value

        value_ = value
        if len(value) > 9:
            value_ = value[:6] + "..."
        self.setPlainText(value_)
