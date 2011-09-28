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
import inspect

class ModuleFilterer(object):
	"""This class is used to filter a list of objects ('modules'). By
	   calling an instance you can add filter requirements. There are
	   two types of filter requirements:
	   - an attribute equals a value
	   - an attribute evaluates to true
	   
	   You can run through the results by a for loop, or get them in
	   a python set/list/tuple/whatever by calling the appropriate
	   conversion function (e.g. set(ModuleFilterer(modules)) )"""

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
	"""This class manages modules. It loads them from a directory when
	   they meet the requirements for being a module, and it offers a
	   few functions to the initialized modules, like getting resource
	   paths and handling imports in the module directory."""

	def __init__(self, modulesPath, *args, **kwargs):
		super(ModuleManager, self).__init__(*args, **kwargs)

		self.modulesPath = modulesPath
		self._events = {}
		self._references = set()

		self._loadModules()

	@staticmethod
	def _callerOfCallerPath():
		callerFile = inspect.getouterframes(inspect.currentframe())[2][1]
		return os.path.dirname(callerFile)

	@classmethod
	def resourcePath(cls, resource):
		return os.path.join(cls._callerOfCallerPath(), resource)

	@property
	def mods(self):
		return ModuleFilterer(self._modules)

	def importFrom(self, path, moduleName):
		#make sure the module is importable
		sys.path.insert(0, path)
		#import the module
		module = __import__(moduleName)
		#remove the module from the python cache, to avoid
		#namespace clashes
		del sys.modules[moduleName]
		#but keep our own reference, otherwise the module namespace
		#will probably be garbage collected.
		self._references.add(module)
		#remove the module path again so it doesn't influence other imports
		sys.path.remove(path)
		return module

	def import_(self, moduleName):
		return self.importFrom(self._callerOfCallerPath(), moduleName)

	def _loadModules(self):
		self._modules = set()

		for root, dirs, files in os.walk(self.modulesPath):
			name = os.path.split(root)[1]
			valid = (
				name + ".py" in files and
				not "_" in root
			)
			if valid:
				container = self.importFrom(root, name)
				module = container.init(self)
				self._modules.add(module)
