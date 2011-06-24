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
import imp
import inspect

class ModuleFilterer(object):
	def __init__(self, modules, *args, **kwargs):
		super(ModuleFilterer, self).__init__(*args, **kwargs)
		self._modules = modules

		self._where = {}
		self._whereTrue = set()

	def __call__(self, *args, **kwargs):
		self._whereTrue = self._whereTrue.union(args)
		self._where.update(kwargs)
		return self

	def __iter__(self):
		return iter(filter(self._filterModule, self._modules))

	def _filterModule(self, module):
		for attribute, value in self._where.iteritems():
			if not self._equals(module, attribute, value):
				return False
		for attribute in self._whereTrue:
			if not self._isTrue(module, attribute):
				return False
		return True

	def _equals(self, module, attribute, value):
		try:
			return getattr(module, attribute) == value
		except AttributeError:
			return False

	def _isTrue(self, module, attribute):
		try:
			return bool(getattr(module, attribute))
		except AttributeError:
			return False

class ModuleManager(object):
	def __init__(self, modulesPath, *args, **kwargs):
		super(ModuleManager, self).__init__(*args, **kwargs)

		self.modulesPath = modulesPath
		self._events = {}
		self._references = []

		self._loadModules()

	@staticmethod
	def _callerOfCallerPath():
		callerFile = inspect.getouterframes(inspect.currentframe())[2][1]
		return os.path.dirname(callerFile)

	@classmethod
	def resourcePath(cls, resource):
		return os.path.join(cls._callerOfCallerPath(), resource)

	@staticmethod
	def createEvent():
		return Event()

	@property
	def mods(self):
		return ModuleFilterer(self._modules)

	def importFrom(self, path, moduleName):
		fp, pathname, description = imp.find_module(moduleName, [path])
		try:
			#import the module
			module = imp.load_module(moduleName, fp, pathname, description)
			#remove the module from the python cache, to avoid
			#namespace clashes
			del sys.modules[moduleName]
			#but keep our own reference, otherwise the module namespace
			#will probably be garbage collected.
			self._references.append(module)
			return module
		finally:
			if fp:
				fp.close()

	def import_(self, moduleName):
		return self.importFrom(self._callerOfCallerPath(), moduleName)

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
				container = self.importFrom(location, fileName)
				module = container.init(self)
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
