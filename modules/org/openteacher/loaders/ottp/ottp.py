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
import tempfile
import os
import uuid
import datetime
try:
	import json
except:
	import simplejson

class OpenTeachingTopoLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingTopoLoaderModule, self).__init__(*args, **kwargs)

		self.type = "load"
		self._mm = moduleManager

	def enable(self):
		for module in self._mm.mods("active", type="modules"):
			module.registerModule("Open Teaching Topo (.ottp) loader", self)

		self.loads = {"ottp": ["topo"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".ottp"):
			return "topo"
	
	def _stringsToDatetimes(self, list):
		for test in list["tests"]:
			for result in test["results"]:
				result["active"]["start"] = datetime.datetime.strptime(result["active"]["start"], "%Y-%m-%dT%H:%M:%S.%f")
				result["active"]["end"] = datetime.datetime.strptime(result["active"]["end"], "%Y-%m-%dT%H:%M:%S.%f")
		
		return list
	
	def load(self, path):
		# Open zipfile
		with zipfile.ZipFile(path, "r") as zipFile:
			listFile = zipFile.open("list.json")
			wordList = listFile.readlines()
			listFile.close()
			
			tempFilePath = os.path.join(tempfile.gettempdir(), "openteacher\org\loaders\ottp\\" + str(uuid.uuid1()))
			
			# Open map
			for name in zipFile.namelist():
				if os.path.splitext(name)[0] == "map":
					zipFile.extract(name, tempFilePath)
					mapName = name
					break
			
			tempFilePath = os.path.join(tempFilePath, name)
			
			feedback = {
				"list": self._stringsToDatetimes(json.loads(wordList[0])),
				"resources": {
					"mapPath": tempFilePath
				}
			}
			
			return feedback

def init(moduleManager):
	return OpenTeachingTopoLoaderModule(moduleManager)