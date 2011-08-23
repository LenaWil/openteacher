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

class SmartLessonType(object):
	def __init__(self, moduleManager, list, indexes, *args, **kwargs):
		super(SmartLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()

		self._list = list
		self._indexes = indexes
		self._test = {
			"results": [],
			"finished": False,
			"pauses": [],
		}
		
		self.askedItems = 0

	@property
	def totalItems(self):
		return len(self._indexes) + self.askedItems

	def start(self):
		self._emitNext()

	def addPause(self, pause):
		self._test["pauses"].append(pause)

	def setResult(self, result):
		# Add the test to the list (if it's not already there)
		self._appendTest()
		
		self.askedItems += 1

		self._test["results"].append(result)
		if result["result"] == "wrong":
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
		self._test["results"][-1] = result

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
	
	def _appendTest(self):
		try:
			self._list["tests"][-1]
		except IndexError:
			self._list["tests"].append(self._test)
		else:
			if not self._list["tests"][-1] == self._test:
				self._list["tests"].append(self._test)

	def _emitNext(self):		
		try:
			self._previousIndex = self._currentIndex
		except AttributeError:
			pass
		try:
			self._currentIndex = self._indexes.pop(0)
		except IndexError:
			#end of lesson
			if len(self._test["results"]) != 0:
				self._test["finished"] = True
				try:
					self._list["tests"]
				except KeyError:
					self._list["tests"] = []
			self.lessonDone.emit()
		else:
			self.newItem.emit(self._list["items"][self._currentIndex])

class SmartModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SmartModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "lessonType"

	def enable(self):
		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.newItem = self._mm.createEvent()
		self.name = _("Smart")
		self.active = True

	def disable(self):
		self.active = False
		del self.newItem
		del self.name

	def createLessonType(self, list, indexes):
		lessonType = SmartLessonType(self._mm, list, indexes)
		lessonType.newItem.handle(self.newItem.emit)
		return lessonType

def init(moduleManager):
	return SmartModule(moduleManager)
