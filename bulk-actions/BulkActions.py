# -*- coding: utf-8 -*-

"""
Bulk Actions
------------
Licensed under the GNU GPL v3.0 terms
"""

import os
import re
import webbrowser
import json
import base64

from functools import partial
from enum import IntEnum
#from enum import Enum

from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase, Krita

from PyQt5.QtCore import (
    QSize,
)

from PyQt5.QtGui import (
    QPixmap,
    QIcon,
)
from PyQt5.QtWidgets import (
    QScrollArea,
    QPushButton,
    QToolButton,
    QStatusBar,
    QLabel,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QWidget,
)

from .KritaNode import KritaNode

from .UI import QHLine

from .Utils import kickstart, flip
from .Utils.Tree import iterPre

KI = Krita.instance()

def remap(oldValue, oldMin, oldMax, newMin, newMax):
    # Linear conversion
    if oldMin == newMin and oldMax == newMax:
        return oldValue;
    return (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin;

def clamp(value, clamp_min, clamp_max):
    return min(clamp_max, max(clamp_min, value))

def openHelp():
    webbrowser.open("https://github.com/Larpon/krita-bulk-actions", new=0, autoraise=True)


class BulkActionType(IntEnum):
    BOOL = 0
    SET = 1

class BulkAction(IntEnum):
    BOOL_VISIBLE = 0
    BOOL_LOCKED = 1
    BOOL_ALPHA_LOCKED = 2
    BOOL_COLLAPSED = 3
    BOOL_INHERIT_ALPHA = 4
    SET_OPACITY = 5

class BulkActionBaseWidget(QWidget):
    type = BulkActionType.BOOL
    hblayout = None

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.hblayout = QHBoxLayout(self)
        self.hblayout.setContentsMargins(2, 2, 2, 2)

    def doAction(self):
        raise NotImplementedError()

    def settings(self):
        raise NotImplementedError()

    def loadSettings(self, settings):
        raise NotImplementedError()

class BulkSetActionWidget(BulkActionBaseWidget):
    type = BulkActionType.SET
    index = 0
    matchLineEdit = QLineEdit()
    actionsComboBox = QComboBox()

    def __init__(self, parent=None):
        BulkActionBaseWidget.__init__(self, parent=parent)

        self.actionsComboBox = QComboBox()
        self.actionsComboBox.addItem('Opacity', BulkAction.SET_OPACITY)

        self.matchLineEdit = QLineEdit()
        self.matchLineEdit.setText('')
        self.matchLineEdit.setPlaceholderText('pattern')


        self.valueLineEdit = QLineEdit()
        self.valueLineEdit.setText('')
        self.valueLineEdit.setPlaceholderText('0 - 100%')
        self.valueLineEdit.setFixedWidth(55)

        applyButton = QToolButton()
        applyButton.setIcon(QIcon.fromTheme("checkmark"))

        applyButton.released.connect(
            partial(self.doAction, self.actionsComboBox, self.matchLineEdit, self.valueLineEdit)
        )

        self.actionsComboBox.activated.connect(
            partial(self.actionsComboBoxActivated, self.actionsComboBox)
        )
        self.matchLineEdit.returnPressed.connect(
            partial(self.doAction, self.actionsComboBox, self.matchLineEdit, self.valueLineEdit)
        )

        self.valueLineEdit.returnPressed.connect(
            partial(self.doAction, self.actionsComboBox, self.matchLineEdit, self.valueLineEdit)
        )

        self.hblayout.addWidget(applyButton)
        self.hblayout.addWidget(self.actionsComboBox)
        self.hblayout.addWidget(self.valueLineEdit)
        self.hblayout.addWidget(self.matchLineEdit)

    def actionsComboBoxActivated(self, combo):
        index = combo.currentIndex()
        self.index = index

    def settings(self):
        return { 'index': self.actionsComboBox.currentIndex(), 'match': self.matchLineEdit.text(), 'value': self.valueLineEdit.text() }

    def loadSettings(self, settings):
        self.actionsComboBox.setCurrentIndex(settings['index'])
        self.matchLineEdit.setText(settings['match'])
        self.valueLineEdit.setText(settings['value'])

    def doAction(self, comboBox, lineEdit, valueEdit):

        doc = KI.activeDocument()
        if doc == None:
            return

        try:
            action_type = comboBox.itemData(comboBox.currentIndex())
            value_text = valueEdit.text()
            match_text = lineEdit.text()
            numbers = re.compile('\d+(?:\.\d+)?')
            value_text = numbers.findall(value_text)[0]
            if value_text == '':
                value_text = '100'
            value_text = clamp(float(value_text),0,100)
            value_text = int(remap(value_text,0.0,100.0,0,255))

            root = doc.rootNode()
            root = KritaNode(root)
            it = iterPre(root)

            if match_text == "":
                nodes = KI.activeWindow().activeView().selectedNodes()
                it = map(partial(KritaNode), nodes)
            else:
                it = filter(lambda n: n.match(lineEdit.text()), it)

            def setOpacity(n):
                n.raw.setOpacity(value_text)

            if action_type is BulkAction.SET_OPACITY:
                it = map(setOpacity, it)

            kickstart(it)
            doc.refreshProjection()
        except ValueError as e:
            print(e)

class BulkBoolActionWidget(BulkActionBaseWidget):
    type = BulkActionType.BOOL
    index = 0
    matchLineEdit = QLineEdit()
    actionsComboBox = QComboBox()

    def __init__(self, parent=None):
        BulkActionBaseWidget.__init__(self, parent=parent)

        self.actionsComboBox = QComboBox()
        self.actionsComboBox.addItem('Visible', BulkAction.BOOL_VISIBLE)
        self.actionsComboBox.addItem('Locked', BulkAction.BOOL_LOCKED)
        self.actionsComboBox.addItem('Alpha Locked', BulkAction.BOOL_ALPHA_LOCKED)
        self.actionsComboBox.addItem('Collapsed', BulkAction.BOOL_COLLAPSED)
        self.actionsComboBox.addItem('Inherit Alpha', BulkAction.BOOL_INHERIT_ALPHA)
        #self.actionsComboBox.insertSeparator(5)
        #self.actionsComboBox.addItem(QIcon.fromTheme("edit-rename"),'Opacity', BulkAction.INT_OPACITY)

        #self.actionsComboBox.addItem('Opacity 100%', 3)

        self.matchLineEdit = QLineEdit()
        self.matchLineEdit.setText('')
        self.matchLineEdit.setPlaceholderText('pattern')

        applyButton = QToolButton()
        applyButton.setIcon(QIcon.fromTheme("view-refresh"))

        applyButton.released.connect(
            partial(self.doAction, self.actionsComboBox, self.matchLineEdit)
        )

        self.actionsComboBox.activated.connect(
            partial(self.actionsComboBoxActivated, self.actionsComboBox)
        )
        self.matchLineEdit.returnPressed.connect(
            partial(self.doAction, self.actionsComboBox, self.matchLineEdit)
        )

        self.hblayout.addWidget(applyButton)
        self.hblayout.addWidget(self.actionsComboBox)
        self.hblayout.addWidget(self.matchLineEdit)

    def actionsComboBoxActivated(self, combo):
        index = combo.currentIndex()
        self.index = index

    def settings(self):
        return { 'index': self.actionsComboBox.currentIndex(), 'match': self.matchLineEdit.text() }

    def loadSettings(self, settings):
        self.actionsComboBox.setCurrentIndex(settings['index'])
        self.matchLineEdit.setText(settings['match'])

    def doAction(self, comboBox, lineEdit):

        doc = KI.activeDocument()
        if doc == None:
            return

        #msg, timeout = (cfg["done"]["msg"].format("Renaming successful!"), cfg["done"]["timeout"])
        try:
            action_type = comboBox.itemData(comboBox.currentIndex())
            match_text = lineEdit.text()
            #print('Action type',action_type)
            doc = KI.activeDocument()
            root = doc.rootNode()
            root = KritaNode(root)

            it = iterPre(root)

            if match_text == "":
                nodes = KI.activeWindow().activeView().selectedNodes()
                it = map(partial(KritaNode), nodes)
            else:
                it = filter(lambda n: n.match(lineEdit.text()), it)

            def toggleVisible(n):
                n.setVisible(not n.visible())
            def toggleLock(n):
                n.setLocked(not n.locked())
            def toggleAlphaLocked(n):
                n.raw.setAlphaLocked(not n.raw.alphaLocked())
            def toggleCollapsed(n):
                n.raw.setCollapsed(not n.raw.collapsed())
                #print('Setting',n.name,'collapsed',n.raw.collapsed())
            def toggleInheritAlpha(n):
                n.raw.setInheritAlpha(not n.raw.inheritAlpha())

            if action_type is BulkAction.BOOL_VISIBLE:
                it = map(toggleVisible, it)
            if action_type is BulkAction.BOOL_LOCKED:
                it = map(toggleLock, it)
            if action_type is BulkAction.BOOL_ALPHA_LOCKED:
                it = map(toggleAlphaLocked, it)
            if action_type is BulkAction.BOOL_COLLAPSED:
                it = map(toggleCollapsed, it)
            if action_type is BulkAction.BOOL_INHERIT_ALPHA:
                it = map(toggleInheritAlpha, it)

            kickstart(it)
            doc.refreshProjection()
        except ValueError as e:
            print(e)
            #msg, timeout = cfg["error"]["msg"].format(e), cfg["error"]["timeout"]
        #statusBar.showMessage(msg, timeout)

class BulkActionsDockWidget(DockWidget):
    title = "Bulk Actions"
    listLayout = QVBoxLayout()
    actions = list()

    def __init__(self):
        super().__init__()
        KI.setBatchmode(True)
        self.setWindowTitle(self.title)
        self.createInterface()

    def isPluginSettingsLayer(self, n):
        return n.isGroupLayer() and n.name == 'Plugin Settings'

    def isSettingsLayer(self, n):
        return n.name == 'Bulk Actions' and self.isPluginSettingsLayer(n.parent)

    def clearBulkActions(self):
        self.actions = list()
        while self.listLayout.count():
            child = self.listLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addNewBulkAction(self, bulk_action_type, settings=None):

        removeButton = QToolButton()
        removeButton.setIcon(QIcon.fromTheme("list-remove"))

        bulkActionWidget = None

        if bulk_action_type == BulkActionType.BOOL:
            bulkActionWidget = BulkBoolActionWidget()
        elif bulk_action_type == BulkActionType.SET:
            bulkActionWidget = BulkSetActionWidget()
        else:
            raise NotImplementedError()

        if settings is not None:
            bulkActionWidget.loadSettings(settings)

        widget = QWidget()

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.addWidget(bulkActionWidget)
        hBoxLayout.addWidget(removeButton)

        widget.setLayout(hBoxLayout)
        #self.listLayout.addWidget(widget)
        self.listLayout.insertWidget(0,widget)

        self.actions.append(bulkActionWidget)

        def removeBulkAction():
            self.actions.remove(bulkActionWidget)
            widget.deleteLater()

        removeButton.clicked.connect( partial(removeBulkAction) )

    def hasSettings(self):

        doc = KI.activeDocument()
        if doc == None:
            return False

        # TODO The following works but it's saved in kritarc - we want a way to save it with the document
        #entry = Application.readSetting('bulkActionsPlugin', 'settings', None)
        #return entry is not None

        root = doc.rootNode()
        root = KritaNode(root)

        it = iterPre(root)
        it = filter(self.isSettingsLayer, it)

        l = list(it)

        if len(l) == 0:
            return False

        children = l[0].children

        if len(children) == 0:
            return False
        return True

    def loadSettings(self):
        #print('Loading...')

        doc = KI.activeDocument()
        if doc == None:
            return

        # TODO The following works but it's saved in kritarc - we want a way to save it with the document
        #entry = Application.readSetting('bulkActionsPlugin', 'settings', None)
        #return entry is not None
        #decoded = Application.readSetting('bulkActionsPlugin', 'settings', None)
        #decoded = base64.b64decode(decoded).decode('utf-8')
        #return json.loads(decoded)

        decoded = None


        root = doc.rootNode()
        root = KritaNode(root)

        it = iterPre(root)

        it = filter(self.isSettingsLayer, it)

        l = list(it)
        if len(l) == 0:
            return None

        children = l[0].children

        if len(children) == 0:
            return None
        else:
            dataLayer = children[0]
            dataLayer.setLocked(False)
            decoded = dataLayer.name
            decoded = base64.b64decode(decoded).decode('utf-8')
            dataLayer.setLocked(True)

        #print('Loaded',decoded)
        return json.loads(decoded)

    def loadAndApplySettings(self):
        if self.hasSettings():
            self.clearBulkActions()
            settings = self.loadSettings()
            if settings['version'] == 1.0:
                for actionSetting in settings['actions']:
                    self.addNewBulkAction(BulkActionType.BOOL,actionSetting)
            if settings['version'] == 1.1:
                for actionSetting in settings['actions']:
                    #print(actionSetting, actionSetting['type'],  BulkActionType(actionSetting['type']))
                    self.addNewBulkAction(BulkActionType(actionSetting['type']), actionSetting['settings'])

    def saveSettings(self):

        doc = KI.activeDocument()
        if doc == None:
            return

        #msg, timeout = (cfg["done"]["msg"].format("Renaming successful!"), cfg["done"]["timeout"])
        try:
            bulkActions = []
            for ba in self.actions:
                bulkActions.append( { 'settings': ba.settings(), 'type': ba.type.value } )
            data = json.dumps({ 'version': 1.1, 'actions':bulkActions }, separators=(',', ':'))
            encodedBytes = base64.b64encode(data.encode("utf-8"))
            encoded = str(encodedBytes, "utf-8")

            #print(data)
            #return

            # TODO The following works but it's saved in kritarc - we want a way to save it with each document
            #Application.writeSetting('bulkActionsPlugin', 'settings', encoded)

            root = doc.rootNode()
            root = KritaNode(root)

            it = iterPre(root)

            it = filter(self.isPluginSettingsLayer, it)
            if len(list(it)) == 0:
                gl = doc.createGroupLayer('Plugin Settings')
                gl.setVisible(False)
                gl.setCollapsed(True)
                gl.setLocked(True)
                doc.rootNode().addChildNode(gl, doc.rootNode().childNodes()[0])

            it = iterPre(root)
            it = filter(self.isSettingsLayer, it)

            if len(list(it)) == 0:
                gl = doc.createGroupLayer('Bulk Actions')
                gl.setVisible(False)
                gl.setCollapsed(True)
                gl.setLocked(True)
                it = iterPre(root)
                it = filter(self.isPluginSettingsLayer, it)
                list(it)[0].raw.addChildNode(gl, None)

            it = iterPre(root)
            it = filter(self.isSettingsLayer, it)

            children = list(it)[0].children

            if len(children) == 0:
                gl = doc.createGroupLayer(encoded)
                gl.setVisible(False)
                gl.setLocked(True)
                it = iterPre(root)
                it = filter(self.isSettingsLayer, it)
                list(it)[0].raw.addChildNode(gl, None)
            else:
                dataLayer = children[0]
                dataLayer.setLocked(False)
                dataLayer.raw.setName(encoded)
                dataLayer.setLocked(True)

            #print('Saved',base64.b64decode(encoded).decode('utf-8'))
            #for i in list(it):
            #    print('Hep',type(i),i)

            #str.encode('base64','strict')

            #kickstart(it)
            doc.refreshProjection()
        except ValueError as e:
            print(e)


    def createInterface(self):
        uiContainer = QWidget(self)

        #for path in QIcon.themeSearchPaths():
        #    print("%s/%s" % (path, QIcon.themeName()))

        helpButton = QToolButton() # self.title+" Help"
        helpButton.setIcon(QIcon.fromTheme("help-contents"))

        addBoolButton = QToolButton()
        addBoolButton.setIcon(QIcon.fromTheme("view-refresh"))

        addSetButton = QToolButton()
        addSetButton.setIcon(QIcon.fromTheme("checkmark"))

        helpHBoxLayout = QHBoxLayout()
        helpHBoxLayout.addWidget(QLabel("Add action"))
        helpHBoxLayout.addWidget(addBoolButton)
        helpHBoxLayout.addWidget(addSetButton)
        helpHBoxLayout.addStretch()
        helpHBoxLayout.addWidget(helpButton)

        saveButton = QPushButton('Save')
        loadButton = QPushButton('Load')
        clearButton = QPushButton('Clear')

        settingsHBoxLayout = QHBoxLayout()
        #settingsHBoxLayout.addWidget(QLabel("Settings"))
        settingsHBoxLayout.addWidget(saveButton)
        settingsHBoxLayout.addWidget(loadButton)
        settingsHBoxLayout.addWidget(clearButton)

        saveButton.clicked.connect(
            partial(self.saveSettings)
        )

        loadButton.clicked.connect(
            partial(self.loadAndApplySettings)
        )

        clearButton.clicked.connect(
            partial(self.clearBulkActions)
        )

        listWidget = QWidget()
        listWidget.setLayout(self.listLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(listWidget)
        scrollArea.setWidgetResizable(True)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(helpHBoxLayout)
        mainLayout.addWidget(QHLine())
        mainLayout.addWidget(scrollArea)
        mainLayout.addLayout(settingsHBoxLayout)

        helpButton.clicked.connect(
            partial(openHelp)
        )


        # Extremly weird bug where clicks on the buttons call the wrong method?
        addBoolButton.clicked.connect(
            partial(self.addNewBulkAction, BulkActionType.BOOL, None )
        )

        addSetButton.clicked.connect(
            partial(self.addNewBulkAction, BulkActionType.SET, None )
        )

        uiContainer.setLayout(mainLayout)
        self.setWidget(uiContainer)

    def canvasChanged(self, canvas):
        pass


def registerDocker():
    docker = DockWidgetFactory(
        "pykrita_bulk_actions", DockWidgetFactoryBase.DockRight, BulkActionsDockWidget
    )
    KI.addDockWidgetFactory(docker)
