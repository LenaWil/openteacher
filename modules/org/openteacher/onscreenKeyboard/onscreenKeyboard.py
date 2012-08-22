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
import weakref

class OnscreenKeyboardWidget(QtGui.QWidget):
	letterChosen = QtCore.pyqtSignal([object])

	def __init__(self, characters, *args,  **kwargs):
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

		topWidget.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Maximum
		)

	def _letterChosen(self):
		text = unicode(self.sender().text())
		self.letterChosen.emit(text)

class KeyboardsWidget(QtGui.QTabWidget):
	def __init__(self, createEvent, data, *args, **kwargs):
		super(KeyboardsWidget, self).__init__(*args, **kwargs)

		self.letterChosen = createEvent()
		self._data = data
		self.update()

	def update(self):
		#clean the widget, needed if this method has been called before.
		self.clear()
		for module in self._data:
			#create tab and add it to the widget
			tab = OnscreenKeyboardWidget(module.data)
			self.addTab(tab, module.name)
			#connect the event that handles letter selection
			tab.letterChosen.connect(self.letterChosen.send)
			#make sure the widget updates on character changes
			if hasattr(module, "updated"):
				module.updated.handle(self.update)

class OnscreenKeyboardModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OnscreenKeyboardModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "onscreenKeyboard"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="event"),
			self._mm.mods(type="onscreenKeyboardData"),
			self._mm.mods(type="translator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._widgets = set()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChangeDone.handle(self._update)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._widgets

	def createWidget(self):
		kw = KeyboardsWidget(
			self._modules.default(type="event").createEvent,
			self._modules.sort("active", type="onscreenKeyboardData")
		)
		self._widgets.add(weakref.ref(kw))
		return kw

	def _update(self):
		for ref in self._widgets:
			widget = ref()
			if widget is not None:
				widget.update()

def init(moduleManager):
	return OnscreenKeyboardModule(moduleManager)
