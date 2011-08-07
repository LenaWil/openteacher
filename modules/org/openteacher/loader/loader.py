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

import sys

class Loader(object):
	def __init__(self, loadModule, guiModule, path, *args, **kwargs):
		super(Loader, self).__init__(*args, **kwargs)

		self.loadModule = loadModule
		self.guiModule = guiModule
		self.path = path

	def load(self):
		self.guiModule.loadFromList(self.loadModule.load(self.path), self.path)

class LoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LoaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "loader"

	@property
	def _supportedFileTypes(self):
		types = set()
		for lesson in self._mm.mods("active", type="lesson"):
			try:
				types.add(lesson.dataType)
			except AttributeError:
				pass
		return types

	@property
	def usableExtensions(self):
		exts = set()

		#Collect exts the loader modules support, if there is a gui
		#module for the type(s) they can provide
		for module in self._mm.mods("active", type="load"):
			for ext, fileTypes in module.loads.iteritems():
				for fileType in fileTypes:
					if fileType in self._supportedFileTypes:
						exts.add(ext)
		return exts

	@property
	def openSupport(self):
		return len(self.usableExtensions) != 0

	def load(self, path):
		loaders = set()

		#Checks if loader modules can open it, and which type they would
		#return if they would load it only adds it as a possibility if
		#there also is a gui module for that type
		
		for loadModule in self._mm.mods("active", type="load"):
			fileType = loadModule.getFileTypeOf(path)
			for guiModule in self._mm.mods("active", type="lesson"):
				try:
					guiModule.loadFromList
				except AttributeError:
					continue
				if guiModule.dataType == fileType:
					loaders.add(Loader(loadModule, guiModule, path))

		if len(loaders) == 0:
			raise NotImplementedError()
		#Choose item
		loader = self._modules.chooseItem(loaders)

		loader.load()

	def loadFromList(self, dataType, list):
		loaders = set()
		for lesson in self._mm.mods(type="lesson"):
			if lesson.dataType == dataType:
				try:
					lesson.loadFromList
				except AttributeError:
					continue
				loaders.add(lesson)
		loader = self._modules.chooseItem(loaders)
		loader.loadFromList(list)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.active = True

	def disable(self):
		self.active = False
		del self._modules

def init(moduleManager):
	return LoaderModule(moduleManager)

