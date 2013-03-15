#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

class Checker(object):
	def __init__(self, languageCode, *args, **kwargs):
		super(Checker, self).__init__(*args, **kwargs)

		self._dict = enchant.Dict(languageCode)

	def check(self, word):
		return self._dict.check(word)

class SpellCheckModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SpellCheckModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "spellChecker"
		self.requires = (
			self._mm.mods(type="languageCodeGuesser"),
		)

	_guessLanguageCode = property(lambda self: self._modules.default("active", type="languageCodeGuesser").guessLanguageCode)

	def createChecker(self, language):
		languageCode = self._guessLanguageCode(language)
		return Checker(languageCode)

	def enable(self):
		global enchant
		try:
			import enchant
		except ImportError:
			return
		self._modules = next(iter(self._mm.mods(type="modules")))

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return SpellCheckModule(moduleManager)
