#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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

class HtmlSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(HtmlSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"
		self.priorities = {
			"student@home": 616,
			"student@school": 616,
			"teacher": 616,
			"wordsonly": 616,
			"selfstudy": 616,
			"testsuite": 616,
			"codedocumentation": 616,
			"all": 616,
		}

		self.requires = (
			self._mm.mods(type="wordsHtmlGenerator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.name = "Hyper Text Markup Language"
		self.saves = {"words": ["html"]}
		
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.saves

	def save(self, type, lesson, path):
		html = self._modules.default(
			"active",
			type="wordsHtmlGenerator"
		).generate(lesson, margin="0.5em")

		with open(path, 'w') as htmlfile:
			htmlfile.write(html)

def init(moduleManager):
	return HtmlSaverModule(moduleManager)
