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
	def __init__(self, updates, rememberChoice, *args, **kwargs):
		super(UpdatesDialog, self).__init__(*args, **kwargs)

		label = QtGui.QLabel(ngettext(
			"There is %s update available, do you want to update?",
			"There are %s updates available, do you want to update?",
			len(updates)
		) % len(updates))
		self.checkBox = QtGui.QCheckBox(_("Remember my choice"))
		self.checkBox.setChecked(rememberChoice)
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

	@property
	def rememberChoice(self):
		return self.checkBox.isChecked()

class UpdatesDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UpdatesDialogModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "updatesDialog"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="updates"),
			self._mm.mods(type="settings"),
			self._mm.mods(type="dataStore"),
		)

	def enable(self):
		modules = set(self._mm.mods("active", type="modules")).pop()
		self._dataStore = modules.default("active", type="dataStore").store
		settings = modules.default("active", type="settings")
		self._rememberChoiceSetting = settings.registerSetting(**{#FIXME: translate all these...
			"internal_name": "org.openteacher.updatesDialog.rememberChoice",
			"name": "Remember if the user wants to install updates or not",
			"type": "boolean",
			"category": "Updates",
			"defaultValue": False,
		})
		self._dataStore["org.openteacher.updatesDialog.userDidUpdatesLastTime"] = False
		self.active = True

		if self._rememberChoiceSetting["value"] and not self._dataStore["org.openteacher.updatesDialog.userDidUpdatesLastTime"]:
			#The user doesn't want to be bothered with updates
			return
		self._updatesMod = modules.default("active", type="updates")
		try:
			updates = self._updatesMod.updates
		except IOError:
			return #FIXME possibly :P

		if not updates:
			return

		#FIXME: should the updatesDialog check for new updates, or another module?
		if self._rememberChoiceSetting["value"] and self._dataStore["org.openteacher.updatesDialog.userDidUpdatesLastTime"]:
			self._updatesMod.update()
		else:
			self._ud = UpdatesDialog(updates, self._rememberChoiceSetting["value"])
			self._tab = modules.default("active", type="ui").addCustomTab(
				self._ud.windowTitle(), #FIXME: retranslate, including dialog itself
				self._ud
			)
			self._tab.closeRequested.handle(self._ud.rejected.emit)
			self._ud.accepted.connect(self._accepted)
			self._ud.rejected.connect(self._rejected)

	def _accepted(self):
		self._rememberChoiceSetting["value"] = self._ud.rememberChoice
		self._tab.close()
		self._updatesMod.update()
		self._dataStore["org.openteacher.updatesDialog.userDidUpdatesLastTime"] = True

	def _rejected(self):
		self._rememberChoiceSetting["value"] = self._ud.rememberChoice
		self._tab.close()
		self._dataStore["org.openteacher.updatesDialog.userDidUpdatesLastTime"] = False

	def disable(self):
		self.active = False
		
		del self._ud
		del self._tab
		del self._updatesMod
		del self._dataStore

def init(moduleManager):
	return UpdatesDialogModule(moduleManager)
