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
		
		self.emailTextBox = QtGui.QLineEdit()
		
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

		self.flayout = QtGui.QFormLayout()
		self.flayout.addRow("0", self.emailTextBox)
		self.flayout.addRow("1", self.passwordTextBox)
		if store:
			self.flayout.addRow(self.saveCheckbox)

		layout = QtGui.QVBoxLayout()
		layout.addLayout(self.flayout)
		layout.addStretch()
		layout.addWidget(buttonBox)

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
		except AttributeError:
			return False

	def retranslate(self):
		self.setWindowTitle(_("WRTS - login please:"))

		self.flayout.itemAt(0, QtGui.QFormLayout.LabelRole).widget().setText(
			_("Email: ")
		)
		self.flayout.itemAt(1, QtGui.QFormLayout.LabelRole).widget().setText(
			_("Password: ")
		)
		try:
			self.saveCheckbox.setText(_("Store mail address and password"))
		except AttributeError:
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
