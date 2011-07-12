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

class SortModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SortModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "listModifier"

	def modifyList(self, indexes, list):
		def getFirstQuestion(word):
			try:
				return word.questions[0]
			except IndexError:
				return None
		#always work on the indexes
		currentList = [list.words[i] for i in indexes]
		newList = sorted(currentList, key=getFirstQuestion)
		return [list.words.index(word) for word in newList]

	def enable(self):
		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)
		self.dataType = "words"
		self.name = _("Sort")
		self.active = True

	def disable(self):
		self.active = False
		del self.dataType
		del self.name

def init(moduleManager):
	return SortModule(moduleManager)
