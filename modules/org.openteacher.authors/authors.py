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

class AuthorsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AuthorsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "authors"

	def registerAuthor(self, category, name):
		self._authors.add((category, name))

	@property
	def registeredAuthors(self):
		return self._authors.copy()

	def enable(self):
		self._authors = set()
		self.active = True

		##########FIXME: DEMO DATA
		self.registerAuthor("Core developer", "Milan Boers")
		self.registerAuthor("Core developer", "Cas Widdershoven")
		self.registerAuthor("Core developer", "Marten de Vries")
		##########END DEMO DATA

	def disable(self):
		self.active = False
		del self._authors

def init(moduleManager):
	return AuthorsModule(moduleManager)
