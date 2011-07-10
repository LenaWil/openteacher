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

class UiControllerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UiControllerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "uiController"

	def initialize(self, ui):
		#FIXME: use one ui module by user's choice. Make the choice with command line args?
		for module in self._mm.mods(type="metadata"):
			module.enable()
		#FIXME: use one ui module by user's choice. Make the choice with command line args?
		for module in self._mm.mods(type="ui"):
			module.enable()

	def run(self, path=None):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._uiModule = set(self._mm.mods("active", type="ui")).pop()

		self._connectEvents()
		self._updateMenuItems()

		if path:
			try:
				self.open_(path)
			except (NotImplementedError, IOError):
				pass

		for module in self._mm.mods("active", type="ui"):
			module.run()
		self._disconnectEvents()

	def new(self):
		self._uiModule.showStartTab()

	def open_(self, path=None):
		loaders = set(self._mm.mods("active", type="loader"))
		loader = self._modules.chooseItem(loaders)

		usableExtensions = loader.usableExtensions
		if not path:
			path = self._uiModule.getLoadPath(
				os.path.expanduser("~"), #FIXME: path should be saved & restored
				usableExtensions
			)
		if path:
			loader.load(path)
		#FIXME: inform the user of succes...

	def save(self):
		#FIXME: this should first check if a path is already known
		self.saveAs()
		#FIXME: inform the user of succes...

	def saveAs(self):
		savers = set(self._mm.mods("active", type="saver"))
		saver = self._modules.chooseItem(savers)

		usableExtensions = saver.usableExtensions
		path = self._uiModule.getSavePath(
			os.path.expanduser("~"), #FIXME: path should be saved & restored
			usableExtensions
		)
		if path:
			saver.save(path)
		#FIXME: inform the user of succes...

	def print_(self):
		#Setup printer
		qtPrinter = self._uiModule.getConfiguredPrinter()
		if qtPrinter is None:
			return
		
		printers = set(self._mm.mods("active", type="printer"))
		printer = self._modules.chooseItem(printers)
		printer.print_(qtPrinter)

	def _updateMenuItemsWrapper(self, *args, **kwargs):
		self._updateMenuItems()

	def _connectEvents(self):
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreationFinished.handle(self._updateMenuItemsWrapper)

		self._uiModule.newEvent.handle(self.new)
		self._uiModule.openEvent.handle(self.open_)
		self._uiModule.saveEvent.handle(self.save)
		self._uiModule.saveAsEvent.handle(self.saveAs)
		self._uiModule.printEvent.handle(self.print_)
		self._uiModule.settingsEvent.handle(self.settings)
		self._uiModule.aboutEvent.handle(self.about)
		self._uiModule.documentationEvent.handle(self.documentation)
		self._uiModule.quitEvent.handle(self.quit_)

		self._uiModule.tabChanged.handle(self._updateMenuItems)

	def _disconnectEvents(self):
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreationFinished.unhandle(self._updateMenuItemsWrapper)

		self._uiModule.newEvent.unhandle(self.new)
		self._uiModule.openEvent.unhandle(self.open_)
		self._uiModule.saveEvent.unhandle(self.save)
		self._uiModule.saveAsEvent.unhandle(self.saveAs)
		self._uiModule.printEvent.unhandle(self.print_)
		self._uiModule.settingsEvent.unhandle(self.settings)
		self._uiModule.aboutEvent.unhandle(self.about)
		self._uiModule.documentationEvent.unhandle(self.documentation)
		self._uiModule.quitEvent.unhandle(self.quit_)

		self._uiModule.tabChanged.unhandle(self._updateMenuItems)

	def _updateMenuItems(self):
		#new, hide when already on the +-tab
		hideNew = self._uiModule.startTabActive
		self._uiModule.enableNew(not hideNew)

		#open
		loaders = set(self._mm.mods("active", type="loader"))
		try:
			loader = self._modules.chooseItem(loaders)
		except IndexError:
			openSupport = False
		else:
			openSupport = loader.openSupport
		self._uiModule.enableOpen(openSupport)

		#save
		savers = set(self._mm.mods("active", type="saver"))
		try:
			saver = self._modules.chooseItem(savers)
		except IndexError:
			saveSupport = False
		else:
			saveSupport = saver.saveSupport
		self._uiModule.enableSave(saveSupport)
		self._uiModule.enableSaveAs(saveSupport)

		#print
		printers = set(self._mm.mods("active", type="printer"))
		try:
			printer = self._modules.chooseItem(printers)
		except IndexError:
			printSupport = False
		else:
			printSupport = printer.printSupport
		self._uiModule.enablePrint(printSupport)

		#settings
		settingsSupport = len(set(self._mm.mods("active", type="settingsDialog"))) != 0
		self._uiModule.enableSettings(settingsSupport)

		#about
		aboutSupport = len(set(self._mm.mods("active", type="about"))) != 0
		self._uiModule.enableAbout(aboutSupport)

		#documentation
		docSupport = len(set(self._mm.mods("active", type="documentation"))) != 0
		self._uiModule.enableDocumentation(docSupport)

	def settings(self):
		module = self._modules.chooseItem(
			set(self._mm.mods("active", type="settingsDialog"))
		)
		module.show()

	def about(self):
		module = self._modules.chooseItem(
			set(self._mm.mods("active", type="about"))
		)
		module.show()

	def documentation(self):
		module = self._modules.chooseItem(
			set(self._mm.mods("active", type="documentation"))
		)
		module.show()

	def quit_(self):
		for ui in self._mm.mods("active", type="ui"):
			ui.interrupt()

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return UiControllerModule(moduleManager)
