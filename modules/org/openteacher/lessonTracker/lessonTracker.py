#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

class LessonTrackerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LessonTrackerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "lessonTracker"

		self.requires = (
			self._mm.mods(type="ui"),
		)
		self.uses = (
			self._mm.mods(type="lesson"),
		)

	@property
	def lessons(self):
		return iter(self._lessons.values())

	@property
	def currentLesson(self):
		uiModule = self._modules.default("active", type="ui")
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

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._lessons = {}

		#Keeps track of all created lessons
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreated.handle(self._lessonAdded)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._lessons

		#Keeps track of all created lessons
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreated.unhandle(self._lessonAdded)

def init(moduleManager):
	return LessonTrackerModule(moduleManager)
