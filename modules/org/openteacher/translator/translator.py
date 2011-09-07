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

	def enable(self):
		self.active = True
		gettext.install("OpenTeacher")#FIXME

	def gettextFunctions(self, localeDir):
		#FIXME: use module which also gives the possibility to choose
		language = locale.getdefaultlocale()[0]
		path = os.path.join(localeDir, language + ".mo")
		if not os.path.isfile(path):
			path = os.path.join(localeDir, language.split("_")[0] + ".mo")
		if os.path.isfile(path):
			t = gettext.GNUTranslations(open(path, "rb"))
			return t.ugettext, t.ungettext
		return unicode, unicode

	def disable(self):
		self.active = False

def init(moduleManager):
	return TranslatorModule(moduleManager)
