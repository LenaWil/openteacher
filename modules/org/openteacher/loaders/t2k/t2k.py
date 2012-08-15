#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

try:
	from lxml import etree as ElementTree
except ImportError:
	try:
		from xml.etree import ElementTree
	except ImportError:
		from elementTree import ElementTree
import datetime
import re

class Teach2000LoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(Teach2000LoaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "load"
		self.priorities = {
			"student@home": 648,
			"student@school": 648,
			"teacher": 648,
			"wordsonly": 648,
			"selfstudy": 648,
			"testsuite": 648,
			"codedocumentation": 648,
			"all": 648,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("t2k.py",)

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.name = _("Teach2000")

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.loads = {"t2k": ["words"]}

		self.active = True

	def disable(self):
		self.active = False

		del self.name
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".t2k"):
			#also support other formats in the future? Well, everything
			#can be opened like it's of type 'words'...
			return "words"

	def load(self, path):
		"""Loads a .t2k file into the OpenTeacher data structure.
		   http://teach2000.memtrain.com/help/00513_advanced_file_format.htm"""
		root = ElementTree.parse(open(path)).getroot()
		wordList = {
			"items": list(),
			"tests": list(),
		}

		#create one test to save all results in that are in the t2k file
		#(t2k doesn't have enough information to know which word was
		#wrong in which test, so we can have only one test.)
		test = {
			"finished": True,
			"results": [],
		}
		for item in root.findall("message_data/items/item"):
			word = {
				"id": int(),
				"questions": list(),
				"answers": list(),
			}

			#id
			word["id"] = int(item.get("id"))

			#questions
			word["questions"].append([])
			for question in item.findall(".//question"):
				#strip BBCode for now
				word["questions"][0].append(
					self._stripBBCode(question.text)
				)

			#answers
			word["answers"].append([])
			for answer in item.findall(".//answer"):
				#strip BBCode for now
				word["answers"][0].append(
					self._stripBBCode(answer.text)
				)

			#remarks (comment in OT)
			word["comment"] = item.findtext("remarks")

			#add a result for every time this word was wrong
			for i in range(int(item.findtext("errors") or 0)):
				test["results"].append({
					"itemId": word["id"],
					"result": "wrong",
				})
			#add a result for every time this word was right
			for i in range(int(item.findtext("correctcount") or 0)):
				test["results"].append({
					"itemId": word["id"],
					"result": "right",
				})

			wordList["items"].append(word)
		#if there were results
		if test["results"]:
			#get the time of the first start result and the one of the
			#last for a global idea of the time range of this 'mega'
			#test. Duration isn't used, since it's way off anyway.
			try:
				startTime = root.findall("message_data/testresults/testresult")[0].findtext("dt")
				endTime = root.findall("message_data/testresults/testresult")[-1].findtext("dt")
			except IndexError:
				pass
			else:
				startTime = self._parseDt(startTime)
				endTime = self._parseDt(endTime)

				#store those times in the first and last result. (which may
				#be the same, technically, but that doesn't matter...)
				test["results"][0]["active"] = {
					"start": startTime,
					"end": startTime,
				}
				test["results"][-1]["active"] = {
					"start": endTime,
					"end": endTime
				}

			#append the test to the list
			wordList["tests"] = [test]
		return {
			"resources": {},
			"list": wordList,
		}

	def _stripBBCode(self, string):
		"""Strips all BBCode tags"""
		return re.sub(r"\[[\w/]*\]", u"", string)

	def _parseDt(self, string):
		"""Parses a date string as found in T2K files to a datetime
		   object."""
		return datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%f")

def init(manager):
	return Teach2000LoaderModule(manager)
