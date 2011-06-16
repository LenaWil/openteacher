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

class LoginDialog(QtGui.QDialog):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		
		emailLabel = QtGui.QLabel(_("Email: "))
		self.emailTextBox = QtGui.QLineEdit()
		
		passwordLabel = QtGui.QLabel(_("Password: "))
		self.passwordTextBox = QtGui.QLineEdit()
		self.passwordTextBox.setEchoMode(QtGui.QLineEdit.Password)

		buttonBox = QtGui.QDialogButtonBox(
			QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok,
			parent=self
		)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		verticalSpacer = QtGui.QSpacerItem(
			20,
			40,
			QtGui.QSizePolicy.Minimum,
			QtGui.QSizePolicy.Expanding
		)

		layout = QtGui.QGridLayout()
		layout.addWidget(emailLabel, 0, 0)
		layout.addWidget(self.emailTextBox, 0, 1)
		layout.addWidget(passwordLabel, 1, 0)
		layout.addWidget(self.passwordTextBox, 1, 1)
		layout.addItem(verticalSpacer, 2, 0, 1, 2)
		layout.addWidget(buttonBox, 3, 0, 1, 2)
		self.setLayout(layout)

		self.setWindowTitle(_("WRTS - login please:"))

	@property
	def email(self):
		return unicode(self.emailTextBox.text())

	@property
	def password(self):
		return unicode(self.passwordTextBox.text())

class ReadOnlyStringListModel(QtGui.QStringListModel):
	def flags(self, index):
		return QtCore.QAbstractItemModel.flags(self, index)

class ListChoiceDialog(QtGui.QDialog):
	def __init__(self, list, parent=None):
		super(self.__class__, self).__init__(parent)

		self.listView = QtGui.QListView()
		listModel = ReadOnlyStringListModel(list)
		self.listView.setModel(listModel)

		buttonBox = QtGui.QDialogButtonBox(
			QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok,
			parent=self
		)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.listView)
		layout.addWidget(buttonBox)
		self.setLayout(layout)

		self.setWindowTitle(_("WRTS - Please choose a list:"))

	@property
	def selectedRowIndex(self):
		return self.listView.selectedIndexes()[0].row()