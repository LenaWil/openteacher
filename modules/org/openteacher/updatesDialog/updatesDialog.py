#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

_, ngettext = unicode, lambda x, y, n: x if n == 1 else y #FIXME, including retranslation

#class UpdatesListModel(QtCore.QAbstractTableModel):
#	def __init__(self, updates, *args, **kwargs):
#		super(UpdatesListModel, self).__init__(*args, **kwargs)
#		
#		self._updates = updates
#		for update in self._updates:
#			update["toBeInstalled"] = QtCore.Qt.Checked
#
#	def columnCount(self, parent):
#		return 2
#
#	def rowCount(self, parent):
#		return len(self._updates)
#
#	def flags(self, *args, **kwargs):
#		return (
#			super(UpdatesListModel, self).flags(*args, **kwargs) |
#			QtCore.Qt.ItemIsUserCheckable
#		)
#
#	def data(self, index, role=QtCore.Qt.DisplayRole):
#		if not index.isValid():
#			return
#		update = self._updates[index.row()]
#		if role == QtCore.Qt.CheckStateRole:
#			return update["toBeInstalled"]
#		elif role == QtCore.Qt.DisplayRole:
#			if index.column() == 0:
#				return "\n".join([
#					update["name"],
#					update["timestamp"].strftime("%x")
#				])
#			elif index.column() == 1:
#				return update["description"]
#
#	def setData(self, index, value, role=QtCore.Qt.EditRole):
#		if not index.isValid() or role != QtCore.Qt.CheckStateRole:
#			return False
#
#		self._updates[index.row()]["toBeInstalled"] = value
#		return True
#
#class UpdatesDialog(QtGui.QDialog):
#	def __init__(self, updates, *args, **kwargs):
#		super(UpdatesDialog, self).__init__(*args, **kwargs)
#
#		self.descriptionWidget = QtGui.QLabel()
#		self.descriptionWidget.setWordWrap(True)
#		self.model = UpdatesListModel(updates)
#
#		listView = QtGui.QListView()
#		listView.setModel(self.model)
#		listView.selectionModel().currentChanged.connect(
#			self.updateDescription
#		)
#
#		splitter = QtGui.QSplitter()
#		splitter.addWidget(listView)
#		splitter.addWidget(self.descriptionWidget)
#
#		buttonBox = QtGui.QDialogButtonBox()
#		buttonBox.addButton(_("Install selection"), QtGui.QDialogButtonBox.AcceptRole)
#		buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
#
#		buttonBox.accepted.connect(self.accept)
#		buttonBox.rejected.connect(self.reject)
#
#		layout = QtGui.QVBoxLayout()
#		layout.addWidget(splitter)
#		layout.addWidget(buttonBox)
#		self.setLayout(layout)
#
#		self.setWindowTitle(_("Updates"))
#
#	def updateDescription(self, new, old):
#		i = self.model.createIndex(new.row(), 1)
#		try:
#			self.descriptionWidget.setText(self.model.data(i))
#		except TypeError:
#			pass

class UpdatesDialog(QtGui.QDialog):
	def __init__(self, updates, *args, **kwargs):
		super(UpdatesDialog, self).__init__(*args, **kwargs)

		label = QtGui.QLabel(ngettext(
			"There is %s update available, do you want to update?",
			"There are %s updates available, do you want to update?",
			len(updates)
		) % len(updates))
		self.checkBox = QtGui.QCheckBox(_("Remember my choice"))
		buttonBox = QtGui.QDialogButtonBox(
			QtGui.QDialogButtonBox.No |
			QtGui.QDialogButtonBox.Yes
		)
		buttonBox.button(QtGui.QDialogButtonBox.Yes).setAutoDefault(True)
		buttonBox.button(QtGui.QDialogButtonBox.No).setAutoDefault(False)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(label)
		layout.addStretch()
		layout.addWidget(self.checkBox)
		layout.addWidget(buttonBox)
		
		self.setLayout(layout)
		self.setWindowTitle(ngettext(
			"Update available",
			"Updates available",
			len(updates)
		))

class UpdatesDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UpdatesDialogModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "updatesDialog"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="updates"),
			self._mm.mods(type="settings"),
		)

	def enable(self):
		modules = set(self._mm.mods("active", type="modules")).pop()
		settings = modules.default("active", type="settings")
		settings.registerSetting(#FIXME: translate all these...
			"org.openteacher.updatesDialog.rememberChoice",
			"Ask permission to update (or not)",
			type="boolean",
			category="Updates",
			defaultValue=False
		)
		settings.registerSetting(
			"org.openteacher.updatesDialog.doUpdates",
			"Update automatically",
			type="boolean",
			category="Updates",
			defaultValue=True
		)
		self.active = True

		if not settings.value("org.openteacher.updatesDialog.doUpdates"):
			return
		updatesMod = modules.default("active", type="updates")
		try:
			updates = updatesMod.updates
		except IOError:
			return #FIXME possibly :P

		if not updates:
			return

		#FIXME: should the updatesDialog check for new updates, or another module?
		if settings.value("org.openteacher.updatesDialog.rememberChoice"):
			updatesMod.update()
		else:
			ud = UpdatesDialog(updates)
			tab = modules.default("active", type="ui").addCustomTab(
				ud.windowTitle(), #FIXME: retranslate, including dialog itself
				ud
			)
			#FIXME: change the value of 'rememberChoice'
			tab.closeRequested.handle(tab.close)
			ud.accepted.connect(tab.close)
			ud.rejected.connect(tab.close)
			ud.accepted.connect(updatesMod.update)

	def disable(self):
		self.active = False

def init(moduleManager):
	return UpdatesDialogModule(moduleManager)
