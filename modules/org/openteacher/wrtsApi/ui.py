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
	def __init__(self, store, *args, **kwargs):
		super(LoginDialog, self).__init__(*args, **kwargs)
		
		self.emailLabel = QtGui.QLabel()
		self.emailTextBox = QtGui.QLineEdit()
		
		self.passwordLabel = QtGui.QLabel()
		self.passwordTextBox = QtGui.QLineEdit()
		self.passwordTextBox.setEchoMode(QtGui.QLineEdit.Password)
		
		if store:
			self.saveCheckbox = QtGui.QCheckBox("", self)

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
		layout.addWidget(self.emailLabel, 0, 0)
		layout.addWidget(self.emailTextBox, 0, 1)
		layout.addWidget(self.passwordLabel, 1, 0)
		layout.addWidget(self.passwordTextBox, 1, 1)
		layout.addWidget(self.saveCheckbox, 2, 0)
		layout.addItem(verticalSpacer, 3, 0, 1, 2)
		layout.addWidget(buttonBox, 4, 0, 1, 2)
		self.setLayout(layout)

	@property
	def email(self):
		return unicode(self.emailTextBox.text())

	@property
	def password(self):
		return unicode(self.passwordTextBox.text())
		
	@property
	def saveCheck(self):
		try:
			return self.saveCheckbox.isChecked()
		except NameError:
			return False

	def retranslate(self):
		self.setWindowTitle(_("WRTS - login please:"))
		self.emailLabel.setText(_("Email: "))
		self.passwordLabel.setText(_("Password: "))
		try:
			self.saveCheckbox.setText(_("Store mail address and password"))
		except NameError:
			pass

class ReadOnlyStringListModel(QtGui.QStringListModel):
	def flags(self, index):
		return QtCore.QAbstractItemModel.flags(self, index)

class ListChoiceDialog(QtGui.QDialog):
	def __init__(self, list, parent=None):
		super(ListChoiceDialog, self).__init__(parent)

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

	@property
	def selectedRowIndex(self):
		return self.listView.selectedIndexes()[0].row()

	def retranslate(self):
		self.setWindowTitle(_("WRTS - Please choose a list:"))
