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
			(u"А", u"а", u"Б", u"б", u"В", u"в"),
			(u"Г", u"г", u"Д", u"д", u"Е", u"е"),
			(u"Ё", u"ё", u"Ж", u"ж", u"З", u"з"),
			(u"И", u"и", u"Й", u"й", u"К", u"к"),
			(u"Л", u"л", u"М", u"м", u"Н", u"н"),
			(u"О", u"о", u"П", u"п", u"Р", u"р"),
			(u"С", u"с", u"Т", u"т", u"У", u"у"),
			(u"Ф", u"ф", u"Х", u"х", u"Ц", u"ц"),
			(u"Ч", u"ч", u"Ш", u"ш", u"Щ", u"щ"),
			(u"Ъ", u"ъ", u"Ы", u"ы", u"Ь", u"ь"),
			(u"Э", u"э", u"Ю", u"ю", u"Я", u"я"),
		)
		self.active = True

	def disable(self):
		self.active = False
		del self.name
		del self.data

def init(moduleManager):
	return CyrillicModule(moduleManager)
