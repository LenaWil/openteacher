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

import tarfile
try:
	import json
except:
	import simplejson

class OpenTeachingWordsLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingWordsLoaderModule, self).__init__(*args, **kwargs)

		self.type = "load"
		self._mm = moduleManager

	def enable(self):
		for module in self._mm.mods("active", type="modules"):
			module.registerModule("Open Teaching Words (.ot) loader", self)

		self.loads = {"otwd": ["words"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".otwd"):
			return "words"

	def load(self, path):
		file = tarfile.open(path, "r:bz2")
		listFile = file.extractfile("list.json")
		wordList = listFile.readlines()
		listFile.close()
		return json.loads(wordList[0])

def init(moduleManager):
	return OpenTeachingWordsLoaderModule(moduleManager)