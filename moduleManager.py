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

import sys
import os

class ModuleFilterer(object):
	def __init__(self, modules, *args, **kwargs):
		super(ModuleFilterer, self).__init__(*args, **kwargs)
		self._modules = modules
		self._includes = set()
		self._excludes = set()

	@property
	def items(self):
		selectedModules = self._modules.copy()
		for include in self._includes:
			group = set()
			for module in self._modules:
				excluded = False
				for exclude in self._excludes:
					if exclude in module.supports:
						excluded = True
				if not excluded and include in module.supports:
					group.add(module)
			selectedModules = selectedModules.intersection(group)
		return selectedModules

	def __iter__(self):
		return iter(self.items)

	def __len__(self):
		return len(self.items)

	def supporting(self, *features):
		self._includes = self._includes.union(features)
		return self

	def exclude(self, *features):
		self._excludes = self._excludes.union(features)
		return self

class ModuleManager(object):
	def __init__(self, modulesPath, *args, **kwargs):
		super(ModuleManager, self).__init__(*args, **kwargs)

		self.modulesPath = modulesPath
		self._events = {}

		self._loadModules()

	@staticmethod
	def resourcePath(filePath, resource):
		return os.path.join(os.path.dirname(filePath), resource)

	@staticmethod
	def createEvent():
		return Event()

	@property
	def mods(self):
		return ModuleFilterer(self._modules)

	def import_(self, executingFile, moduleName):
		path = os.path.dirname(executingFile)
		sys.path.insert(0, path)
		try:
			del sys.modules[moduleName]
		except KeyError:
			pass
		module = __import__(moduleName)
		sys.path.remove(path)
		return module

	def _loadModules(self):
		self._modules = set()

		for moduleName in os.listdir(self.modulesPath):
			location = os.path.join(self.modulesPath, moduleName)
			fileName = moduleName.split(".")[-1]
			valid = (
				not moduleName.startswith("_") and
				os.path.isdir(location)
			)
			if valid:
				sys.path.insert(0, location)
				container = __import__(fileName)
				self._modules.add(container.init(self))
				sys.path.remove(location)

class Event(object):
	def __init__(self, *args, **kwargs):
		super(Event, self).__init__(*args, **kwargs)

		self._handlers = set()

	def handle(self, handler):
		self._handlers.add(handler)

	def unhandle(self, handler):
		self._handlers.remove(handler)

	def emit(self, *args, **kwargs):
		for handler in self._handlers:
			handler(*args, **kwargs)
