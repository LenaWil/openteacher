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

class Saver(object):
	def __init__(self, module, dataType, lesson, path, *args, **kwargs):
		super(Saver, self).__init__(*args, **kwargs)
		
		self.module = module
		self.dataType = dataType
		self.lesson = lesson
		self.path = path

	def save(self):
		self.module.save(self.dataType, self.lesson.list, self.path)

class SaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "saver"

	@property
	def usableExtensions(self):
		extensions = set()

		#Collect exts the loader modules support, if there is a gui
		#module for the data type(s) they can provide
		for module in self._mm.mods("active", type="save"):
			for exts in module.saves.values():
				for ext in exts:
					extensions.add(ext)
		return extensions

	def _modulesUpdated(self):
		#Keeps track of all created lessons
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreated.handle(self._lessonAdded)

	@property
	def _currentLesson(self):
		uiModule = set(self._mm.mods("active", type="ui")).pop()
		try:
			return self._lessons[uiModule.currentFileTab]
		except KeyError:
			return

	def _lessonAdded(self, lesson):
		self._lessons[lesson.fileTab] = lesson
		lesson.stopped.handle(
			lambda: self._removeLesson(lesson.fileTab)
		)

	def _removeLesson(self, fileTab):
		del self._lessons[fileTab]

	@property
	def saveSupport(self):
		return self._currentLesson is not None and len(self.usableExtensions) != 0

	def save(self, path):
		path = path.encode(sys.getfilesystemencoding())
		savers = set()

		if not self._currentLesson.module:
			try:
				self._currentLesson.module.save
			except AttributeError:
				raise NotImplementedError()

		dataType = self._currentLesson.module.dataType
		for module in self._mm.mods("active", type="save"):
			for ext in module.saves[dataType]:
				if path.endswith(ext):
					savers.add(Saver(module, dataType, self._currentLesson, path))

		if len(savers) == 0:
			raise NotImplementedError()

		#Choose item
		saver = self._modules.chooseItem(savers)
		#Save
		saver.save()

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.modulesUpdated.handle(self._modulesUpdated)
		self._lessons = {}
		self.active = True

	def disable(self):
		self.active = False
		self._modules.modulesUpdated.unhandle(self._modulesUpdated)
		del self._modules
		del self._lessons

def init(moduleManager):
	return SaverModule(moduleManager)
