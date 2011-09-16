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
	def __init__(self, moduleManager, createEvent, list, indexes, *args, **kwargs):#FIXME: get rid of the moduleManager here...
		super(IntervalLessonType, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.newItem = createEvent()
		self.lessonDone = createEvent()
		self._list = list
		self._indexes = indexes
		self._test = {
			"results": [],
			"finished": False,
			"pauses": [],
		}
		
		self.totalItems = len(self._indexes)
		
		# Ids of items in the group
		self._group = []
	
	@property
	def askedItems(self):
		ids = []
		for item in self._test["results"]:
			if ids.count(item["itemId"]) == 0:
				ids.append(item["itemId"])
		
		return len(ids)

	def start(self):
		size = 4
		for module in self._mm.mods("active", type="settings"):
			size = module.value("org.openteacher.lessonTypes.interval.groupSize")
		if size < 2:
			size = 2
		
		# Add items to the group
		for i in xrange(size):
			try:
				self._list["items"][i]
			except:
				pass
			else:
				self._group.append(i)
		self._sendNext()
	
	# result is a Result-type object saying whether the question was answered right or wrong
	def setResult(self, result):
		# Add the test to the list (if it's not already there)
		self._appendTest()
		
		self._test["results"].append(result)

		self._sendNext()
	
	def addPause(self, pause):
		self._test["pauses"].append(pause)

	def correctLastAnswer(self, result):
		self._test["results"][-1] = result
	
	def _appendTest(self):
		try:
			self._list["tests"][-1]
		except IndexError:
			self._list["tests"].append(self._test)
		else:
			if not self._list["tests"][-1] == self._test:
				self._list["tests"].append(self._test)
	
	def _sendNext(self):		
		minQuestions = 2
		for module in self._mm.mods("active", type="settings"):
			minQuestions = module.value("org.openteacher.lessonTypes.interval.minQuestions")
		if minQuestions < 1:
			minquestions = 2
		
		whenKnown = 80
		for module in self._mm.mods("active", type="settings"):
			whenKnown = module.value("org.openteacher.lessonTypes.interval.whenKnown")
		if whenKnown < 0 or whenKnown > 99:
			whenKnown = 80
		
		# Go through all the items in the group to see which can be removed
		for i in self._group:
			right = 0
			wrong = 0
			# Fill in right and wrong variables
			for item in self._test["results"]:
				if item["itemId"] == i:
					if item["result"] == "right":
						right += 1
					elif item["result"] == "wrong":
						wrong += 1
			
			if right + wrong > minQuestions and \
			   right / float(right + wrong) > whenKnown / 100.0:
				# Add new one
				try:
					# Try if it exists
					self._list["items"][self._group[-1] + 1]
				except:
					pass
				else:
					# Add it
					self._group.append(self._group[-1] + 1)
				# Remove this item from the group
				self._group.remove(i)
		
		if len(self._group) == 0:
			# index not in list, so end of lesson
			if len(self._test["results"]) != 0:
				try:
					self._list["tests"]
				except KeyError:
					self._list["tests"] = []
			self._test["finished"] = True
			self.lessonDone.send()
		else:
			# Copy group, because we are going to modify it
			randomGroup = self._group[:]
			# We will take out the last id, so a question isn't asked twice
			if len(self._test["results"]) > 0:
				try:
					randomGroup.remove(self._test["results"][-1]["itemId"])
				except ValueError:
					# Not in list anymore
					pass
			
			if len(randomGroup) > 1:
				# Get random number
				r = random.randrange(0, len(randomGroup) - 1)
			else:
				r = 0
			
			if len(randomGroup) > 0:
				# There is more than one left, so ask another one than the last one
				self.newItem.send(self._list["items"][randomGroup[r]])
			else:
				# There is only one left, so ask that one
				self.newItem.send(self._list["items"][self._group[0]])

		#Just send the next question and everything will be fine :)
		skip = _sendNext

class IntervalModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(IntervalModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "lessonType"
		self.requires = (
			self._mm.mods(type="event"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)

	def enable(self):
		#Translations
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		# Settings
		for module in self._mm.mods("active", type="settings"):#FIXME: choose one
			module.registerSetting(
				"org.openteacher.lessonTypes.interval.groupSize",
				"Max. size of group",
				"number",
				"Lessons",
				"Interval",
				defaultValue=4
			)
		for module in self._mm.mods("active", type="settings"):
			module.registerSetting(
				"org.openteacher.lessonTypes.interval.minQuestions",
				"Min. questions asked",
				"number",
				"Lessons",
				"Interval",
				defaultValue=2
			)
		for module in self._mm.mods("active", type="settings"):
			module.registerSetting(
				"org.openteacher.lessonTypes.interval.whenKnown",
				"% right before known",
				"number",
				"Lessons",
				"Interval",
				defaultValue=80
			)

		self.newItem = self._createEvent()
		self.name = _("Interval")
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.newItem
		del self.name

	@property
	def _createEvent(self):
		return self._modules.default(type="event").createEvent

	def createLessonType(self, list, indexes):
		lessonType = IntervalLessonType(self._mm, self._createEvent, list, indexes)
		lessonType.newItem.handle(self.newItem.send)
		return lessonType

def init(moduleManager):
	return IntervalModule(moduleManager)
