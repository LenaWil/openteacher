#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

from PyQt4 import QtGui
import sys
import os
import platform

class FileTab(object):
	def __init__(self, moduleManager, tabWidget, widget, *args, **kwargs):
		super(FileTab, self).__init__(*args, **kwargs)
		
		self._tabWidget = tabWidget
		self._widget = widget
		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.closeRequested = self._modules.default(
			type="event"
		).createEvent()

		i = self._tabWidget.indexOf(self._widget)
		closeButton = self._tabWidget.tabBar().tabButton(
			i,
			QtGui.QTabBar.RightSide
		)
		closeButton.clicked.connect(lambda: self.closeRequested.send())
		closeButton.setShortcut(QtGui.QKeySequence.Close)

	def close(self):
		i = self._tabWidget.indexOf(self._widget)
		self._tabWidget.removeTab(i)

class LessonFileTab(FileTab):
	def __init__(self, moduleManager, tabWidget, widget, *args, **kwargs):
		super(LessonFileTab, self).__init__(moduleManager, tabWidget, widget, *args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.tabChanged = self._modules.default(type="event").createEvent()
		self._widget.currentChanged.connect(lambda: self.tabChanged.send())
	
	def _setCurrentTab(self, value):
		self._widget.setCurrentWidget(value)

	def _getCurrentTab(self):
		return self._widget.currentWidget()

	currentTab = property(_getCurrentTab, _setCurrentTab)

class GuiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GuiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ui"
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="metadata"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="recentlyOpenedViewer"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
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
		self._ui.ICON_PATH = self._mm.resourcePath("icons/") #FIXME: something less hard to debug?
		
		# Add Aero glass option on Windows
		self._settings = self._modules.default("active", type="settings")
		if platform.system() == "Windows" and platform.version() >= 6.0:
			self._aeroSetting = self._settings.registerSetting(**{
			"internal_name": "org.openteacher.gui.aero",
			"name": "Use Aero glass (experimental)",
			"type": "boolean",
			"category": "User interface",
			"subcategory": "Effects",
			"defaultValue": False,
			})

		self._app = QtGui.QApplication(sys.argv)
		try:
			recentlyOpenedViewer = self._modules.default("active", type="recentlyOpenedViewer").createViewer()
		except IndexError:
			recentlyOpenedViewer = None
		self._widget = self._ui.OpenTeacherWidget(recentlyOpenedViewer, self._aeroSetting)

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
		
		self.active = True

	def disable(self):
		self.active = False
		
		del self._modules
		del self._ui
		del self._app
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

	def run(self):
		self._widget.show()
		self._app.exec_()

	def interrupt(self):
		self._app.closeAllWindows()

	def hide(self):
		self._widget.hide()

	def showStartTab(self):
		self._widget.tabWidget.setCurrentWidget(self._widget.tabWidget.startWidget)

	def addLessonCreateButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonCreateButton(*args, **kwargs)

		event = self._modules.default(type="event").createEvent()
		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		button.clicked.connect(lambda: event.send())
		return event

	def addLessonLoadButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonLoadButton(*args, **kwargs)
		
		event = self._modules.default(type="event").createEvent()
		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		button.clicked.connect(lambda: event.send())
		return event

	def addFileTab(self, text, enterWidget=None, teachWidget=None, resultsWidget=None):
		widget = self._ui.LessonTabWidget(enterWidget, teachWidget, resultsWidget)
		
		return self.addCustomTab(text, widget)

	def addCustomTab(self, text, widget):
		# We wrap the layout in a QVBoxLayout widget, so messages can be added on top of the tab.
		wrapperWidget = QtGui.QWidget()
		wrapperLayout = QtGui.QVBoxLayout()
		
		wrapperLayout.insertWidget(0, widget)
		wrapperWidget.setLayout(wrapperLayout)
		
		self._widget.tabWidget.addTab(wrapperWidget, text)
		
		fileTab = self._fileTabs[wrapperWidget] = FileTab(
			self._mm,
			self._widget.tabWidget,
			wrapperWidget
		)
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

	def getSavePath(self, startdir, exts): #FIXME: separate module
		stringExts = []
		
		filters = []
		for ext in exts:
			filters.append(ext + " (*." + ext + ")")

		lastWidget = self._widget.tabWidget.currentWidget()
		fileDialog = QtGui.QFileDialog()
		fileDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
		fileDialog.setWindowTitle(_("Choose file to save"))
		fileDialog.setNameFilters(filters)
		fileDialog.setDirectory(startdir)

		tab = self.addCustomTab(fileDialog.windowTitle(), fileDialog)
		tab.closeRequested.handle(tab.close)
		fileDialog.rejected.connect(tab.close)
		fileDialog.accepted.connect(tab.close)
		result = fileDialog.exec_()

		self._widget.tabWidget.setCurrentWidget(lastWidget)
		if result:
			ext = fileDialog.selectedNameFilter().split("(*")[1].split(")")[0]
			filename = str(fileDialog.selectedFiles()[0])
			if os.path.splitext(filename)[1] != ext:
				filename += ext
			return unicode(filename)
		else:
			return None
	
	def getLoadPath(self, startdir, exts): #FIXME: separate module
		stringExts = set()
		for ext in exts:
			stringExts.add("*." + ext)
		filter = u"Lessons (%s)" % u" ".join(stringExts)

		fileDialog = QtGui.QFileDialog()
		fileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
		fileDialog.setWindowTitle(_("Choose file to open"))
		fileDialog.setFilter(filter)
		fileDialog.setDirectory(startdir)

		tab = self.addCustomTab(fileDialog.windowTitle(), fileDialog)
		tab.closeRequested.handle(tab.close)
		fileDialog.rejected.connect(tab.close)
		fileDialog.accepted.connect(tab.close)
		if fileDialog.exec_():
			return unicode(fileDialog.selectedFiles()[0])
		else:
			return None
	
	def getConfiguredPrinter(self): #FIXME: separate module
		#Setup printer
		printer = QtGui.QPrinter()
		
		printDialog = QtGui.QPrintDialog(printer)
		result = printDialog.exec_()
		if not result:
			return
		return printer

	#FIXME: something more dynamic?
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
