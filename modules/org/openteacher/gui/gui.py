#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
#	Copyright 2011, Milan Boers
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
import sys
import platform

class Action(object):
	def __init__(self, createEvent, qtMenu, qtAction, *args, **kwargs):
		super(Action, self).__init__(*args, **kwargs)

		self._qtMenu = qtMenu
		self._qtAction = qtAction

		self.triggered = createEvent()
		#lambda to prevent useless Qt arguments to pass
		self._qtAction.triggered.connect(lambda: self.triggered.send())

	def remove(self):
		self._qtMenu.removeAction(self._qtAction)

	text = property(
		lambda self: unicode(self._qtAction.text()),
		lambda self, value: self._qtAction.setText(value)
	)

	enabled = property(
		lambda self: self._qtMenu.isEnabled(),
		lambda self, value: self._qtAction.setEnabled(value)
	)

#FIXME: make sure it's possible for the new menus to specify the place
#to insert new actions/menus
class Menu(object):
	def __init__(self, event, qtMenu, *args, **kwargs):
		super(Menu, self).__init__(*args, **kwargs)

		self._createEvent = event
		self._qtMenu = qtMenu

	def addAction(self):
		qtAction = QtGui.QAction(self._qtMenu)
		self._qtMenu.addAction(qtAction)
		return Action(self._createEvent, self._qtMenu, qtAction)

	def addMenu(self):
		qtSubMenu = QtGui.QMenu()
		self._qtMenu.addMenu(qtSubMenu)
		return Menu(self._createEvent, qtSubMenu)

	def remove(self):
		self._qtMenu.hide()

	text = property(
		lambda self: unicode(self._qtMenu.title()),
		lambda self, value: self._qtMenu.setTitle(value)
	)

	enabled = property(
		lambda self: self._qtMenu.isEnabled(),
		lambda self, value: self._qtMenu.setEnabled(value)
	)

class StatusViewer(object):
	def __init__(self, statusBar, *args, **kwargs):
		super(StatusViewer, self).__init__(*args, **kwargs)

		self._statusBar = statusBar

	def show(self, message):
		self._statusBar.showMessage(message)

class FileTab(object):
	def __init__(self, moduleManager, tabWidget, wrapperWidget, widget, lastWidget, *args, **kwargs):
		super(FileTab, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods(type="modules")).pop()

		self._tabWidget = tabWidget
		self._wrapperWidget = wrapperWidget
		self._widget = widget
		self._lastWidget = lastWidget

		self.closeRequested = self._modules.default(
			type="event"
		).createEvent()

		closeButton = self._tabWidget.tabBar().tabButton(
			self._index,
			QtGui.QTabBar.RightSide
		)
		closeButton.clicked.connect(lambda: self.closeRequested.send())
		closeButton.setShortcut(QtGui.QKeySequence.Close)

	@property
	def _index(self):
		return self._tabWidget.indexOf(self._wrapperWidget)

	def close(self):
		i = self._tabWidget.indexOf(self._wrapperWidget)
		self._tabWidget.removeTab(i)
		if self._lastWidget:
			self._tabWidget.setCurrentWidget(self._lastWidget)

	title = property(
		lambda self: self._tabWidget.tabText(self._index),
		lambda self, val: self._tabWidget.setTabText(self._index, val)
	)

class LessonFileTab(FileTab):
	def __init__(self, *args, **kwargs):
		super(LessonFileTab, self).__init__(*args, **kwargs)

		#properties are defined in parent class
		self.tabChanged = self._modules.default(type="event").createEvent()
		self._widget.currentChanged.connect(lambda: self.tabChanged.send())

	currentTab = property(
		lambda self: self._widget.currentWidget(),
		lambda self, value: self._widget.setCurrentWidget(value)
	)

class GuiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GuiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ui"
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="startWidget"),
			self._mm.mods(type="metadata"),
		)
		self.uses = (
			self._mm.mods(type="buttonRegister"),
			self._mm.mods(type="translator"),
			self._mm.mods(type="settings"),
		)
		self.priorities = {
			"student@home": 0,
			"student@school": 0,
			"teacher": 0,
			"wordsonly": 0,
			"selfstudy": 0,
			"all": 0,
			"default": -1,
		}

		self.filesWithTranslations = ("gui.py", "ui.py")

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		createEvent = self._modules.default(type="event").createEvent

		self.tabChanged = createEvent()
		self.applicationActivityChanged = createEvent()

		self._ui = self._mm.import_("ui")
		self._ui.ICON_PATH = self._mm.resourcePath("icons/")

		# Add Aero glass option on Windows
		try:
			self._settings = self._modules.default(type="settings")
		except IndexError, e:
			self._aeroSetting = None
		else:
			if platform.system() == "Windows" and platform.version() >= 6.0:
				self._aeroSetting = self._settings.registerSetting(**{
					"internal_name": "org.openteacher.gui.aero",
					"name": "Use Aero glass (experimental)",
					"type": "boolean",
					"category": "User interface",
					"subcategory": "Effects",
					"defaultValue": False,
					"advanced": True,
				})
			else:
				self._aeroSetting = None
		
		self._app = QtGui.QApplication(sys.argv)
		
		self._widget = self._ui.OpenTeacherWidget(
			self._modules.default("active", type="startWidget").createStartWidget(),
			self._aeroSetting and self._aeroSetting["value"],
		)

		try:
			br = self._modules.default("active", type="buttonRegister")
		except IndexError:
			pass
		else:
			#add the open action as a load button too.
			self._loadButton = br.registerButton("load")
			self._loadButton.clicked.handle(self._widget.openAction.triggered.emit)

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		metadata = self._modules.default("active", type="metadata").metadata
		self._widget.setWindowTitle(metadata["name"])
		self._widget.setWindowIcon(QtGui.QIcon(metadata["iconPath"]))

		self._fileTabs = {}

		#Make menus accessable
		#file
		self.fileMenu = Menu(createEvent, self._widget.fileMenu)
		self.newAction = Action(createEvent, self._widget.fileMenu, self._widget.newAction)
		self.openAction = Action(createEvent, self._widget.fileMenu, self._widget.openAction)
		self.saveAction = Action(createEvent, self._widget.fileMenu, self._widget.saveAction)
		self.saveAsAction = Action(createEvent, self._widget.fileMenu, self._widget.saveAsAction)
		self.printAction = Action(createEvent, self._widget.fileMenu, self._widget.printAction)
		self.quitAction = Action(createEvent, self._widget.fileMenu, self._widget.quitAction)

		#edit
		self.editMenu = Menu(createEvent, self._widget.editMenu)
		self.settingsAction = Action(createEvent, self._widget.editMenu, self._widget.settingsAction)

		#help
		self.helpMenu = Menu(createEvent, self._widget.helpMenu)
		self.documentationAction = Action(createEvent, self._widget.helpMenu, self._widget.docsAction)
		self.aboutAction = Action(createEvent, self._widget.helpMenu, self._widget.aboutAction)

		self._widget.tabWidget.currentChanged.connect(
			lambda: self.tabChanged.send()
		)
		self._widget.activityChanged.connect(
			lambda activity: self.applicationActivityChanged.send(
				"active" if activity else "inactive"
			)
		)

		#make the statusViewer available
		self.statusViewer = StatusViewer(self._widget.statusBar())

		#set application name (handy for e.g. Phonon)
		self._app.setApplicationName(metadata["name"])
		self._app.setApplicationVersion(metadata["version"])

		self.active = True

	def disable(self):
		self.active = False

		try:
			br = self._modules.default("active", type="buttonRegister")
		except IndexError:
			pass
		else:
			#we don't unhandle the event, since PyQt4 does some weird
			#memory stuff making it impossible to find the right item,
			#and it's unneeded anyway.
			br.unregisterButton(self._loadButton)
			del self._loadButton

		del self._modules
		del self._ui
		del self._fileTabs
		del self.tabChanged
		del self.applicationActivityChanged
		del self._widget

		del self.fileMenu
		del self.newAction
		del self.openAction
		del self.saveAction
		del self.saveAsAction
		del self.printAction
		del self.quitAction

		del self.editMenu
		del self.settingsAction

		del self.helpMenu
		del self.documentationAction
		del self.aboutAction

		del self.statusViewer

	def _retranslate(self):
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self._ui._, self._ui.ngettext = _, ngettext
		self._widget.retranslate()

		self._loadButton.changeText.send(_("Open from file"))

	def run(self):
		"""Starts the event loop of the Qt application. 
		   Can only be called once.

		"""
		self._widget.show()
		self._app.exec_()

		#Prevents segmentation fault
		del self._app
		QtCore.qApp = None

	def interrupt(self):
		self._app.closeAllWindows()

	def hide(self):
		self._widget.hide()

	@property
	def startTab(self):
		return self._widget.tabWidget.startWidget

	def showStartTab(self):
		self._widget.tabWidget.setCurrentWidget(self._widget.tabWidget.startWidget)

	def addFileTab(self, enterWidget=None, teachWidget=None, resultsWidget=None, previousTabOnClose=False):
		widget = self._ui.LessonTabWidget(enterWidget, teachWidget, resultsWidget)

		return self.addCustomTab(widget, previousTabOnClose)

	def addCustomTab(self, widget, previousTabOnClose=False):
		# We wrap the layout in a QVBoxLayout widget, so messages can be added on top of the tab.
		wrapperWidget = QtGui.QWidget()
		wrapperLayout = QtGui.QVBoxLayout()

		wrapperLayout.insertWidget(0, widget)
		wrapperWidget.setLayout(wrapperLayout)

		if previousTabOnClose:
			lastWidget = self._widget.tabWidget.currentWidget()
		else:
			lastWidget = None

		self._widget.tabWidget.addTab(wrapperWidget, "")

		args = (self._mm, self._widget.tabWidget, wrapperWidget, widget, lastWidget)

		if widget.__class__ == self._ui.LessonTabWidget:
			fileTab = self._fileTabs[wrapperWidget] = LessonFileTab(*args)
		else:
			fileTab = self._fileTabs[wrapperWidget] = FileTab(*args)
		return fileTab

	@property
	def currentFileTab(self):
		try:
			return self._fileTabs[self._widget.tabWidget.currentWidget()]
		except KeyError:
			return

	def addStyleSheetRules(self, rules):
		self._app.setStyleSheet(self._app.styleSheet() + "\n\n" + rules)

	def setStyle(self, style):
		self._app.setStyle(style)

	@property
	def qtParent(self):
		"""Only use this as widget parent, or for application
		global Qt settings, and don't be surprised if another
		module sets that setting differently.

		"""
		return self._widget

	@property
	def startTabActive(self):
		return self._widget.tabWidget.startWidget == self._widget.tabWidget.currentWidget()

def init(moduleManager):
	return GuiModule(moduleManager)
