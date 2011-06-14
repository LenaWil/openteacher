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

class OpenTeachingWordsSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingWordsSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("save", "initializing")
		self.requires = (1, 0)
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Open Teaching Words (.otwd) saver", self)

	def enable(self):
		self.saves = {"words": ["otwd"]}
		self._pyratemp = self._mm.import_("pyratemp")
		self.active = True

	def disable(self):
		self.active = False
		del self.saves
		del self._pyratemp

	def save(self, type, list, path):
		templatePath = self._mm.resourcePath("index.xml")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"list": list
		}
		content = t(**data)
		print content.encode("UTF-8")

def init(moduleManager):
	return OpenTeachingWordsSaverModule(moduleManager)
