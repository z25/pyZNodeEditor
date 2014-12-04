#!/usr/bin/python3

from PySide.QtCore import (Qt, QSocketNotifier)
from PySide.QtGui import (QPainter, QBrush, QPalette)
from PySide.QtGui import (QApplication, QMainWindow, QAction, QWidget,
    QGraphicsItem, QGraphicsScene, QGraphicsView)

from zocp import ZOCP
import zmq

import logging

from qnodeseditor import QNodesEditor
from qneblock import QNEBlock
from qneport import QNEPort

class QNEMainWindow(QMainWindow):
    def __init__(self, parent):
        super(QNEMainWindow, self).__init__(parent)

        self.logger = logging.getLogger("zne")
        self.logger.setLevel(logging.INFO)

        self.setMinimumSize(640,480)
        self.setWindowTitle("ZOCP Node Editor")

        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush( QApplication.palette().window() )

        self.view = QGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        self.nodesEditor = QNodesEditor(self)
        self.nodesEditor.install(self.scene)

        self.nodesEditor.onAddConnection = self.onAddConnection
        self.nodesEditor.onRemoveConnection = self.onRemoveConnection

        self.scale = 1
        self.installActions()

        self.initZOCP()

        self.nodes = {}


    def closeEvent(self, *args):
        self.zocp.stop()


    def installActions(self):
        quitAct = QAction("&Quit", self, shortcut="Ctrl+Q",
            statusTip="Exit the application", triggered=self.close)

        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(quitAct)

        # for shortcuts
        self.view.addAction(quitAct)

        selectAllAct = QAction("Select &All", self, shortcut="Ctrl+A",
            triggered=self.nodesEditor.selectAll)
        selectInverseAct = QAction("Select &Inverse", self, shortcut="Ctrl+I",
            triggered=self.nodesEditor.selectInverse)
        deleteSelectedAct = QAction("&Delete Selected", self, shortcut="Del",
            triggered=self.nodesEditor.deleteSelected)

        editMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(selectAllAct)
        editMenu.addAction(selectInverseAct)
        editMenu.addSeparator()
        editMenu.addAction(deleteSelectedAct)

        self.view.addAction(selectAllAct)
        self.view.addAction(selectInverseAct)
        self.view.addAction(deleteSelectedAct)

        zoomInAct = QAction("Zoom &In", self, shortcut="Ctrl++",
            triggered=self.zoomIn)
        zoomOutAct = QAction("Zoom &Out", self, shortcut="Ctrl+-",
            triggered=self.zoomOut)
        zoomResetAct = QAction("&Reset Zoom", self, shortcut="Ctrl+0",
            triggered=self.zoomReset)

        viewMenu = self.menuBar().addMenu("&View")
        viewMenu.addAction(zoomInAct)
        viewMenu.addAction(zoomOutAct)
        viewMenu.addSeparator()
        viewMenu.addAction(zoomResetAct)

        self.view.addAction(zoomInAct)
        self.view.addAction(zoomOutAct)
        self.view.addAction(zoomResetAct)


    def zoomIn(self):
        if self.scale < 4:
            self.scale *= 1.2
            self.view.scale(1.2, 1.2)


    def zoomOut(self):
        if self.scale > 0.1:
            self.scale /= 1.2
            self.view.scale(1/1.2, 1/1.2)


    def zoomReset(self):
        self.scale = 1
        self.view.setTransform(QTransform())


    #########################################
    # Node editor callbacks
    #########################################
    def onAddConnection(self, connection, fromPort, toPort):
        fromBlock = fromPort.block()
        toBlock = toPort.block()

        emitter = ("%s@%s" % (fromPort.portName(), fromBlock.uuid().hex))
        receiver = ("%s@%s" % (toPort.portName(), toBlock.uuid().hex))

        self.zocp.peer_subscribe(toBlock.uuid(), emitter, receiver)

        self.logger.debug("added subscription from %s on %s to %s on %s" %
               (fromPort.portName(), fromBlock.name(), toPort.portName(), toBlock.name()))


    def onRemoveConnection(self, connection, fromPort, toPort):
        fromBlock = fromPort.block()
        toBlock = toPort.block()

        emitter = ("%s@%s" % (fromPort.portName(), fromBlock.uuid().hex))
        receiver = ("%s@%s" % (toPort.portName(), toBlock.uuid().hex))

        self.zocp.peer_unsubscribe(toBlock.uuid(), emitter, receiver)

        self.logger.debug("removed subscription from %s on %s to %s on %s" %
               (fromPort.portName(), fromBlock.name(), toPort.portName(), toBlock.name()))


    def onBlockMove(self, block, position):
        peer = block.uuid()
        self.zocp.peer_set(peer, {"_zne_position": position})


    #########################################
    # ZOCP implementation
    #########################################
    def initZOCP(self):
        import socket

        self.zocp = ZOCP()
        self.zocp.set_name("ZOCP Node Editor@%s" % socket.gethostname())
        self.notifier = QSocketNotifier(
            self.zocp.inbox.getsockopt(zmq.FD),
            QSocketNotifier.Read)
        self.notifier.setEnabled(True)
        self.notifier.activated.connect(self.onZOCPEvent)
        self.zocp.on_peer_enter = self.onPeerEnter
        self.zocp.on_peer_exit = self.onPeerExit
        self.zocp.on_peer_modified = self.onPeerModified
        self.zocp.on_peer_signaled = self.onPeerSignaled
        self.zocp.start()

        zl = logging.getLogger("zocp")
        zl.setLevel(logging.INFO)


    def onZOCPEvent(self):
        self.zocp.run_once(0)


    def onPeerEnter(self, peer, name, *args, **kwargs):
        # Subscribe to any and all value changes
        self.zocp.peer_subscribe(peer)

        # Add named block; ports are not known at this point
        node = {}
        node["block"] = QNEBlock(None)
        self.scene.addItem(node["block"])
        node["block"].setName(name)
        node["block"].setUuid(peer)
        node["block"].addPort(name, False, False, QNEPort.NamePort)
        node["block"].onBlockMove = self.onBlockMove
        node["ports"] = dict()

        self.nodes[peer.hex] = node


    def onPeerExit(self, peer, name, *args, **kwargs):
        # Unsibscribe from value changes
        self.zocp.peer_unsubscribe(peer)

        # Remove block
        if peer.hex in self.nodes:
            self.nodes[peer.hex]["block"].delete()
            self.nodes.pop(peer.hex)


    def onPeerModified(self, peer, data, *args, **kwargs):
        for portname in data:
            if "access" not in data[portname]:
                # Metadata, not a capability
                if portname == "_zne_position":
                    pos = data[portname]
                    block = self.nodes[peer.hex]["block"]
                    block.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, False)
                    block.setPos(pos[0], pos[1])
                    block.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
                continue

            if portname not in self.nodes[peer.hex]["ports"]:
                hasInput = "s" in data[portname]["access"]
                hasOutput = "e" in data[portname]["access"]
                port = {}
                port["port"] = self.nodes[peer.hex]["block"].addPort(portname, hasInput, hasOutput)
                port["caps"] = data[portname]
                self.nodes[peer.hex]["ports"][portname] = port
            else:
                #TODO: modify existing port
                pass


    def onPeerSignaled(self, peer, data, *args, **kwargs):
        pass



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    widget = QNEMainWindow(None)
    widget.show()

    sys.exit(app.exec_())
