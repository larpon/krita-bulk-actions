# -*- coding: utf-8 -*-
import os
import re

from collections import OrderedDict

from krita import Krita

KI = Krita.instance()

class KritaNode:
    """
    Wrapper around Krita's Node class, that represents a layer.
    Adapted from https://github.com/GDquest/krita-batch-exporter/blob/0a21f34942794e12ebdab86f74860379169f6f77/krita_batch_exporter/Infrastructure.py#L28
    """

    def __init__(self, node):
        self.node = node

    def __bool__(self):
        return bool(self.node)

    @property
    def name(self):
        name = self.node.name()
        return name

    @property
    def raw(self):
        return self.node

    @property
    def parent(self):
        return KritaNode(self.node.parentNode())

    @property
    def children(self):
        return [KritaNode(n) for n in self.node.childNodes()]

    @property
    def type(self):
        return self.node.type()

    @property
    def position(self):
        bounds = self.node.bounds()
        return bounds.x(), bounds.y()

    @property
    def bounds(self):
        bounds = self.node.bounds()
        return bounds.x(), bounds.y(), bounds.width(), bounds.height()

    @property
    def size(self):
        bounds = self.node.bounds()
        return bounds.width(), bounds.height()

    def isLayer(self):
        return "layer" in self.type

    def isMask(self):
        return "mask" in self.type

    def isPaintLayer(self):
        return self.type == "paintlayer"

    def isGroupLayer(self):
        return self.type == "grouplayer"

    def isFileLayer(self):
        return self.type == "filelayer"

    def isFilterLayer(self):
        return self.type == "filterlayer"

    def isFillLayer(self):
        return self.type == "filllayer"

    def isCloneLayer(self):
        return self.type == "clonelayer"

    def isVectorLayer(self):
        return self.type == "vectorlayer"

    def isTransparencyMask(self):
        return self.type == "transparencyMask"

    def isFilterMask(self):
        return self.type == "filtermask"

    def isTransformMask(self):
        return self.type == "transformmask"

    def isSelectionMask(self):
        return self.type == "selectionmask"

    def isColorizeMask(self):
        return self.type == "colorizemask"

    def match(self, m):
        name = self.node.name()
        return m in name

    def setVisible(self, visibility):
        self.node.setVisible(visibility)

    def toggleVisible(self, node):
        self.node.setVisible(not self.node.visible())

    def setLocked(self, lock):
        self.node.setLocked(lock)

    def toggleLocked(self, node):
        self.node.setLocked(not self.node.locked())

    def visible(self):
        return self.node.visible()

    def locked(self):
        return self.node.locked()
