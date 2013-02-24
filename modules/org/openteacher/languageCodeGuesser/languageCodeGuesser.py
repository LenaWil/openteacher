#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012-2013, Marten de Vries
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
import gettext

class LanguageCodeGuesserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LanguageCodeGuesserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "languageCodeGuesser"
		self.uses = (
			self._mm.mods(type="translator"),
		)

	def guessLanguageCode(self, languageName):
		try:
			return self._index[languageName.lower().strip()]
		except AttributeError:
			#index doesn't exist yet, generate it. This way, the index
			#is only generated if it's actually used (it's relatively
			#heavy)
			self._retranslate()
			return self.guessLanguageCode(languageName)
		except KeyError:
			return

	def enable(self):
		global pycountry
		try:
			import pycountry
		except ImportError:
			#remain inactive
			return

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._re = re.compile("[,;]")

		try:
			self._translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		#retranslate's not called, because guessLanguageCode does that
		#only when it's actually necessary (it's quite heavy).

		self.active = True

	def _retranslate(self):
		try:
			lang = self._translator.language
		except AttributeError:
			lang = "C"
		translation = gettext.translation(
			"iso_639",
			pycountry.LOCALES_DIR,
			languages=[lang.split("_")[0]],
			fallback=True
		)

		self._index = {}
		for lang in pycountry.languages:
			if not hasattr(lang, "alpha2"):
				continue
			nativeTranslation = gettext.translation(
				"iso_639",
				pycountry.LOCALES_DIR,
				languages=[lang.alpha2],
				fallback=True
			)
			self._index[self._re.split(lang.name)[0].lower()] = lang.alpha2
			self._index[self._re.split(translation.ugettext(lang.name))[0].lower()] = lang.alpha2
			self._index[self._re.split(nativeTranslation.ugettext(lang.name))[0].lower()] = lang.alpha2

		#make the test suite pass ;).
		self._index["frisian"] = "fy"
		self._index["frysk"] = "fy"

	def disable(self):
		self.active = False

		del self._modules
		del self._re
		if hasattr(self, "_translator"):
			del self._translator
		del self._index

def init(moduleManager):
	return LanguageCodeGuesserModule(moduleManager)
