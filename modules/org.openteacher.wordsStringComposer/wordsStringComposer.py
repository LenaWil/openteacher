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

class WordsStringComposerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsStringComposerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("wordsStringComposer",)
		self.requires = (1, 0)
		self.active = False

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

	def compose(self, item):
		if len(item) == 0:
			return u""
		elif len(item) == 1:
			return u", ".join(item[0])
		else:
			text = u""
			counter = 1
			for obligatorySet in item:
				text += u"".join([
					unicode(counter),
					u". ",
					u", ".join(obligatorySet),
					u" "
				])
				counter += 1
			return text.strip()

def init(moduleManager):
	return WordsStringComposerModule(moduleManager)
