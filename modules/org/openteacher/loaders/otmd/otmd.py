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
import copy
try:
	import json
except:
	import simplejson

class OpenTeachingMediaLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingMediaLoaderModule, self).__init__(*args, **kwargs)
		
		self.type = "load"
		self._mm = moduleManager

	def enable(self):
		for module in self._mm.mods("active", type="modules"):
			module.registerModule("Open Teaching Media (.otmd) loader", self)
		
		self.loads = {"otmd": ["media"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".otmd"):
			return "media"

	def load(self, path):
		# Open zipfile
		with zipfile.ZipFile(path, "r") as zipFile:
			# Open json file with places
			listFile = zipFile.open("list.json")
			wordList = listFile.readlines()
			listFile.close()
			
			id = str(uuid.uuid1())
			tempFilePath = os.path.join(tempfile.gettempdir(), "openteacher\org\loaders\otmd\\" + id)
			
			list = json.loads(wordList[0])
		
			for name in zipFile.namelist():
				if name != "list.json":
					zipFile.extract(name, tempFilePath)
					# Search for same name
					for item in list["items"]:
						if item["filename"] == name:
							item["filename"] = os.path.abspath(os.path.join(tempFilePath, name))
							break
			
			return list

def init(moduleManager):
	return OpenTeachingMediaLoaderModule(moduleManager)