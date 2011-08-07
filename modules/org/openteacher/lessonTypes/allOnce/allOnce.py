#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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

'''
Events:
newItem
lessonDone
''' #FIXME: python style comment, or just remove?
class AllOnceLessonType(object):
	def __init__(self, moduleManager, list, indexes, *args, **kwargs):
		super(AllOnceLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()
		self._list = list
		self._indexes = indexes
		self._test = []

		self.totalItems = len(self._indexes)
		self.askedItems = 0

	def start(self):
		self._emitNext()
	
	# result is a Result-type object saying whether the question was answered right or wrong
	def setResult(self, result):
		self._test.append(result)

		self.askedItems += 1
		self._emitNext()

	def correctLastAnswer(self, result):
		self._test[-1] = result

	def _emitNext(self):
		try:
			i = self._indexes[self.askedItems]
		except IndexError:
			#lesson end
			if len(self._test) != 0:
				try:
					self._list["tests"]
				except KeyError:
					self._list["tests"] = []
				self._list["tests"].append(self._test)
			self.lessonDone.emit()
		else:
			self.newItem.emit(self._list["items"][i])

class AllOnceModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AllOnceModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "lessonType"

	def enable(self):
		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.newItem = self._mm.createEvent()
		self.name = _("All once")
		self.active = True

	def disable(self):
		self.active = False
		del self.newItem
		del self.name

	def createLessonType(self, list, indexes):
		lessonType = AllOnceLessonType(self._mm, list, indexes)
		lessonType.newItem.handle(self.newItem.emit)
		return lessonType

def init(moduleManager):
	return AllOnceModule(moduleManager)
