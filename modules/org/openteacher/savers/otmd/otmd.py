#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
#	Copyright 2011-2012, Marten de Vries
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
import copy
import os

class Lesson(object):
	pass

class OpenTeachingMediaSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingMediaSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"
		self.priorities = {
			"student@home": 112,
			"student@school": 112,
			"teacher": 112,
			"wordsonly": -1,
			"selfstudy": 112,
			"testsuite": 112,
			"codedocumentation": 112,
			"all": 112,
		}
		
		self.requires = (
			self._mm.mods(type="settings"),
			self._mm.mods(type="otxxSaver"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)

	def enable(self):		
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._otxxSaver = self._modules.default("active", type="otxxSaver")

		self.name = "Open Teaching Media"
		self.saves = {"media": ["otmd"]}

		self._settings = self._modules.default("active", type="settings")
		self._compressionSetting = self._settings.registerSetting(**{
			"internal_name": "org.openteacher.savers.otmd.compression",
			"name": "Enable compression",
			"type": "boolean",
			"category": "Media Lesson",
			"subcategory": ".otmd saving",
			"defaultValue": True,
			"advanced": True,
		})
		
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._otxxSaver
		del self._settings
		del self._compressionSetting
		del self.name
		del self.saves

	def save(self, type, lesson, path):
		compression = zipfile.ZIP_STORED
		if self._compressionSetting["value"]:
			compression = zipfile.ZIP_DEFLATED

		#FIXME: let media use the resources attribute in a way similar
		#to topo.
		lesson_clone = Lesson()
		lesson_clone.list = copy.deepcopy(lesson.list)
		lesson_clone.resources = {}
		for item in lesson_clone.list["items"]:
			if not item["remote"]:
				lesson_clone.resources[os.path.basename(item["filename"])] = item["filename"]
				item["filename"] = os.path.basename(item["filename"])

		resourceFilenames = {}
		for resourceName in lesson_clone.resources:
			resourceFilenames[resourceName] = resourceName

		self._otxxSaver.save(lesson_clone, path, resourceFilenames, compression)

def init(moduleManager):
	return OpenTeachingMediaSaverModule(moduleManager)
