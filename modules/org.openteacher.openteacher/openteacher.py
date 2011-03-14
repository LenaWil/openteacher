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

import os
import sys

class GuiLoader(object):
	def __init__(self, module, path):
		self.module = module
		self.path = path

	def __call__(self):
		self.module.loadFromFile(self.path)

	def __unicode__(self):
		return unicode(self.module)

class GuiSaver(object):
	def __init__(self, type, module, path):
		self.type
		self.module = module
		self.path = path

	def __call__(self):
		self.module.saveToFile(self.type, self.path)

	def __unicode__(self):
		return unicode(self.module)

class ImportLoader(object):
	def __init__(self, importer, guiModule, path):
		self.importer = importer
		self.guiModule = guiModule
		self.path = path

	def __call__(self):
		list = self.importer(self.path)
		self.guiModule.loadFromList(list)

	def __unicode__(self):
		return u"".join([
			unicode(self.guiModule),
			" using ",
			unicode(self.importer)
		])

class ExportSaver(object):
	def __init__(self, type, exporter, currentActionHandler, path):
		self.type = type
		self.exporter = exporter
		self.currentActionHandler = currentActionHandler
		self.path = path

	def __call__(self):
		list = self.currentActionHandler.list
		self.exporter(self.type, list, self.path)

	def __unicode__(self):
		return u"".join([
			unicode(self.currentActionHandler),
			" using ",
			unicode(self.importer)
		])

class GuiPrinter(object):
	def __init__(self, type, module, printer):
		self.type
		self.module = module
		self.printer = printer

	def __call__(self):
		self.module.print_(self.type, self.printer)

	def __unicode__(self):
		return unicode(self.module)

class ExportPrinter(object):
	def __init__(self, type, modulePrinter, printer, currentActionHandler):
		self.type = type
		self.modulePrinter = modulePrinter
		self.printer = printer
		self.currentActionHandler = currentActionHandler

	def __call__(self):
		list = self.currentActionHandler.list
		self.modulePrinter(self.type, list, self.printer)

	def __unicode__(self):
		return u"".join([
			unicode(self.currentActionHandler),
			" using ",
			unicode(self.printer)
		])

class OpenTeacherModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(OpenTeacherModule, self).__init__(*args, **kwargs)
		self.manager = manager
		self.supports = ("execute", "openteacher-core")

		self._lessons = {}

	def new(self):
		self.uiModule.showStartTab()

	def open_(self):
		path = self.uiModule.getLoadPath(
			os.path.expanduser("~"),
			self._usableLoadExtensions
		)
		if path:
			self.load(path)

	def save(self):
		#FIXME: this should first check if a path is already known
		self.saveAs()

	def saveAs(self):
		path = self.uiModule.getSavePath(
			os.path.expanduser("~"),
			self._usableSaveExtensions
		)
		if path:
			self._save(path)

	@property
	def _usableLoadExtensions(self):
		exts = set()
		#FIXME: Collect exts the GUI Modules support

		#Collect exts the loader modules support, if there is a gui
		#module for the type(s) they can provide
		for module in self.manager.mods.supporting("import"):
			for ext, fileTypes in module.importer.imports.iteritems():
				for fileType in fileTypes:
					if fileType in self._supportedFileTypes:
						exts.add(ext)
		return exts

	@property
	def _usableSaveExtensions(self):
		extensions = set()
		#FIXME: Collect exts the GUI Modules support

		#Collect exts the loader modules support, if there is a gui
		#module for the type(s) they can provide
		for module in self.manager.mods.supporting("export"):
			for exts in module.exporter.exports.values():
				for ext in exts:
					extensions.add(ext)
		return extensions

	@property
	def _supportedFileTypes(self):
		return (module.type for module in self.manager.mods.supporting("lesson"))

	def _save(self, path):
		path = path.encode(sys.getfilesystemencoding())

		savers = set()
		#FIXME: Also add GUI-module savers

		if self._currentLesson.module in self.manager.mods.supporting("list"):
			type = self._currentLesson.module.type
			for module in self.manager.mods.supporting("export"):
				for ext in module.exporter.exports[type]:
					if path.endswith(ext):
						saver = ExportSaver(
							type,
							module.exporter,
							self._currentLesson,
							path
						)
						savers.add(saver)

		if len(savers) == 0:
			raise NotImplementedError()

		#FIXME: let the user decide (and take settings into account)
		saver = savers.pop()
		#Save
		saver()
		#TODO: inform the user everything went OK.

	def load(self, path):
		loaders = set()
		#TODO: check if lesson modules can open path

		#Checks if loader modules can open it, and which type they would
		#return if they would load it only adds it as a possibility if
		#there also is a gui module for that type
		for loadModule in self.manager.mods.supporting("import"):
			fileType = loadModule.importer.getFileTypeOf(path)
			for guiModule in self.manager.mods.supporting("lesson", "loadList"):
				if guiModule.type == fileType:
					loader = ImportLoader(
						loadModule.importer,
						guiModule,
						path
					)
					loaders.add(loader)

		if len(loaders) == 0:
			raise NotImplementedError()
		#FIXME: let the user choice which loader to use (should also
		#take settings into account)
		loader = loaders.pop()

		loader()
		
		#TODO: inform the user

	def loadList(self, type, list):
		loaders = set()
		for guiModule in self.manager.mods.supporting("lesson", "loadList"):
			if guiModule.type == type:
				loaders.add(guiModule)
		if len(loaders) == 0:
			raise NotImplementedError()
		#FIXME: let the user choice which loader to use (should also
		#take settings into account)
		loader = loaders.pop()

		loader.loadFromList(list)
		
		#TODO: inform the user

	def print_(self):
		#Setup printer
		printer = self.uiModule.getConfiguredPrinter()
		if printer is None:
			return

		#print
		printers = set()
		#FIXME: Also add GUI-module printers

		if self._currentLesson.module in self.manager.mods.supporting("list"):
			type = self._currentLesson.module.type
			for module in self.manager.mods.supporting("print"):
				if type in module.printer.prints:
					printer = ExportPrinter(
						type,
						module.printer,
						printer,
						self._currentLesson
					)
					printers.add(printer)

		if len(printers) == 0:
			raise NotImplementedError()

		#FIXME: let the user decide (and take settings into account)
		printer = printers.pop()
		#Save
		printer()
		#TODO: inform the user everything went OK.

	def settings(self):
		pass

	def about(self):
		pass

	def quit_(self):
		self.uiModule.interrupt()

	def run(self):
		for module in self.manager.mods.supporting("ui", "state"):
			module.enable()

		#FIXME: Make a choice!
		uiModules = self.manager.mods.supporting("ui")
		if len(uiModules) != 1:
			raise Exception("Exactly one OpenTeacher UI module should be installed!")

		self._connectEvents(uiModules)

		for module in self.manager.mods.supporting("state").exclude("ui"):
			module.enable()

		for module in self.manager.mods.supporting("lesson"):
			module.lessonCreated.handle(self._lessonAdded)

		self.uiModule = uiModules.items.pop()
		self._updateMenuItems()
		self.uiModule.run()

		self._disconnectEvents(uiModules)

	@property
	def _currentLesson(self):
		try:
			return self._lessons[self.uiModule.currentFileTab]
		except KeyError:
			return

	def _lessonAdded(self, lesson):
		self._lessons[lesson.fileTab] = lesson
		lesson.stopped.handle(
			lambda: self._removeLesson(lesson.fileTab)
		)
		
		self._updateMenuItems()

	def _removeLesson(self, fileTab):
		del self._lessons[fileTab]

	def _connectEvents(self, uiModules):
		for module in uiModules:
			module.newEvent.handle(self.new)
			module.openEvent.handle(self.open_)
			module.saveEvent.handle(self.save)
			module.saveAsEvent.handle(self.saveAs)
			module.printEvent.handle(self.print_)
			module.settingsEvent.handle(self.settings)
			module.aboutEvent.handle(self.about)
			module.quitEvent.handle(self.quit_)

			module.tabChanged.handle(self._updateMenuItems)

	def _disconnectEvents(self, uiModules):
		for module in uiModules:
			module.newEvent.unhandle(self.new)
			module.openEvent.unhandle(self.open_)
			module.saveEvent.unhandle(self.save)
			module.saveAsEvent.unhandle(self.saveAs)
			module.printEvent.unhandle(self.print_)
			module.settingsEvent.unhandle(self.settings)
			module.aboutEvent.unhandle(self.about)
			module.quitEvent.unhandle(self.quit_)
			
			module.tabChanged.unhandle(self._updateMenuItems)

	def _updateMenuItems(self):
		for module in self.manager.mods.supporting("ui"):
			#new, hide when already on the +-tab
			hideNew = module.startTabActive
			module.enableNew(not hideNew)

			#open
			openSupport = len(self._usableLoadExtensions) != 0
			module.enableOpen(openSupport)

			#save
			saveSupport = len(self._usableSaveExtensions) != 0 and not module.startTabActive
			module.enableSave(saveSupport)
			module.enableSaveAs(saveSupport)

			#print
			printSupport = self._printingPossible()
			module.enablePrint(printSupport)

	def _printingPossible(self):
		#FIXME: Check the GUI Modules for printing support

		#Checks for printer modules, and if there is a gui module for
		#the type(s) they can provide

		try:
			type = self._currentLesson.module.type
		except AttributeError:
			return False
		for module in self.manager.mods.supporting("print"):
			if type in module.printer.prints:
				return True
		return False

def init(manager):
	return OpenTeacherModule(manager)
