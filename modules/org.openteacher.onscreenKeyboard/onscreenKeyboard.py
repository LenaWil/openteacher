#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
#	Copyright 2008-2011, Milan Boers
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

class OnscreenKeyboardWidget(QtGui.QWidget):
	def __init__(self, manager, characters, *args,  **kwargs):
		super(OnscreenKeyboardWidget, self).__init__(*args, **kwargs)

		topWidget = QtGui.QWidget()

		layout = QtGui.QGridLayout()
		layout.setSpacing(1)
		layout.setContentsMargins(0, 0, 0, 0)

		i = 0
		for line in characters:
			j = 0
			for item in line:
				b = QtGui.QPushButton(item)
				b.clicked.connect(self._letterChosen)
				b.setMinimumSize(1, 1)
				b.setFlat(True)
				b.setAutoFillBackground(True)
				palette = b.palette()
				if i % 2 == 0:
					brush = palette.brush(QtGui.QPalette.Base)
				else:
					brush = palette.brush(QtGui.QPalette.AlternateBase)
				palette.setBrush(QtGui.QPalette.Button, brush)
				b.setPalette(palette)
				if not item:
					b.setEnabled(False)
				layout.addWidget(b, i, j)
				j += 1
			i+= 1
		topWidget.setLayout(layout)
		palette = topWidget.palette()
		brush = palette.brush(QtGui.QPalette.WindowText)
		palette.setBrush(QtGui.QPalette.Window, QtCore.Qt.darkGray)
		topWidget.setPalette(palette)
		topWidget.setAutoFillBackground(True)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(topWidget)
		mainLayout.addStretch()
		mainLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(mainLayout)

		self._mm = manager
		self.letterChosen = self._mm.createEvent()

		topWidget.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Maximum
		)

	def _letterChosen(self):
		text = unicode(self.sender().text())
		self.letterChosen.emit(text)

class OnscreenKeyboardModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OnscreenKeyboardModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("onscreenKeyboard",)
		self.requires = (1, 0)

	def enable(self): pass
	def disable(self): pass

	def getWidget(self):
		widget = QtGui.QTabWidget()
		widget.letterChosen = self._mm.createEvent()
		for module in self._mm.activeMods.supporting("onscreenKeyboardData"):
			tab = OnscreenKeyboardWidget(self._mm, module.data)
			widget.addTab(tab, module.name)
			tab.letterChosen.handle(widget.letterChosen.emit)
		return widget

	def showLetter(self, letter):
		print letter

def init(moduleManager):
	return OnscreenKeyboardModule(moduleManager)
