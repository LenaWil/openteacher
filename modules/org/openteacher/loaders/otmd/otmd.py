#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import zipfile

class OpenTeachingMediaLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingMediaLoaderModule, self).__init__(*args, **kwargs)
		
		self.type = "load"
		self.priorities = {
			"student@home": 216,
			"student@school": 216,
			"teacher": 216,
			"wordsonly": -1,
			"selfstudy": 216,
			"testsuite": 216,
			"codedocumentation": 216,
			"all": 216,
		}
		
		self._mm = moduleManager
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="otxxLoader"),
		)

	def enable(self):
		self.name = "Open Teaching Media"
		self.loads = {"otmd": ["media"]}

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._otxxLoader = self._modules.default("active", type="otxxLoader")

		self.active = True

	def disable(self):
		self.active = False

		del self.name
		del self.loads

		del self._modules
		del self._otxxLoader

	def getFileTypeOf(self, path):
		if path.endswith(".otmd"):
			return "media"

	def load(self, path):
		resourceFilenames = {}
		with zipfile.ZipFile(path, "r") as zipFile:
			names = zipFile.namelist()
		names.remove("list.json")
		for name in names:
			resourceFilenames[name] = name
		return self._otxxLoader.load(path, resourceFilenames)

def init(moduleManager):
	return OpenTeachingMediaLoaderModule(moduleManager)
