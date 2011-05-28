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

class SmartLessonType(object):
	def __init__(self, moduleManager, list, *args, **kwargs):
		super(SmartLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()

		self._list = list[:] #copy
		self.askedQuestions = 0

	@property
	def totalQuestions(self):
		return len(self._list)

	def start(self):
		self._emitNext()

	def setResult(self, result):
		self.askedQuestions += 1

		#FIXME: Process results
		if result == "wrong":
			if self._list[-1] != self._currentItem:
				self._list.append(self._currentItem)
			if self._currentItem not in (self._list[1], self._list[2]):
				self._list.insert(2, self._currentItem)
		self._emitNext()

	def correctLastAnswer(self):
		#FIXME: Reverse the results

		if self._list[-1] == self._previousItem:
			del self._list[-1]
		if self._list[1] == self._previousItem: #2 became 1 because of the new word
			del self._list[1]

	def _emitNext(self):
		try:
			self._previousItem = self._currentItem
		except AttributeError:
			self._previousItem = None
		try:
			self._currentItem = self._list.pop(0)
			self.newItem.emit(self._currentItem)
		except IndexError:
			self.lessonDone.emit()

class SmartModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SmartModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("lessonType",)
		self.requires = (1, 0)

	def enable(self):
		self.name = _("Smart") #FIXME: own '_'
		self.active = True

	def disable(self):
		self.active = False
		del self.name

	def createLessonType(self, list):
		return SmartLessonType(self._mm, list)

def init(moduleManager):
	return SmartModule(moduleManager)
