#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

import sys

class Action(object):
	def __init__(self, createEvent, *args, **kwargs):
		super(Action, self).__init__(*args, **kwargs)

		self.triggered = createEvent()
		self.toggled = createEvent()

	def remove(self):
		pass

class Menu(object):
	def __init__(self, createEvent, *args, **kwargs):
		super(Menu, self).__init__(*args, **kwargs)

		self._createEvent = createEvent

	def addAction(self, priority):
		return Action(self._createEvent)

class GuiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GuiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ui"

	def enable(self):
		global QtCore, QtGui
		try:
			from PyQt4 import QtCore, QtGui
		except ImportError:
			return

		self._app = QtGui.QApplication.instance()
		if not self._app:
			self._app = QtGui.QApplication(sys.argv)

		self._modules = next(iter(self._mm.mods(type="modules")))
		self._createEvent = self._modules.default(type="event").createEvent

		newMenu = lambda: Menu(self._createEvent)
		newAction = lambda: Action(self._createEvent)

		self.fileMenu = newMenu()
		self.newAction = newAction()
		self.openAction = newAction()
		self.saveAction = newAction()
		self.saveAsAction = newAction()
		self.printAction = newAction()
		self.quitAction = newAction()

		self.settingsAction = newAction()
		self.fullscreenAction = newAction()

		self.aboutAction = newAction()
		self.documentationAction = newAction()

		self.tabChanged = self._createEvent()
		self.currentFileTab = None
		self.startTabActive = True

		self.active = True

	def run(self, closeRequested):
		pass

	def disable(self):
		self.active = False

		del self._modules
		del self._createEvent

		del self._app

		del self.fileMenu
		del self.newAction
		del self.openAction
		del self.saveAction
		del self.saveAsAction
		del self.printAction
		del self.quitAction

		del self.settingsAction
		del self.fullscreenAction

		del self.aboutAction
		del self.documentationAction

		del self.tabChanged
		del self.currentFileTab
		del self.startTabActive

def init(moduleManager):
	return GuiModule(moduleManager)
