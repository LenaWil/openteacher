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

	def _save(self, path):
		path = path.encode(sys.getfilesystemencoding())
		savers = set()

		if not self._currentLesson.module in self._mm.mods.supporting("list"):
			raise NotImplementedError()

		type = self._currentLesson.module.type
		for module in self._mm.activeMods.supporting("save"):
			for ext in module.exporter.exports[type]:
				if path.endswith(ext):
					savers.add(lambda: module.save( #FIXME, something cleaner...
						type,
						self._currentLesson.list,
						path)
					)

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
		for loadModule in self._mm.activeMods.supporting("load"):
			fileType = loadModule.getFileTypeOf(path)
			for guiModule in self._mm.activeMods.supporting("lesson", "loadList"):
				if guiModule.type == fileType:
					loaders.add(lambda: guiModule.loadFromList(loadModule.load(path)))

		if len(loaders) == 0:
			raise NotImplementedError()
		#FIXME: let the user choice which loader to use (should also
		#take settings into account)
		loader = loaders.pop()

		loader()
		
		#TODO: inform the user

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
				printers.add(lambda: module.print_(type, self._currentLesson.list, printer))

		if len(printers) == 0:
			raise NotImplementedError()

		#FIXME: let the user decide (and take settings into account)
		printer = printers.pop()
		#Save
		printer()
		#TODO: inform the user everything went OK.

	def settings(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.show()

	def about(self):
		pass

	def quit_(self):
		self.uiModule.interrupt()

	def run(self):
		#FIXME: use one ui module by user's choice.
		for module in self._mm.mods.supporting("ui"):
			module.enable()

		uiModules = self._mm.activeMods.supporting("ui")
		self._connectEvents(uiModules)

		for module in self._mm.mods.supporting("settings"):
			module.enable()

		for module in self._mm.mods.supporting("initializing"):
			module.initialize()

		#FIXME: modules should activate each other/be activated via the settings!
		for module in self._mm.mods.exclude("ui").exclude("settings"):
			module.enable()

		for module in self._mm.mods.supporting("lesson"):
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
		for module in self._mm.activeMods.supporting("ui"):
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
