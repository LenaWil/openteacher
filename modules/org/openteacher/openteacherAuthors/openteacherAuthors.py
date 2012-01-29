#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

class OpenTeacherAuthorsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherAuthorsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "openteacherAuthors"
		self.uses = (
			self._mm.mods(type="authors"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		a = self._modules.default("active", type="authors")

		#Core development team
		a.registerAuthor("Core developer", "Milan Boers") #FIXME: translate
		a.registerAuthor("Core developer", "Cas Widdershoven")
		a.registerAuthor("Core developer", "Marten de Vries")

		#Patches
		a.registerAuthor("Patches contributor", "Roel Huybrechts")
		a.registerAuthor("Patches contributor", "David D Lowe")

		#Packaging
		a.registerAuthor("Debian/Ubuntu packager", "Charlie Smotherman")

		#Artwork
		a.registerAuthor("Artwork", "Yordi de Graaf")

		#Translators
		#FIXME: add them here

		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return OpenTeacherAuthorsModule(moduleManager)
