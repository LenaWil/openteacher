#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

class IntervalLessonType(object):
	def __init__(self, createEvent, list, indexes, modifyItem, groupSizeSetting, minQuestionsSetting, whenKnownSetting, *args, **kwargs):
		super(IntervalLessonType, self).__init__(*args, **kwargs)

		self.newItem = createEvent()
		self.lessonDone = createEvent()
		self.list = list
		self._indexes = indexes
		self._modifyItem = modifyItem or (lambda item: item)

		self._groupSizeSetting = groupSizeSetting
		self._minQuestionsSetting = minQuestionsSetting
		self._whenKnownSetting = whenKnownSetting

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
		size = self._groupSizeSetting["value"]
		if size < 2:
			size = 2

		# Add items to the group
		for i in xrange(size):
			try:
				self.list["items"][i]
			except IndexError:
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
			self.list["tests"][-1]
		except KeyError:
			self.list["tests"] = [self._test]
		except IndexError:
			self.list["tests"].append(self._test)
		else:
			if not self.list["tests"][-1] == self._test:
				self.list["tests"].append(self._test)

	def _sendNext(self):
		minQuestions = self._minQuestionsSetting["value"]
		if minQuestions < 1:
			minQuestions = 2

		whenKnown = self._whenKnownSetting["value"]
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
					self.list["items"][self._group[-1] + 1]
				except IndexError:
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
					self.list["tests"]
				except KeyError:
					self.list["tests"] = []
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
				item = self.list["items"][randomGroup[r]]
				self.newItem.send(self._modifyItem(item))
			else:
				# There is only one left, so ask that one
				item = self.list["items"][self._group[0]]
				self.newItem.send(self._modifyItem(item))

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
			self._mm.mods(type="settings"),
		)
		self.filesWithTranslations = ("interval.py",)
		self.priorities = {
			"default": 170,
		}

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		# Settings
		try:
			self._settings = self._modules.default(type="settings")
		except IndexError, e:
			self._whenKnownSetting = {"value": 80}
			self._minQuestionsSetting = {"value": 2}
			self.__groupSizeSetting = {"value": 4}
		else:
			self._groupSizeSetting = self._settings.registerSetting(**{
				"internal_name": "org.openteacher.lessonTypes.interval.groupSize",
				"type": "number",
				"defaultValue": 4,
				"minValue": 1,
			})
			self._minQuestionsSetting = self._settings.registerSetting(**{
				"internal_name": "org.openteacher.lessonTypes.interval.minQuestions",
				"type": "number",
				"defaultValue": 2,
				"minValue": 1,
			})
			self._whenKnownSetting = self._settings.registerSetting(**{
				"internal_name": "org.openteacher.lessonTypes.interval.whenKnown",
				"type": "number",
				"defaultValue":80,
				"minValue": 0,
				"maxValue": 99,
			})

		self.newItem = self._createEvent()

		#register _retranslate()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		#install translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.name = _("Interval")

		#settings
		categories = {
			"category": _("Lesson type"),
			"subcategory": _("Interval"),
		}
		self._groupSizeSetting["name"] = _("Maximum size of group")
		self._groupSizeSetting.update(categories)
		self._minQuestionsSetting["name"] = _("Minimum amount of questions asked")
		self._minQuestionsSetting.update(categories)
		self._whenKnownSetting["name"] = _("Percent right before known")
		self._whenKnownSetting.update(categories)

	def disable(self):
		self.active = False

		del self._modules
		del self._settings
		del self._groupSizeSetting
		del self._minQuestionsSetting
		del self._whenKnownSetting

		del self.newItem
		del self.name

	@property
	def _createEvent(self):
		return self._modules.default(type="event").createEvent

	def createLessonType(self, list, indexes, modifyItem=None):
		lessonType = IntervalLessonType(self._createEvent, list, indexes, modifyItem, self._groupSizeSetting, self._minQuestionsSetting, self._whenKnownSetting)
		lessonType.newItem.handle(self.newItem.send)
		return lessonType

def init(moduleManager):
	return IntervalModule(moduleManager)
