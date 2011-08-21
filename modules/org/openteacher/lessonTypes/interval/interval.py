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

import random

"""
Events:
newItem
lessonDone
"""
class IntervalLessonType(object):
	def __init__(self, moduleManager, list, indexes, *args, **kwargs):
		super(IntervalLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = self._mm.createEvent()
		self.lessonDone = self._mm.createEvent()
		self._list = list
		self._indexes = indexes
		self._test = []

		self.totalItems = len(self._indexes)
		self.askedItems = 0
		
		# Items in the group
		self._group = []

	def start(self):
		# Add items to the group
		for i in xrange(4):
			try:
				self._list["items"][i]
			except:
				pass
			else:
				self._group.append(i)
		self._emitNext()
	
	# result is a Result-type object saying whether the question was answered right or wrong
	def setResult(self, result):
		self._test.append(result)

		self.askedItems += 1
		self._emitNext()

	def correctLastAnswer(self, result):
		self._test[-1] = result

	def _emitNext(self):
		# Go through all the items in the group to see which can be removed
		for i in self._group:
			right = 0
			wrong = 0
			# Fill in right and wrong variables
			for item in self._test:
				if item["itemId"] == i:
					if item["result"] == "right":
						right += 1
					elif item["result"] == "wrong":
						wrong += 1
			if right + wrong > 2 and \
			   right / (right + wrong) > 0.8:
				print "You know " + str(i)
				# Add new one
				try:
					self._list["items"][self._group[-1] + 1]
				except:
					pass
				else:
					print "adding " + str(self._group[-1] + 1)
					self._group.append(self._group[-1] + 1)
				# Remove this item from the group
				self._group.remove(i)
		
		if len(self._group) == 0:
			# index not in list, so end of lesson
			if len(self._test) != 0:
				try:
					self._list["tests"]
				except KeyError:
					self._list["tests"] = []
				self._list["tests"].append(self._test)
			self.lessonDone.emit()
		else:
			if len(self._group) > 1:
				# Get random number
				r = random.randrange(0, len(self._group) - 1)
			else:
				r = 0
			self.newItem.emit(self._list["items"][self._group[r]])
			

class IntervalModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(IntervalModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "lessonType"

	def enable(self):
		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.newItem = self._mm.createEvent()
		self.name = _("Interval")
		self.active = True

	def disable(self):
		self.active = False
		del self.newItem
		del self.name

	def createLessonType(self, list, indexes):
		lessonType = IntervalLessonType(self._mm, list, indexes)
		lessonType.newItem.handle(self.newItem.emit)
		return lessonType

def init(moduleManager):
	return IntervalModule(moduleManager)
