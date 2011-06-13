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
import optparse
import unittest
import sys

class Saver(object):
	def __init__(self, module, type, lesson, path, *args, **kwargs):
		super(Saver, self).__init__(*args, **kwargs)
		
		self.module = module
		self.type = type
		self.lesson = lesson
		self.path = path

	def save(self):
		self.module.save(self.type, self.lesson.list, self.path)

	def __str__(self): #FIXME
		return str(self.module)

class Loader(object):
	def __init__(self, loadModule, guiModule, path, *args, **kwargs):
		super(Loader, self).__init__(*args, **kwargs)
		
		self.loadModule = loadModule
		self.guiModule = guiModule
		self.path = path

	def load(self):
		self.guiModule.loadFromList(self.loadModule.load(self.path))

	def __str__(self): #FIXME
		return str(self.loadModule)

class Printer(object):
	def __init__(self, module, type, lesson, printer, *args, **kwargs):#FIXME: 'printer' creation (as in the argument) should be handled by a separate module.
		super(Printer, self).__init__(*args, **kwargs)

		self.module = module
		self.type = type
		self.lesson = lesson
		self.printer = printer

	def print_(self):
		self.module.print_(self.type, self.lesson.list, self.printer)

	def __str__(self): #FIXME
		return str(self.module)

class OpenTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("openteacher-core",)
		self.requires = (1, 0)
		self.active = False

	def enable(self):
		self._lessons = {}
		self.active = True

	def disable(self):
		self.active = False
		del self._lessons

	def new(self):
		self.uiModule.showStartTab()

	def open_(self):
		path = self.uiModule.getLoadPath(
			os.path.expanduser("~"), #FIXME: path should be saved & restored
			self._usableLoadExtensions
		)
		if path:
			self.load(path)

	def save(self):
		#FIXME: this should first check if a path is already known
		self.saveAs()

	def saveAs(self):
		path = self.uiModule.getSavePath(
			os.path.expanduser("~"), #FIXME: path should be saved & restored
			self._usableSaveExtensions
		)
		if path:
			self._save(path)

	@property
	def _usableLoadExtensions(self):
		exts = set()

		#Collect exts the loader modules support, if there is a gui
		#module for the type(s) they can provide
		for module in self._mm.activeMods.supporting("load"):
			for ext, fileTypes in module.loads.iteritems():
				for fileType in fileTypes:
					if fileType in self._supportedFileTypes:
						exts.add(ext)
		return exts

	@property
	def _usableSaveExtensions(self):
		extensions = set()

		#Collect exts the loader modules support, if there is a gui
		#module for the type(s) they can provide
		for module in self._mm.activeMods.supporting("save"):
			for exts in module.saves.values():
				for ext in exts:
					extensions.add(ext)
		return extensions

	@property
	def _supportedFileTypes(self):
		return (module.type for module in self._mm.activeMods.supporting("lesson"))

	def _save(self, path):#FIXME: should be public like self.load(path)?
		path = path.encode(sys.getfilesystemencoding())
		savers = set()

		if not self._currentLesson.module in self._mm.mods.supporting("list"):
			raise NotImplementedError()

		type = self._currentLesson.module.type
		for module in self._mm.activeMods.supporting("save"):
			for ext in module.saves[type]:
				if path.endswith(ext):
					savers.add(Saver(module, type, self._currentLesson, path))

		if len(savers) == 0:
			raise NotImplementedError()

		#Choose item
		saver = self.uiModule.chooseItem(savers)
		#Save
		saver.save()
		#FIXME: inform the user everything went OK.

	def loadList(self, type, list):
		loaders = set()
		for module in self._mm.activeMods.supporting("loadList"):
			if module.type == type:
				loaders.add(module)
		loader = self.uiModule.chooseItem(loaders)
		loader.loadFromList(list)

	def load(self, path):
		loaders = set()

		#Checks if loader modules can open it, and which type they would
		#return if they would load it only adds it as a possibility if
		#there also is a gui module for that type
		for loadModule in self._mm.activeMods.supporting("load"):
			fileType = loadModule.getFileTypeOf(path)
			for guiModule in self._mm.activeMods.supporting("lesson", "loadList"):
				if guiModule.type == fileType:
					loaders.add(Loader(loadModule, guiModule, path))

		if len(loaders) == 0:
			raise NotImplementedError()
		#Choose item
		loader = self.uiModule.chooseItem(loaders)

		loader.load()
		
		#FIXME: inform the user

	def print_(self):
		#Setup printer
		printer = self.uiModule.getConfiguredPrinter()
		if printer is None:
			return

		#print
		printers = set()
		if self._currentLesson.module not in self._mm.mods.supporting("list"):
			raise NotImplementedError()

		type = self._currentLesson.module.type
		for module in self._mm.activeMods.supporting("print"):
			if type in module.prints:
				printers.add(Printer(module, type, self._currentLesson, printer))

		if len(printers) == 0:
			raise NotImplementedError()

		#Choose item
		printer = self.uiModule.chooseItem(printers)
		#Save
		printer.print_()
		#FIXME: inform the user everything went OK.

	def settings(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.show()

	def about(self):
		for module in self._mm.activeMods.supporting("about"):
			module.show()

	def documentation(self):
		for module in self._mm.activeMods.supporting("documentation"):
			module.show()

	def quit_(self):
		self.uiModule.interrupt()

	def run(self):
		parser = optparse.OptionParser()
		parser.add_option("-m", "--mode", dest="mode", help="set OpenTeacher in a certain MODE.", default="execute")
		options, args = parser.parse_args()
		if options.mode == "execute":
			try:
				self.execute(args[0])
			except IndexError:
				self.execute()
		elif options.mode == "test":
			self.test()

	def test(self):
		testSuite = unittest.TestSuite()
		for module in self._mm.mods.supporting("test"):
			module.enable()
			newTests = unittest.TestLoader().loadTestsFromTestCase(module.TestCase)
			testSuite.addTests(newTests)
			module.disable()
		unittest.TextTestRunner().run(testSuite)

	def execute(self, path=None):
		self.enable()

		#FIXME: use one ui module by user's choice. Make the choice with command line args
		for module in self._mm.mods.supporting("ui"):
			module.enable()

		uiModules = self._mm.activeMods.supporting("ui")
		self._connectEvents(uiModules)

		for module in self._mm.mods.supporting("settings"):
			module.enable()
			module.modulesUpdated.handle(self._modulesUpdated)

		for module in self._mm.mods.supporting("initializing"):
			module.initialize()

		#FIXME: modules should activate each other/be activated via the
		#settings. Activating/deactivating does already work, but since
		#the preferences of the user aren't saved yet, I still have this
		#enabled, because otherwise debugging takes too much time.
		#(You would have to enable every module you need every time by
		#hand)
		for module in self._mm.mods.exclude("ui").exclude("settings").exclude("openteacher-core"):
			module.enable()
		self._modulesUpdated()

		self.uiModule = uiModules.items.pop()
		self._updateMenuItems()

		if path:
			try:
				self.load(path)
			except (NotImplementedError, IOError):
				pass
			
		self.uiModule.run()

		self._disconnectEvents(uiModules)
		
		for module in self._mm.activeMods:
			module.disable()

	def _modulesUpdated(self):
		#Keeps track of all created lessons
		for module in self._mm.activeMods.supporting("lesson"):
			module.lessonCreated.handle(self._lessonAdded)

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
			module.documentationEvent.handle(self.documentation)
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
			module.documentationEvent.unhandle(self.documentation)
			module.quitEvent.unhandle(self.quit_)

			module.tabChanged.unhandle(self._updateMenuItems)

	def _updateMenuItems(self):
		for module in self._mm.activeMods.supporting("ui"):
			#new, hide when already on the +-tab
			hideNew = module.startTabActive
			module.enableNew(not hideNew)

			#open
			openSupport = len(self._usableLoadExtensions) != 0
			module.enableOpen(openSupport)

			#save
			saveSupport = self._currentLesson is not None and len(self._usableSaveExtensions) != 0
			module.enableSave(saveSupport)
			module.enableSaveAs(saveSupport)

			#print
			printSupport = self._printingPossible()
			module.enablePrint(printSupport)

			#settings
			settingsSupport = len(self._mm.activeMods.supporting("settings").items) != 0
			module.enableSettings(settingsSupport)

			#about
			aboutSupport = len(self._mm.activeMods.supporting("about").items) != 0
			module.enableAbout(aboutSupport)

	def _printingPossible(self):
		#Checks for printer modules, and if there is a gui module for
		#the type(s) they can provide

		try:
			type = self._currentLesson.module.type
		except AttributeError:
			return False
		for module in self._mm.activeMods.supporting("print"):
			if type in module.prints:
				return True
		return False

def init(moduleManager):
	return OpenTeacherModule(moduleManager)
