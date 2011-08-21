#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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
import datetime
try:
	import json
except:
	import simplejson as json

class OpenTeachingWordsLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingWordsLoaderModule, self).__init__(*args, **kwargs)

		self.type = "load"
		self._mm = moduleManager

	def enable(self):
		for module in self._mm.mods("active", type="modules"):
			module.registerModule("Open Teaching Words (.otwd) loader", self)

		self.loads = {"otwd": ["words"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".otwd"):
			return "words"

	def _parseDt(self, data):
		return datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S.%f")

	def load(self, path):
		otwdzip = zipfile.ZipFile(path, "r")
		listFile = otwdzip.open("list.json")
		list = json.load(listFile)
		for item in list["items"]:
			try:
				item["created"] = self._parseDt(item["created"])
			except KeyError:
				pass
		for test in list["tests"]:
			for pause in test["pauses"]:
				pause["start"] = self._parseDt(pause["start"])
				pause["end"] = self._parseDt(pause["end"])
			for result in test["results"]:
				try:
					active = result["active"]
				except AttributeError:
					pass
				else:
					active["start"] = self._parseDt(active["start"])
					active["end"] = self._parseDt(active["end"])
		return list

def init(moduleManager):
	return OpenTeachingWordsLoaderModule(moduleManager)
