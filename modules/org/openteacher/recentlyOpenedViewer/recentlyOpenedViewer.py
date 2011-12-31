#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Milan Boers
#
#	This file is part of OpenTeacher.
#
#	OpenTeacher is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenTeacher is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui
import weakref

class RecentlyOpenedModel(QtCore.QAbstractListModel):
	def __init__(self, modules, *args, **kwargs):
		super(RecentlyOpenedModel, self).__init__(*args, **kwargs)
		
		self._modules = modules
		
		self._items = []

	def columnCount(self, parent=None):
		return 1

	def rowCount(self, parent=None):
		return len(self._items)

	def data(self, index, role):
		if not index.isValid():
			return
		item = self._items[index.row()]
		if role == QtCore.Qt.DisplayRole:
			return item["label"]
		elif role == QtCore.Qt.DecorationRole:
			if item.has_key("item"):
				return QtGui.QPixmap(item["icon"])

	def update(self, items):
		self.beginResetModel()
		self._items = items
		self.endResetModel()

	def open(self, row):
		item = self._items[row]
		print item
		
		module = self._modules.default(
			*item["moduleArgsSelector"],
			**item["moduleKwargsSelector"]
		)
		
		method = getattr(module, item["method"])
		
		method(
			*item["args"],
			**item["kwargs"]
		)

class RecentlyOpenedListView(QtGui.QListView):
	def __init__(self, modules, *args, **kwargs):
		super(RecentlyOpenedListView, self).__init__(*args, **kwargs)

		self.setModel(RecentlyOpenedModel(modules))
		self.doubleClicked.connect(self._doubleClicked)

	def _doubleClicked(self, index):
		self.model().open(index.row())

class RecentlyOpenedViewer(QtGui.QGroupBox):
	def __init__(self, modules, *args, **kwargs):
		super(RecentlyOpenedViewer, self).__init__(*args, **kwargs)

		self.listView = RecentlyOpenedListView(modules)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.listView)
		self.setLayout(layout)

	def retranslate(self):
		self.setTitle(_("Recently opened:"))

class RecentlyOpenedViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(RecentlyOpenedViewerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.requires = (
			self._mm.mods(type="recentlyOpened"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)

		self.type = "recentlyOpenedViewer"

	def enable(self):
		self.active = True

		self._viewers = set()

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self._recentlyOpened = self._modules.default(
			"active",
			type="recentlyOpened"
		)
		self._recentlyOpened.updated.handle(self._update)

	def _retranslate(self):
		#Translations
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		for viewer in self._viewers:
			ref = viewer()
			if ref is not None:
				ref.retranslate()

	def disable(self):
		self.active = False

		del self._modules
		del self._viewers

	def createViewer(self):
		viewer = RecentlyOpenedViewer(self._modules)
		recentlyOpened = self._recentlyOpened.getRecentlyOpened()
		
		viewer.listView.model().update(recentlyOpened)
		self._viewers.add(weakref.ref(viewer))
		return viewer

	def _update(self):
		data = self._recentlyOpened.getRecentlyOpened()
		for viewer in self._viewers:
			ref = viewer()
			if ref is not None:
				ref.listView.model().update(data)

def init(moduleManager):
	return RecentlyOpenedViewerModule(moduleManager)
