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

		self.supports = ("uiController",)
		self.requires = (1, 0)
		self.active = False

	def initialize(self, ui):
		#FIXME: use ui
		for module in self._mm.mods.supporting("metadata"):
			module.enable()
		#FIXME: use one ui module by user's choice. Make the choice with command line args
		for module in self._mm.mods.supporting("ui"):
			module.enable()

	def run(self, path=None):
		#FIXME: only one is activated...
		uiModules = self._mm.activeMods.supporting("ui")
		self._connectEvents(uiModules)

		self.uiModule = uiModules.items.pop()
		self._updateMenuItems()

		if path:
			try:
				self.load(path)
			except (NotImplementedError, IOError):
				pass

		for module in self._mm.activeMods.supporting("ui"):
			module.run()
		self._disconnectEvents(uiModules)

	def new(self):
		self.uiModule.showStartTab()

	def open_(self):
		#FIXME: only one
		for module in self._mm.activeMods.supporting("loader"):
			usableExtensions = module.usableExtensions
		path = self.uiModule.getLoadPath(
			os.path.expanduser("~"), #FIXME: path should be saved & restored
			usableExtensions
		)
		if path:
			#FIXME: choose one
			for module in self._mm.activeMods.supporting("loader"):
				module.load(path)
		#FIXME: inform the user of succes...

	def save(self):
		#FIXME: this should first check if a path is already known
		self.saveAs()
		#FIXME: inform the user of succes...

	def saveAs(self):
		for module in self._mm.activeMods.supporting("saver"): #FIXME: only one
			usableExtensions = module.usableExtensions
		path = self.uiModule.getSavePath(
			os.path.expanduser("~"), #FIXME: path should be saved & restored
			usableExtensions
		)
		if path:
			#FIXME: choose one
			for module in self._mm.activeMods.supporting("saver"):
				module.save(path)

	def print_(self):
		#Setup printer
		printer = self.uiModule.getConfiguredPrinter()
		if printer is None:
			return
		#FIXME: choose one
		for module in self._mm.activeMods.supporting("printer"):
			module.print_(printer)

	def _updateMenuItemsWrapper(self, *args, **kwargs):
		self._updateMenuItems()

	def _connectEvents(self, uiModules):
		for module in self._mm.activeMods.supporting("lesson"):
			module.lessonCreationFinished.handle(self._updateMenuItemsWrapper)

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
		for module in self._mm.activeMods.supporting("lesson"):
			module.lessonCreationFinished.unhandle(self._updateMenuItemsWrapper)
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
			#FIXME: choose one
			for loader in self._mm.activeMods.supporting("loader"):
				openSupport = loader.openSupport
			module.enableOpen(openSupport)

			#save
			#FIXME: choose one
			for saver in self._mm.activeMods.supporting("saver"):
				saveSupport = saver.saveSupport
			module.enableSave(saveSupport)
			module.enableSaveAs(saveSupport)

			#print
			#FIXME: choose one
			for printer in self._mm.activeMods.supporting("printer"):
				printSupport = printer.printSupport
			module.enablePrint(printSupport)

			#settings
			settingsSupport = len(self._mm.activeMods.supporting("settingsDialog").items) != 0
			module.enableSettings(settingsSupport)

			#about
			aboutSupport = len(self._mm.activeMods.supporting("about").items) != 0
			module.enableAbout(aboutSupport)

	def settings(self):
		for module in self._mm.activeMods.supporting("settingsDialog"):
			module.show()

	def about(self):
		for module in self._mm.activeMods.supporting("about"):
			module.show()

	def documentation(self):
		for module in self._mm.activeMods.supporting("documentation"):
			module.show()

	def quit_(self):
		self.uiModule.interrupt()

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return UiControllerModule(moduleManager)
