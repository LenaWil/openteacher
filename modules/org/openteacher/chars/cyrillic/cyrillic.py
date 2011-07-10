#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
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

class CyrillicModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(CyrillicModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "onscreenKeyboardData"

	def enable(self):
		self.name = _("Cyrillic")
		self.data = (
			(u"а", u"б", u"в", u"г", u"д", u"e"),
			(u"A", u"Б", u"B", u"Г", u"Д", u"E"),
			(u"ë", u"ж", u"з", u"и", u"й", u"к"),
			(u"Ë", u"Ж", u"З", u"И", u"Й", u"K"),
			(u"л", u"м", u"н", u"o", u"п", u"р"),
			(u"Л", u"M", u"H", u"O", u"П", u"P"),
			(u"с", u"т", u"у", u"ф", u"x", u"ц"),
			(u"C", u"T", u"y", u"Ф", u"X", u"Ц"),
			(u"ч", u"ш", u"щ", u"ъ", u"ы", u"ь"),
			(u"Ч", u"Ш", u"Щ", u"Ъ", u"Ы", u"Ь"),
			(u"э", u"ю", u"я", u"Э", u"Ю", u"Я"),
		)
		self.active = True

	def disable(self):
		self.active = False
		del self.name
		del self.data

def init(moduleManager):
	return CyrillicModule(moduleManager)
