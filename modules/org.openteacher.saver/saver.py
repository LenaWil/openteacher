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
	def __init__(self, module, type, lesson, path, *args, **kwargs):
		super(Saver, self).__init__(*args, **kwargs)
		
		self.module = module
		self.type = type
		self.lesson = lesson
		self.path = path

	def save(self):
		self.module.save(self.type, self.lesson.list, self.path)

	def __str__(self): #FIXME
		return str(self.module)

class SaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("saver",)
		self.requires = (1, 0)
		self.active = False

	@property
	def usableExtensions(self):
		extensions = set()

		#Collect exts the loader modules support, if there is a gui
		#module for the type(s) they can provide
		for module in self._mm.activeMods.supporting("save"):
			for exts in module.saves.values():
				for ext in exts:
					extensions.add(ext)
		return extensions

	def _modulesUpdated(self):
		#Keeps track of all created lessons
		for module in self._mm.activeMods.supporting("lesson"):
			module.lessonCreated.handle(self._lessonAdded)

	@property
	def _currentLesson(self):
		uiModule = self._mm.activeMods.supporting("ui").items.pop() #FIXME
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

	def save(self, path):#FIXME: should be public like self.load(path)?
		path = path.encode(sys.getfilesystemencoding())
		savers = set()

		if not self._currentLesson.module in self._mm.mods.supporting("list"):
			raise NotImplementedError()

		type = self._currentLesson.module.type
		for module in self._mm.activeMods.supporting("save"):
			for ext in module.saves[type]:
				if path.endswith(ext):
					savers.add(Saver(module, type, self._currentLesson, path))

		if len(savers) == 0:
			raise NotImplementedError()

		uiModule = self._mm.activeMods.supporting("ui").items.pop() #FIXME
		#Choose item
		saver = uiModule.chooseItem(savers)
		#Save
		saver.save()

	def enable(self):
		for module in self._mm.activeMods.supporting("modules"):
			module.modulesUpdated.handle(self._modulesUpdated)
		self._lessons = {}
		self.active = True

	def disable(self):
		self.active = False
		for module in self._mm.activeMods.supporting("modules"):
			module.modulesUpdated.unhandle(self._modulesUpdated)
		del self._lessons

def init(moduleManager):
	return SaverModule(moduleManager)
