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

_, ngettext = unicode, unicode #FIXME

class UpdatesListModel(QtCore.QAbstractTableModel):
	def __init__(self, updates, *args, **kwargs):
		super(UpdatesListModel, self).__init__(*args, **kwargs)
		
		self._updates = updates
		for update in self._updates:
			update["toBeInstalled"] = QtCore.Qt.Checked

	def columnCount(self, parent):
		return 2

	def rowCount(self, parent):
		return len(self._updates)

	def flags(self, *args, **kwargs):
		return (
			super(UpdatesListModel, self).flags(*args, **kwargs) |
			QtCore.Qt.ItemIsUserCheckable
		)

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not index.isValid():
			return
		update = self._updates[index.row()]
		if role == QtCore.Qt.CheckStateRole:
			return update["toBeInstalled"]
		elif role == QtCore.Qt.DisplayRole:
			if index.column() == 0:
				return "\n".join([
					update["name"],
					update["timestamp"].strftime("%x")
				])
			elif index.column() == 1:
				return update["description"]

	def setData(self, index, value, role=QtCore.Qt.EditRole):
		if not index.isValid() or role != QtCore.Qt.CheckStateRole:
			return False

		self._updates[index.row()]["toBeInstalled"] = value
		return True

class UpdatesDialog(QtGui.QDialog):
	def __init__(self, updates, *args, **kwargs):
		super(UpdatesDialog, self).__init__(*args, **kwargs)

		self.descriptionWidget = QtGui.QLabel()
		self.descriptionWidget.setWordWrap(True)
		self.model = UpdatesListModel(updates)

		listView = QtGui.QListView()
		listView.setModel(self.model)
		listView.selectionModel().currentChanged.connect(
			self.updateDescription
		)

		splitter = QtGui.QSplitter()
		splitter.addWidget(listView)
		splitter.addWidget(self.descriptionWidget)

		buttonBox = QtGui.QDialogButtonBox()
		buttonBox.addButton(_("Install selection"), QtGui.QDialogButtonBox.AcceptRole)
		buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)

		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(splitter)
		layout.addWidget(buttonBox)
		self.setLayout(layout)

		self.setWindowTitle(_("Updates"))

	def updateDescription(self, new, old):
		i = self.model.createIndex(new.row(), 1)
		try:
			self.descriptionWidget.setText(self.model.data(i))
		except TypeError:
			pass

class UpdatesDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UpdatesDialogModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "updatesDialog"
		self.requires = (
			self._mm.mods(type="updates"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.active = True

		self.ud = UpdatesDialog(self._modules.default("active", type="updates").updates)
		self.ud.show()

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return UpdatesDialogModule(moduleManager)
