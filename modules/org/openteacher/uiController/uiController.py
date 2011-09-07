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

import os

class UiControllerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UiControllerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "uiController"
		self.requires = (
			(
				("active",),
				{"type": "ui"},
			),
			( #FIXME: make loader, saver and printer into self.uses?
				("active",),
				{"type": "loader"},
			),
			(
				("active",),
				{"type": "saver"},
			),
			(
				("active",),
				{"type": "printer"},
			),
			(
				("active",),
				{"type": "metadata"},
			),
		)
		self.uses = (
			(
				("active",),
				{"type": "settingsDialog"},
			),
			(
				("active",),
				{"type": "about"},
			),
			(
				("active",),
				{"type": "documentation"},
			),
			(
				("active",),
				{"type": "translator"},
			),
		)

#	def initialize(self):
#		try:
#			self._modules.default(type="settings").enable()
#		except IndexError:
#			pass
#		try:
#			self._modules.default(type="translator").enable()
#		except IndexError:
#			pass
#		try:
#			self._modules.default(type="metadata").enable()
#		except IndexError:
#			pass
#		try:
#			self._modules.default(type="ui").enable()
#		except IndexError:
#			pass

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

	def run(self, path=None):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
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

	def open_(self, path=None):
		loader = self._modules.default("active", type="loader")

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
		saver = self._modules.default("active", type="saver")

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

		printer = self._modules.default("active", type="printer")
		printer.print_(qtPrinter)

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
		try:
			loader = self._modules.default("active", type="loader")
		except IndexError:
			openSupport = False
		else:
			openSupport = loader.openSupport
		self._uiModule.enableOpen(openSupport)

		#save
		try:
			saver = self._modules.default("active", type="saver")
		except IndexError:
			saveSupport = False
		else:
			saveSupport = saver.saveSupport
		self._uiModule.enableSave(saveSupport)
		self._uiModule.enableSaveAs(saveSupport)

		#print
		try:
			printer = self._modules.default("active", type="printer")
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
