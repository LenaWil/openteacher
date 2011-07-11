#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
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

from PyQt4 import QtGui, QtCore

class Result(str):
	pass

class InputTyping(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InputTyping, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingInput"

		self._mm = moduleManager
		
		self.inputLineEdit = QtGui.QLineEdit()

		self.checkButton = QtGui.QPushButton(u"Check!")
		self.checkButton.setShortcut(QtCore.Qt.Key_Return) #FIXME: translatable?
		self.correctButton = QtGui.QPushButton(u"Correct anyway")

		mainLayout = QtGui.QGridLayout()
		mainLayout.addWidget(self.inputLineEdit, 0, 0)
		mainLayout.addWidget(self.checkButton, 0, 1)
		mainLayout.addWidget(self.correctButton, 1, 1)
		self.setLayout(mainLayout)

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False
		
class InputTypingModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InputTypingModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingInput"

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

	def createWidget(self):
		return InputTyping(self._mm)

def init(moduleManager):
	return InputTypingModule(moduleManager)
