#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

import re

class WordsStringParserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsStringParserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("wordsStringParser",)
		self.requires = (1, 0)
		self.active = False

	def parse(self, text):
		obligatorySegments = self._regex.split(text)
		obligatorySegments = filter(lambda x: x.strip() != u"", obligatorySegments)
		item = []
		for segment in obligatorySegments:
			words = segment.split(",")
			words = [word.strip() for word in words]
			words = filter(lambda x: x.strip() != u"", words)
			item.append(tuple(words))
		return item

	def enable(self):
		self._regex = re.compile(r"[0-9]+\.")
		self.active = True

	def disable(self):
		self.active = False
		del self._regex

def init(moduleManager):
	return WordsStringParserModule(moduleManager)
