#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

import sys

class Saver(object):
	def __init__(self, module, dataType, lesson, path, *args, **kwargs):
		super(Saver, self).__init__(*args, **kwargs)
		
		self.module = module
		self.dataType = dataType
		self.lesson = lesson
		self.path = path

	def save(self):
		self.module.save(self.dataType, self.lesson, self.path)

class SaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "saver"
		self.uses = (
			self._mm.mods(type="save"),
		)
		self.requires = (
			self._mm.mods(type="lessonTracker"),
		)

	@property
	def usableExtensions(self):
		extensions = []

		dataType = self._lessonTracker.currentLesson.dataType

		#Collect exts the loader modules support, if there is a gui
		#module for the data type(s) they can provide
		for module in self._modules.sort("active", type="save"):
			if module.saves.get(dataType) is not None:
				for ext in module.saves[dataType]:
					extensions.append((ext, module.name))

		return extensions

	@property
	def saveSupport(self):
		return self._lessonTracker.currentLesson is not None and len(self.usableExtensions) != 0

	def save(self, path):
		path = path.encode(sys.getfilesystemencoding())
		savers = []

		dataType = self._lessonTracker.currentLesson.dataType
		for module in self._modules.sort("active", type="save"):
			if dataType in module.saves:
				for ext in module.saves[dataType]:
					if path.endswith(ext):
						savers.append(Saver(module, dataType, self._lessonTracker.currentLesson, path))

		if len(savers) == 0:
			raise NotImplementedError()

		saver = savers[0]
		#Save
		saver.save()

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._lessonTracker = self._modules.default("active", type="lessonTracker")

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._lessonTracker

def init(moduleManager):
	return SaverModule(moduleManager)
