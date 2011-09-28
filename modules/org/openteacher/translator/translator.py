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

import gettext
import locale
import os

class TranslatorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TranslatorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "translator"
		self.uses = (
			self._mm.mods("event"),
			self._mm.mods("languageChooser"),
		)

	def enable(self):
		self.active = True

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.languageChanged = self._modules.default(
			type="event"
		).createEvent()
		#gettext.install("OpenTeacher")#FIXME

	@property
	def language(self):
		language = None#FIXME: use module which also gives the possibility to choose
		if not language:
			try:
				lc = self._modules.default("active", type="languageChooser")
			except IndexError:
				pass
			else:
				language = lc.language
		if not language:
			language = locale.getdefaultlocale()[0]
		return language

	def gettextFunctions(self, localeDir, language=None):
		if not language:
			language = self.language
		path = os.path.join(localeDir, language + ".mo")
		if not os.path.isfile(path):
			path = os.path.join(localeDir, language.split("_")[0] + ".mo")
		if os.path.isfile(path):
			t = gettext.GNUTranslations(open(path, "rb"))
			return t.ugettext, t.ungettext
		return unicode, lambda x, y, n: x if n == 1 else y

	def disable(self):
		self.active = False

		del self._modules
		del self.languageChaned

def init(moduleManager):
	return TranslatorModule(moduleManager)
