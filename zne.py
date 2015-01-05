#!/usr/bin/python3

from PySide.QtCore import (Qt, QSocketNotifier)
from PySide.QtGui import (QPainter, QBrush, QPalette, QIcon, QTransform)
from PySide.QtGui import (QApplication, QMainWindow, QMessageBox, QAction,
    QWidget, QGraphicsItem, QGraphicsScene, QGraphicsView)

from zocp import ZOCP
import zmq

import logging

from qnodeseditor import QNodesEditor
from qneblock import QNEBlock
from qneport import QNEPort
from qneconnection import QNEConnection

class QNEMainWindow(QMainWindow):
    def __init__(self, parent):
        super(QNEMainWindow, self).__init__(parent)

        self.logger = logging.getLogger("zne")
        self.logger.setLevel(logging.INFO)

        self.setMinimumSize(560,360)
        self.setWindowTitle("ZOCP Node Editor")
        self.setWindowIcon(QIcon('assets/icon.png'))

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        self.nodesEditor = QNodesEditor(self, self.scene, self.view)

        self.nodesEditor.onAddConnection = self.onAddConnection
        self.nodesEditor.onRemoveConnection = self.onRemoveConnection
        self.nodesEditor.onBlockMoved = self.onBlockMoved

        self.scale = 1
        self.installActions()

        self.initZOCP()

        self.nodes = {}
        self.pendingSubscribers = {}


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
        selectNoneAct = QAction("Select &None", self, shortcut="Ctrl+D",
            triggered=self.nodesEditor.selectNone)
        selectInverseAct = QAction("Select &Inverse", self, shortcut="Ctrl+I",
            triggered=self.nodesEditor.selectInverse)
        deleteSelectedAct = QAction("&Delete Selected", self, shortcut="Del",
            triggered=self.nodesEditor.deleteSelected)

        editMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(selectAllAct)
        editMenu.addAction(selectNoneAct)
        editMenu.addAction(selectInverseAct)
        editMenu.addSeparator()
        editMenu.addAction(deleteSelectedAct)

        self.view.addAction(selectAllAct)
        self.view.addAction(selectNoneAct)
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

        aboutAct = QAction("&About", self,
             triggered=self.about)

        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction(aboutAct)

        self.view.addAction(aboutAct)


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


    def about(self):
        QMessageBox.about(self, "About ZOCP Node Editor",
            "<p>A monitor/editor for ZOCP nodes, implemented in PySide"
             "(Python/Qt4).</p><p>ZOCP is the Z25 Orchestration Control "
             "Protocol, currently in development at "
             "<a href='http://z25.org'>z25.org</a></p>")


    #########################################
    # Node editor callbacks
    #########################################
    def onAddConnection(self, connection, fromPort, toPort):
        fromBlock = fromPort.block()
        toBlock = toPort.block()

        emitter = toPort.portName()
        emit_peer = toBlock.uuid()
        receiver = fromPort.portName()
        recv_peer = fromBlock.uuid()

        self.zocp.signal_subscribe(recv_peer, receiver, emit_peer, emitter)

        self.logger.debug("added subscription from %s on %s to %s on %s" %
               (receiver, toBlock.name(), emitter, fromBlock.name()))


    def onRemoveConnection(self, connection, fromPort, toPort):
        fromBlock = fromPort.block()
        toBlock = toPort.block()

        emitter = toPort.portName()
        emit_peer = toBlock.uuid()
        receiver = fromPort.portName()
        recv_peer = fromBlock.uuid()

        self.zocp.signal_unsubscribe(recv_peer, receiver, emit_peer, emitter)

        self.logger.debug("removed subscription from %s on %s to %s on %s" %
               (receiver, toBlock.name(), emitter, fromBlock.name()))


    def onBlockMoved(self, block):
        pos = block.pos()
        peer = block.uuid()
        self.zocp.peer_set(peer, {"_zne_position": [pos.x(), pos.y()]})


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
        self.zocp.signal_subscribe(self.zocp.get_uuid(), None, peer, None)

        # Add named block; ports are not known at this point
        node = {}
        node["block"] = QNEBlock(None)
        self.scene.addItem(node["block"])
        node["block"].setName(name)
        node["block"].setUuid(peer)
        node["block"].addPort(name, False, False, QNEPort.NamePort)
        node["block"].setVisible(False)
        node["ports"] = dict()

        self.nodes[peer.hex] = node


    def onPeerExit(self, peer, name, *args, **kwargs):
        # Unsubscribe from value changes
        self.zocp.signal_unsubscribe(self.zocp.get_uuid(), None, peer, None)

        # Remove block
        if peer.hex in self.nodes:
            self.nodes[peer.hex]["block"].delete()
            self.nodes.pop(peer.hex)


    def onPeerModified(self, peer, name, data, *args, **kwargs):
        for portname in data:
            portdata = data[portname]

            if portname not in self.nodes[peer.hex]["ports"]:
                if "access" in portdata:
                    hasInput = "s" in portdata["access"]
                    hasOutput = "e" in portdata["access"]
                    port = self.nodes[peer.hex]["block"].addPort(portname, hasInput, hasOutput)
                    port.setValue(str(portdata["value"]))
                    self.nodes[peer.hex]["ports"][portname] = port

                else:
                    # Metadata, not a capability
                    if portname == "_zne_position":
                        block = self.nodes[peer.hex]["block"]
                        block.setPos(portdata[0], portdata[1])

            else:
                port = self.nodes[peer.hex]["ports"][portname]
                if "value" in portdata:
                    port.setValue(str(portdata["value"]))

            if "subscribers" in portdata:
                self.updateSubscribers(port, portdata["subscribers"])

        if len(self.nodes[peer.hex]["ports"]) > 0:
            self.nodes[peer.hex]["block"].setVisible(True)
        self.updatePendingSubscribers(peer)


    def onPeerSignaled(self, peer, name, data, *args, **kwargs):
        [portname, value] = data
        if portname in self.nodes[peer.hex]["ports"]:
            self.nodes[peer.hex]["ports"][portname].setValue(str(value))


    def updateSubscribers(self, port, subscribers):
        port1 = port.outputPort

        # check if any current connections should be removed
        connections = port.connections()
        for connection in connections:
            if(connection.port1().isOutput()):
                port2 = connection.port2()
            else:
                port2 = connection.port1()
            subscriber = [port2.block().uuid().hex, port2.portName()]
            if subscriber not in subscribers:
                connection.delete()

        # add new connections for new subscriptions
        for subscriber in subscribers:
            [uuid, portname] = subscriber
            if uuid in self.nodes:
                node = self.nodes[uuid]
                if portname in node["ports"]:
                    port2 = node["ports"][portname]
                    if not port2.isConnected(port1):
                        # create new connection
                        connection = QNEConnection(None)
                        connection.setPort1(port1)
                        connection.setPort2(port2)
                        connection.updatePosFromPorts()
                        connection.updatePath()
                        self.scene.addItem(connection)
                    continue

            # if the connection could not be made yet, add it to a list of
            # pending subscriber-connections
            if uuid not in self.pendingSubscribers:
                self.pendingSubscribers[uuid] = []
            self.pendingSubscribers[uuid].append([port1, portname])


    def updatePendingSubscribers(self, peer):
        if peer.hex in self.pendingSubscribers:
            for subscriber in self.pendingSubscribers[peer.hex]:
                [port1, portname] = subscriber
                if peer.hex in self.nodes and portname in self.nodes[peer.hex]["ports"]:
                    port2 = self.nodes[peer.hex]["ports"][portname]

                    connection = QNEConnection(None)
                    connection.setPort1(port1)
                    connection.setPort2(port2)
                    connection.updatePosFromPorts()
                    connection.updatePath()
                    self.scene.addItem(connection)
                else:
                    # TODO: handle case where port is still not available
                    pass

            self.pendingSubscribers.pop(peer.hex)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    widget = QNEMainWindow(None)
    widget.show()

    sys.exit(app.exec_())
