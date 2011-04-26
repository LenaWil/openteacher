#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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

class NormalLessonType(object):
	def __init__(self, moduleManager, list, *args, **kwargs):
		super(NormalLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()
		self._list = list[:] #copy

		self.totalQuestions = len(self._list)
		self.askedQuestions = 0

	def start(self):
		try:
			self.newItem.emit(self._list.pop())
		except IndexError:
			self.lessonDone.emit()

	def setResult(self, result):
		#result: string 'right' or 'wrong'
		#FIXME: store results!

		self.askedQuestions += 1

		try:
			self.newItem.emit(self._list.pop())
		except IndexError:
			self.lessonDone.emit()

	def correctLastAnswer(self):
		#FIXME: do something! ;)
		pass

class NormalLessonTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(NormalLessonTypeModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("lessonType",)
		self.requires = (1, 0)

	def enable(self):
		self.name = _("Normal lesson") #FIXME: own '_'
		self.active = True

	def disable(self):
		self.active = False
		del self.name

	def createLessonType(self, list):
		return NormalLessonType(self._mm, list)

def init(moduleManager):
	return NormalLessonTypeModule(moduleManager)
