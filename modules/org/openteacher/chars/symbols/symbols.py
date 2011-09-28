#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
#	Copyright 2008-2011, Milan Boers
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

class SymbolsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SymbolsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "onscreenKeyboardData"
		self.uses = (
			self._mm.mods(type="translator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.data = (
			(u"à", u"á", u"â", u"ä", u"ã", u"å"),
			(u"À", u"Á", u"Â", u"Ä", u"Ã", u"Å"),
			(u"è", u"é", u"ê", u"ë", u"Ç", u"ç"),
			(u"È", u"É", u"Ê", u"Ë", u"Ñ", u"ñ"),
			(u"ì", u"í", u"î", u"ï", u"Û", u"û"),
			(u"Ì", u"Í", u"Î", u"Ï", u"Ú", u"ú"),
			(u"ò", u"ó", u"ô", u"ö", u"Ü", u"ü"),
			(u"Ò", u"Ó", u"Ô", u"Ö", u"Ù", u"ß")
		)
		self.active = True

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.name = _("Symbols")

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.data

def init(moduleManager):
	return SymbolsModule(moduleManager)
