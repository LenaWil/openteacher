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

from PyQt4 import QtGui
import sys
import gettext
import ui

class FileTab(object):
	def __init__(self, manager, tabWidget, widget, *args, **kwargs):
		super(FileTab, self).__init__(*args, **kwargs)
		
		self._tabWidget = tabWidget
		self._widget = widget
		self.manager = manager
		
		self.closeRequested = self.manager.createEvent()
		
		i = self._tabWidget.indexOf(self._widget)
		closeButton = self._tabWidget.tabBar().tabButton(
			i,
			QtGui.QTabBar.RightSide
		)
		closeButton.clicked.connect(lambda: self.closeRequested.emit())

	def close(self):
		i = self._tabWidget.indexOf(self._widget)
		self._tabWidget.removeTab(i)

class GuiModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(GuiModule, self).__init__(*args, **kwargs)
		self.manager = manager
		self.supports = ("ui", "state")

		self.newEvent = self.manager.createEvent()
		self.openEvent = self.manager.createEvent()
		self.saveEvent = self.manager.createEvent()
		self.saveAsEvent = self.manager.createEvent()
		self.printEvent = self.manager.createEvent()
		self.quitEvent = self.manager.createEvent()
		self.settingsEvent = self.manager.createEvent()		
		self.aboutEvent = self.manager.createEvent()
		
		self.tabChanged = self.manager.createEvent()

	def enable(self):
		self._app = QtGui.QApplication(sys.argv)
		gettext.install("OpenTeacher")

		self._widget = ui.OpenTeacherWidget()
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
		self._widget.tabWidget.currentChanged.connect(
			lambda: self.tabChanged.emit()
		)

	def disable(self):
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

		event = self.manager.createEvent()
		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		button.clicked.connect(lambda: event.emit())
		return event

	def addLessonLoadButton(self, *args, **kwargs):
		button = self._widget.tabWidget.startWidget.addLessonLoadButton(*args, **kwargs)
		
		event = self.manager.createEvent()
		#Lambda's because otherwise Qt's argument checked is passed ->
		#error.
		button.clicked.connect(lambda: event.emit())
		return event

	def addFileTab(self, text, enterWidget, teachWidget):
		widget = ui.LessonTabWidget(enterWidget, teachWidget)
		self._widget.tabWidget.addTab(widget, text)
		
		fileTab = self._fileTabs[widget] = FileTab(
			self.manager,
			self._widget.tabWidget,
			widget
		)
		return fileTab

	def addCustomTab(self, text, widget):
		self._widget.tabWidget.addTab(widget, text)
		
		fileTab = self._fileTabs[widget] = FileTab(
			self.manager,
			self._widget.tabWidget,
			widget
		)
		return fileTab

	@property
	def currentFileTab(self):
		try:
			return self._fileTabs[self._widget.tabWidget.currentWidget()]
		except KeyError:
			#startWidget
			return

	@property
	def qtParent(self):
		return self._widget

	def getSavePath(self, startdir, exts):
		stringExts = []
		for ext in exts:
			stringExts.append("*." + ext)
		filter = u"Lessons (%s)" % u" ".join(stringExts)
		return unicode(QtGui.QFileDialog.getSaveFileName(
			self._widget,
			_("Choose location to save"),
			startdir,
			filter
		))

	def getLoadPath(self, startdir, exts):
		stringExts = set()
		for ext in exts:
			stringExts.add("*." + ext)
		filter = u"Lessons (%s)" % u" ".join(stringExts)
		return unicode(QtGui.QFileDialog.getOpenFileName(
			self._widget,
			_("Choose file to open"),
			startdir,
			filter
		))

	def getConfiguredPrinter(self):
		#Setup printer
		printer = QtGui.QPrinter()

		printDialog = QtGui.QPrintDialog(printer)
		if not printDialog.exec_():
			return
		return printer
	
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

	@property
	def startTabActive(self):
		return self._widget.tabWidget.startWidget == self._widget.tabWidget.currentWidget()

def init(manager):
	ui.ICON_PATH = manager.resourcePath(__file__, "icons/")
	return GuiModule(manager)
