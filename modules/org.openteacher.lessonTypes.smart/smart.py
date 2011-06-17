#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
#	Copyright 2008-2011, Milan Boers
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

class Test(list):
	pass

class SmartLessonType(object):
	def __init__(self, moduleManager, list, indexes, *args, **kwargs):
		super(SmartLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()

		self._list = list
		self._indexes = indexes
		self._test = Test()
		self.askedItems = 0

	@property
	def totalItems(self):
		return len(self._indexes) + self.askedItems

	def start(self):
		self._emitNext()

	def setResult(self, result):
		self.askedItems += 1

		self._test.append(result)
		if result == "wrong":
			try:
				if self._indexes[-1] != self._currentIndex:
					self._indexes.append(self._currentIndex)
			except IndexError:
				pass
			try:
				if self._currentIndex not in (self._indexes[1], self._indexes[2]):
					self._indexes.insert(2, self._currentIndex)
			except IndexError:
				pass

		self._emitNext()

	def correctLastAnswer(self, result):
		self._test[-1] = result

		try:
			if self._indexes[-1] == self._previousIndex:
				del self._indexes[-1]
		except IndexError:
			pass

		try:
			if self._indexes[1] == self._previousIndex: #2 became 1 because of the new word
				del self._indexes[1]
		except IndexError:
			pass

	def _emitNext(self):
		try:
			self._previousIndex = self._currentIndex
		except AttributeError:
			pass
		try:
			self._currentIndex = self._indexes.pop(0)
		except IndexError:
			#end of lesson
			if len(self._test) != 0:
				try:
					self._list.tests
				except AttributeError:
					self._list.tests = []
				self._list.tests.append(self._test)
			self.lessonDone.emit()
		else:
			self.newItem.emit(self._list.items[self._currentIndex])

class SmartModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SmartModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("lessonType",)
		self.requires = (1, 0)
		
		self.newItem = self._mm.createEvent()

	def enable(self):
		self.name = _("Smart") #FIXME: own '_'
		self.active = True

	def disable(self):
		self.active = False
		del self.name

	def createLessonType(self, list, indexes):
		lessonType = SmartLessonType(self._mm, list, indexes)
		lessonType.newItem.handle(self.newItem.emit)
		return lessonType

def init(moduleManager):
	return SmartModule(moduleManager)
