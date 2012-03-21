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

#FIXME: sort buttons on the start tab and make the remove buttons of it
#work.

from PyQt4 import QtCore, QtGui
import sys
import platform

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

class Button(object):
	def __init__(self, qtButton, createEvent, removeMethod, *args, **kwargs):
		super(Button, self).__init__(*args, **kwargs)

		self.clicked = createEvent()

		self._qtButton = qtButton
		#Lambda because otherwise Qt's argument checked is passed ->
		#error.
		self._qtButton.clicked.connect(lambda: self.clicked.send())
		
		self._removeMethod = removeMethod

	text = property(
		lambda self: self._qtButton.text(),
		lambda self, value: self._qtButton.setText(value)
	)

	icon = property(
		lambda self: self._qtButton.icon(),
		lambda self, icon: self._qtButton.setIcon(icon)
	)

	def remove(self):
		self._removeMethod(self._qtButton)

class GuiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GuiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ui"
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="metadata"),
			self._mm.mods(type="menuWrapper"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="recentlyOpenedViewer"),
			self._mm.mods(type="settings"),
		)
		self.filesWithTranslations = ["gui.py"]

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		createEvent = self._modules.default(type="event").createEvent

		self.newEvent = createEvent()
		self.openEvent = createEvent()
		self.saveEvent = createEvent()
		self.saveAsEvent = createEvent()
		self.printEvent = createEvent()
		self.quitEvent = createEvent()
		self.settingsEvent = createEvent()		
		self.aboutEvent = createEvent()
		self.documentationEvent = createEvent()

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
		try:
			recentlyOpenedViewer = self._modules.default("active", type="recentlyOpenedViewer").createViewer()
		except IndexError:
			recentlyOpenedViewer = None
		
		if self._aeroSetting != None and self._aeroSetting["value"] == True:
			self._widget = self._ui.OpenTeacherWidget(recentlyOpenedViewer, True)
		else:
			self._widget = self._ui.OpenTeacherWidget(recentlyOpenedViewer, False)

		#add the open action as a load button too.
		self._loadButton = self.addLessonLoadButton()
		self._loadButton.clicked.handle(self.openEvent.send)

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		metadata = self._modules.default("active", type="metadata").metadata
		self._widget.setWindowTitle(
			" ".join([metadata["name"], metadata["version"]])
		)
		self._widget.setWindowIcon(QtGui.QIcon(metadata["iconPath"]))

		self._fileTabs = {}

		#Make menus accessable
		wrapMenu = self._modules.default("active", type="menuWrapper").wrapMenu
		self.fileMenu = wrapMenu(self._widget.fileMenu)
		self.editMenu = wrapMenu(self._widget.editMenu)
		self.helpMenu = wrapMenu(self._widget.helpMenu)

		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		self._widget.newAction.triggered.connect(
			lambda: self.newEvent.send()
		)
		self._widget.openAction.triggered.connect(
			lambda: self.openEvent.send()
		)
		self._widget.saveAction.triggered.connect(
			lambda: self.saveEvent.send()
		)
		self._widget.saveAsAction.triggered.connect(
			lambda: self.saveAsEvent.send()
		)
		self._widget.printAction.triggered.connect(
			lambda: self.printEvent.send()
		)
		self._widget.quitAction.triggered.connect(
			lambda: self.quitEvent.send()
		)
		self._widget.settingsAction.triggered.connect(
			lambda: self.settingsEvent.send()
		)
		self._widget.aboutAction.triggered.connect(
			lambda: self.aboutEvent.send()
		)
		self._widget.docsAction.triggered.connect(
			lambda: self.documentationEvent.send()
		)
		self._widget.tabWidget.currentChanged.connect(
			lambda: self.tabChanged.send()
		)
		self._widget.activityChanged.connect(
			lambda activity: self.applicationActivityChanged.send(
				"active" if activity else "inactive"
			)
		)

		#set application name (handy for e.g. Phonon)
		self._app.setApplicationName(metadata["name"])
		self._app.setApplicationVersion(metadata["version"])

		self.active = True

	def disable(self):
		self.active = False

		self._loadButton.remove()
		
		del self._modules
		del self._ui
		del self._fileTabs
		del self.newEvent
		del self.openEvent
		del self.saveEvent
		del self.saveAsEvent
		del self.printEvent
		del self.quitEvent
		del self.settingsEvent
		del self.aboutEvent
		del self.documentationEvent
		del self.tabChanged
		del self.applicationActivityChanged
		del self._widget
		del self.fileMenu
		del self.editMenu
		del self.helpMenu
		del self._loadButton

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

		self._loadButton.text = _("Open from file")

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

	def showStartTab(self):
		self._widget.tabWidget.setCurrentWidget(self._widget.tabWidget.startWidget)

	def addLessonCreateButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonCreateButton(*args, **kwargs)
		createEvent = self._modules.default(type="event").createEvent

		return Button(button, createEvent, self._widget.tabWidget.startWidget.removeLessonCreateButton)

	def addLessonLoadButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonLoadButton(*args, **kwargs)
		createEvent = self._modules.default(type="event").createEvent

		return Button(button, createEvent, self._widget.tabWidget.startWidget.removeLessonLoadButton)

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

	def enableNew(self, boolean):
		self._widget.newAction.setEnabled(boolean)

	def enableOpen(self, boolean):
		self._widget.openAction.setEnabled(boolean)

	def enableSave(self, boolean):
		self._widget.saveAction.setEnabled(boolean)

	def enableSaveAs(self, boolean):
		self._widget.saveAsAction.setEnabled(boolean)

	def enablePrint(self, boolean):
		self._widget.printAction.setEnabled(boolean)

	def enableSettings(self, boolean):
		self._widget.settingsAction.setEnabled(boolean)

	def enableAbout(self, boolean):
		self._widget.aboutAction.setEnabled(boolean)

	def enableDocumentation(self, boolean):
		self._widget.docsAction.setEnabled(boolean)

	@property
	def startTabActive(self):
		return self._widget.tabWidget.startWidget == self._widget.tabWidget.currentWidget()

def init(moduleManager):
	return GuiModule(moduleManager)
