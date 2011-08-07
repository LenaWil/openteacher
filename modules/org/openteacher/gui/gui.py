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
import gettext
import os

class FileTab(object):
	def __init__(self, moduleManager, tabWidget, widget, *args, **kwargs):
		super(FileTab, self).__init__(*args, **kwargs)
		
		self._tabWidget = tabWidget
		self._widget = widget
		self._mm = moduleManager
		
		self.closeRequested = self._mm.createEvent()
		
		i = self._tabWidget.indexOf(self._widget)
		closeButton = self._tabWidget.tabBar().tabButton(
			i,
			QtGui.QTabBar.RightSide
		)
		closeButton.clicked.connect(lambda: self.closeRequested.emit())
		closeButton.setShortcut("Ctrl+F4")

	def close(self):
		i = self._tabWidget.indexOf(self._widget)
		self._tabWidget.removeTab(i)

class LessonFileTab(FileTab):
	def __init__(self, moduleManager, tabWidget, widget, *args, **kwargs):
		super(LessonFileTab, self).__init__(moduleManager, tabWidget, widget, *args, **kwargs)

		self.tabChanged = self._mm.createEvent()
		self._widget.currentChanged.connect(lambda: self.tabChanged.emit())
	
	def _setCurrentTab(self, value):
		self._widget.setCurrentWidget(value)
	
	def _getCurrentTab(self):
		self._widget.currentWidget()
	
	currentTab = property(_getCurrentTab, _setCurrentTab)

class GuiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GuiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ui"

	def enable(self):
		self.newEvent = self._mm.createEvent()
		self.openEvent = self._mm.createEvent()
		self.saveEvent = self._mm.createEvent()
		self.saveAsEvent = self._mm.createEvent()
		self.printEvent = self._mm.createEvent()
		self.quitEvent = self._mm.createEvent()
		self.settingsEvent = self._mm.createEvent()		
		self.aboutEvent = self._mm.createEvent()
		self.documentationEvent = self._mm.createEvent()

		self.tabChanged = self._mm.createEvent()

		self._ui = self._mm.import_("ui")
		self._ui.ICON_PATH = self._mm.resourcePath("icons/") #FIXME: something less hard to debug?

		#Translations
		global _
		global ngettext

		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = self._ui._, self._ui.ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self._app = QtGui.QApplication(sys.argv)
		gettext.install("OpenTeacher")#FIXME

		self._widget = self._ui.OpenTeacherWidget()

		for module in self._mm.mods("active", "name", type="metadata"):
			name = module.name
		for module in self._mm.mods("active", "version", type="metadata"):
			version = module.version
		for module in self._mm.mods("active", "iconPath", type="metadata"):
			iconPath = module.iconPath
		self._widget.setWindowTitle(" ".join([name, version]))
		self._widget.setWindowIcon(QtGui.QIcon(iconPath))

		self._fileTabs = {}

		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		self._widget.newAction.triggered.connect(
			lambda: self.newEvent.emit()
		)
		self._widget.openAction.triggered.connect(
			lambda: self.openEvent.emit()
		)
		self._widget.saveAction.triggered.connect(
			lambda: self.saveEvent.emit()
		)
		self._widget.saveAsAction.triggered.connect(
			lambda: self.saveAsEvent.emit()
		)
		self._widget.printAction.triggered.connect(
			lambda: self.printEvent.emit()
		)
		self._widget.quitAction.triggered.connect(
			lambda: self.quitEvent.emit()
		)
		self._widget.settingsAction.triggered.connect(
			lambda: self.settingsEvent.emit()
		)
		self._widget.aboutAction.triggered.connect(
			lambda: self.aboutEvent.emit()
		)
		self._widget.docsAction.triggered.connect(
			lambda: self.documentationEvent.emit()
		)
		self._widget.tabWidget.currentChanged.connect(
			lambda: self.tabChanged.emit()
		)
		self.active = True

	def disable(self):
		self.active = False

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
		del self._widget

	def run(self):
		self._widget.show()
		self._app.exec_()

	def interrupt(self):
		self._app.closeAllWindows()

	def hide(self):
		"""Raises AttributeError"""
		self._widget.hide()

	def showStartTab(self):
		self._widget.tabWidget.setCurrentWidget(self._widget.tabWidget.startWidget)

	def addLessonCreateButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonCreateButton(*args, **kwargs)

		event = self._mm.createEvent()
		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		button.clicked.connect(lambda: event.emit())
		return event

	def addLessonLoadButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonLoadButton(*args, **kwargs)
		
		event = self._mm.createEvent()
		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		button.clicked.connect(lambda: event.emit())
		return event

	def addFileTab(self, text, enterWidget, teachWidget):
		widget = self._ui.LessonTabWidget(enterWidget, teachWidget)
		self._widget.tabWidget.addTab(widget, text)
		
		fileTab = self._fileTabs[widget] = LessonFileTab(
			self._mm,
			self._widget.tabWidget,
			widget
		)
		return fileTab

	def addCustomTab(self, text, widget):
		self._widget.tabWidget.addTab(widget, text)
		
		fileTab = self._fileTabs[widget] = FileTab(
			self._mm,
			self._widget.tabWidget,
			widget
		)
		return fileTab

	@property
	def currentFileTab(self):
		try:
			return self._fileTabs[self._widget.tabWidget.currentWidget()]
		except KeyError:
			return

	@property
	def qtParent(self):
		return self._widget

	def getSavePath(self, startdir, exts):
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

	def getLoadPath(self, startdir, exts):
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

	def getConfiguredPrinter(self):
		#Setup printer
		printer = QtGui.QPrinter()

		printDialog = QtGui.QPrintDialog(printer)
		lastWidget = self._widget.tabWidget.currentWidget()
		tab = self.addCustomTab(printDialog.windowTitle(), printDialog)
		tab.closeRequested.handle(tab.close)
		printDialog.rejected.connect(tab.close)
		printDialog.accepted.connect(tab.close)
		result = printDialog.exec_()
		self._widget.tabWidget.setCurrentWidget(lastWidget)
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

	def chooseItem(self, items):
		d = self._ui.ItemChooser(items)
		d.exec_()
		return d.item

def init(moduleManager):
	return GuiModule(moduleManager)
