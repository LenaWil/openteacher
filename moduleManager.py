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

__version__ = (1,0)

import sys
import os
import imp

class ModuleFilterer(object):
	#Cache used to speed up module lookups, is class member so all
	#instances can use it.
	_cache = {}

	def __init__(self, modules, *args, **kwargs):
		super(ModuleFilterer, self).__init__(*args, **kwargs)
		self._modules = modules
		self._includes = set()
		self._excludes = set()

	@property
	def items(self):
		#Freeze sets so they are hashable
		self._includes = frozenset(self._includes)
		self._excludes = frozenset(self._excludes)

		#do a cache look up, maybe it speeds everything a little up - i
		#couldn't measure the difference, but it was nice to code ;)
		try:
			return self._cache[(self._includes, self._excludes)].copy()
		except KeyError:
			pass
		#Look up the modules manually
		selectedModules = self._modules.copy()
		for include in self._includes:
			group = set()
			for module in selectedModules:
				if include in module.supports:
					group.add(module)
			selectedModules = selectedModules.intersection(group)
		selectedModules = set(filter(self._moduleNotExcluded, selectedModules))
		#store the result in the cache for later use
		self._cache[(self._includes, self._excludes)] = selectedModules.copy()
		return selectedModules

	def _moduleNotExcluded(self, module):
		for interface in module.supports:
			if interface in self._excludes:
				return False
		return True

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

class ActiveModuleFilterer(ModuleFilterer):
	@property
	def items(self):
		modules = super(ActiveModuleFilterer, self).items
		return set(filter(self._isActive, modules))

	def _isActive(self, module):
		try:
			return module.active
		except AttributeError:
			return False

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

	@property
	def activeMods(self):
		return ActiveModuleFilterer(self._modules)

	def import_(self, path, moduleName):
		if os.path.isfile(path):
			#so path can be __file__
			path = os.path.dirname(path)
		sys.path.insert(0, path)
		fp, pathname, description = imp.find_module(moduleName)
		try:
			return imp.load_module(moduleName, fp, pathname, description)
		finally:
			sys.path.remove(path)
			if fp:
				fp.close()

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
				container = self.import_(location, fileName)
				module = container.init(self)
				if module.requires[0] == __version__[0] and module.requires[1] <= __version__[1]:
					self._modules.add(module)

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
