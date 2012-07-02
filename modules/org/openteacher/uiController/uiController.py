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

import os

class UiControllerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UiControllerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "uiController"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="metadata"),
			self._mm.mods(type="execute"),
		)
		self.uses = (
			self._mm.mods(type="settingsDialog"),
			self._mm.mods(type="about"),
			self._mm.mods(type="documentation"),
			self._mm.mods(type="translator"),
			self._mm.mods(type="loader"),
			self._mm.mods(type="saver"),
			self._mm.mods(type="printer"),
			self._mm.mods(type="printDialog"),
			self._mm.mods(type="fileDialogs"),
			self._mm.mods(type="lessonTracker"),
			self._mm.mods(type="dataStore"),
			self._mm.mods(type="dialogShower"),
		)
		#priorities are handled by gui.py...

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		try:
			self._store = self._modules.default(type="dataStore").store
		except IndexError:
			self._store = {}
		try:
			self._fileDialogs = self._modules.default("active", type="fileDialogs")
		except IndexError:
			self._fileDialogs = None
		try:
			self._printDialog = self._modules.default("active", type="printDialog")		
		except IndexError:
			self._printDialog = None
		try:
			self._lessonTracker = self._modules.default("active", type="lessonTracker")
		except IndexError:
			self._lessonTracker = None
		self._saver = self._modules.default("active", type="saver")
		self._execute = self._modules.default(type="execute")

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self._execute.startRunning.handle(self.run)

		self.active = True

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

	def disable(self):
		self.active = False

		self._execute.startRunning.unhandle(self.run)

		del self._modules
		if hasattr(self, "_fileDialogs"):
			del self._fileDialogs
		if hasattr(self, "_printDialog"):
			del self._printDialog
		if hasattr(self, "_lessonTracker"):
			del self._lessonTracker
		if hasattr(self, "_saver"):
			del self._saver
		if hasattr(self, "_loader"):
			del self._loader
		if hasattr(self, "_printer"):
			del self._printer

		del self._execute

	def run(self, path=None):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")

		self._connectEvents()
		self._updateMenuItems()

		if path:
			try:
				self.open_(path)
			except (NotImplementedError, IOError):
				pass

		self._uiModule.run()
		self._disconnectEvents()

	def new(self):
		self._uiModule.showStartTab()

	@property
	def _lastPath(self):
		try:
			return self._store["org.openteacher.uiController.lastPath"]
		except KeyError:
			return os.path.expanduser("~")

	@_lastPath.setter
	def _lastPath(self, path):
		self._store["org.openteacher.uiController.lastPath"] = path

	def _showError(self, msg):
		tab = self._uiModule.currentFileTab or self._uiModule.startTab
		try:
			self._modules.default("active", type="dialogShower").showError.send(tab, msg)
		except IndexError:
			#fallback
			print msg

	def open_(self, path=None):
		loader = self._modules.default("active", type="loader")

		usableExtensions = loader.usableExtensions
		if not path:
			path = self._fileDialogs.getLoadPath(
				self._lastPath,
				usableExtensions
			)
		if path:
			try:
				loader.load(path)
			except NotImplementedError, e:
				print e
				self._showError(_("Couldn't open the file, because the file type is unknown"))
			except IOError, e:
				print e
				self._showError(_("Couldn't open the file, is it still there and do we have the right to open it?"))
			except Exception, e:
				print e
				self._showError(_("Couldn't open the file, it seems to be corrupted."))
			self._lastPath = path
		self._uiModule.statusViewer.show(_("File opened succesfully."))

	def _doSave(self, path):
		try:
			self._saver.save(path)
		except IOError, e:
			print e
			self._showError(_("Couldn't save the file, is there enough free disk space and do we have the right to write to the specified location?"))
		else:
			self._uiModule.statusViewer.show(_("File saved succesfully."))

	def save(self, path=None):
		if not path:
			try:
				path = self._lessonTracker.currentLesson.path
			except AttributeError:
				self.saveAs()
				return
		if path:
			self._doSave(path)
		else:
			self.saveAs()

	def saveAs(self):
		path = self._fileDialogs.getSavePath(
			self._lastPath,
			#sort on names (not extensions)
			sorted(self._saver.usableExtensions, key=lambda ext: ext[1]),
			#default (== top most) extension
			self._saver.usableExtensions[0]
		)
		if path:
			self._lastPath = path
			self._doSave(path)

	def print_(self):
		#Setup printer
		qtPrinter = self._printDialog.getConfiguredPrinter()
		if qtPrinter is None:
			return

		printer = self._modules.default("active", type="printer")
		printer.print_(qtPrinter)

	def _connectEvents(self):
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreationFinished.handle(self._updateMenuItemsWrapper)

		self._uiModule.newAction.triggered.handle(self.new)
		self._uiModule.openAction.triggered.handle(self.open_)
		self._uiModule.saveAction.triggered.handle(self.save)
		self._uiModule.saveAsAction.triggered.handle(self.saveAs)
		self._uiModule.printAction.triggered.handle(self.print_)
		self._uiModule.settingsAction.triggered.handle(self.settings)
		self._uiModule.aboutAction.triggered.handle(self.about)
		self._uiModule.documentationAction.triggered.handle(self.documentation)
		self._uiModule.quitAction.triggered.handle(self.quit_)

		self._uiModule.tabChanged.handle(self._updateMenuItems)

	def _disconnectEvents(self):
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreationFinished.unhandle(self._updateMenuItemsWrapper)

		self._uiModule.newAction.triggered.unhandle(self.new)
		self._uiModule.openAction.triggered.unhandle(self.open_)
		self._uiModule.saveAction.triggered.unhandle(self.save)
		self._uiModule.saveAsAction.triggered.unhandle(self.saveAs)
		self._uiModule.printAction.triggered.unhandle(self.print_)
		self._uiModule.settingsAction.triggered.unhandle(self.settings)
		self._uiModule.aboutAction.triggered.unhandle(self.about)
		self._uiModule.documentationAction.triggered.unhandle(self.documentation)
		self._uiModule.quitAction.triggered.unhandle(self.quit_)

		self._uiModule.tabChanged.unhandle(self._updateMenuItems)

	def _updateMenuItems(self):
		#subscribe self to the lesson (if it's there nothing happens
		#due to the internal implementation of event. Which is also
		#guaranteed by a test suite test, btw. So it's by design.)
		if hasattr(self._lessonTracker.currentLesson, "changedEvent"):
			self._lessonTracker.currentLesson.changedEvent.handle(self._updateMenuItems)

		#new, hide when already on the +-tab
		hideNew = self._uiModule.startTabActive
		self._uiModule.newAction.enabled = not hideNew

		#open
		try:
			loader = self._modules.default("active", type="loader")
		except IndexError:
			openSupport = False
		else:
			openSupport = loader.openSupport
		openSupport = openSupport and self._fileDialogs is not None
		self._uiModule.openAction.enabled = openSupport

		#save
		try:
			saver = self._modules.default("active", type="saver")
		except IndexError:
			saveSupport = False
		else:
			saveSupport = saver.saveSupport
		saveSupport = saveSupport and self._fileDialogs is not None
		self._uiModule.saveAsAction.enabled = saveSupport

		try:
			enableSave = saveSupport and self._lessonTracker.currentLesson.changed
		except AttributeError:
			enableSave = saveSupport #assume changed
		self._uiModule.saveAction.enabled = enableSave

		#print
		try:
			printer = self._modules.default("active", type="printer")
		except IndexError:
			printSupport = False
		else:
			printSupport = printer.printSupport
		printSupport = printSupport and self._printDialog is not None
		self._uiModule.printAction.enabled = printSupport

		#settings
		settingsSupport = len(set(self._mm.mods("active", type="settingsDialog"))) != 0
		self._uiModule.settingsAction.enabled = settingsSupport

		#about
		aboutSupport = len(set(self._mm.mods("active", type="about"))) != 0
		self._uiModule.aboutAction.enabled = aboutSupport

		#documentation
		docSupport = len(set(self._mm.mods("active", type="documentation"))) != 0
		self._uiModule.documentationAction.enabled = docSupport

	def _updateMenuItemsWrapper(self, *args, **kwargs):
		self._updateMenuItems()

	def settings(self):
		self._modules.default("active", type="settingsDialog").show()

	def about(self):
		self._modules.default("active", type="about").show()

	def documentation(self):
		self._modules.default("active", type="documentation").show()

	def quit_(self):
		self._uiModule.interrupt()

def init(moduleManager):
	return UiControllerModule(moduleManager)
