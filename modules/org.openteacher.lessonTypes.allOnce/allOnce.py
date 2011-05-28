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

class AllOnceLessonType(object):
	def __init__(self, moduleManager, list, *args, **kwargs):
		super(AllOnceLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()
		self._list = list[:] #copy

		self.totalQuestions = len(self._list)
		self.askedQuestions = 0

	def start(self):
		self._emitNext()

	def setResult(self, result):
		#result: string 'right' or 'wrong'
		#FIXME: store results!

		self.askedQuestions += 1

		self._emitNext()

	def correctLastAnswer(self):
		#FIXME: do something! ;)
		pass

	def _emitNext(self):
		try:
			self.newItem.emit(self._list.pop(0))
		except IndexError:
			self.lessonDone.emit()

class AllOnceModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AllOnceModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("lessonType",)
		self.requires = (1, 0)

	def enable(self):
		self.name = _("All once") #FIXME: own '_'
		self.active = True

	def disable(self):
		self.active = False
		del self.name

	def createLessonType(self, list):
		return AllOnceLessonType(self._mm, list)

def init(moduleManager):
	return AllOnceModule(moduleManager)
