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

import zipfile
try:
	import json
except ImportError:
	import simplejson as json

class ModulePackage(object):
	def __init__(self, installPath, file, *args, **kwargs):
		"""Raises all kinds of errors returned by the zipfile module and
		   IOError

		"""
		super(ModuleInstaller, self).__init__(*args, **kwargs)

		self._installPath = installPath
		self._zip = zipfile.ZipFile(file)
		if self._zip.testzip() is not None:
			del self._zip
			raise IOError("Corrupted zip file")

	@property
	def metadata(self):
		return simplejson.loads(self._zip.comment)

	def install(self):
		self._zip.extractall(self._installPath)

class ModuleInstallerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ModuleInstallerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "moduleInstaller"

	def createModulePackage(self, *args, **kwargs):
		return ModulePackage(self._mm.modulePath, *args, **kwargs)

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return ModuleInstallerModule(moduleManager)
