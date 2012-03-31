#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

import code

BANNER_TEMPL = """Welcome to the {appname} {appversion} interactive Python shell!

The module manager is in the 'mm' variable. For your convenience, we 
also added the 'modules' module in the 'modules' variable so you can
start experimenting with modules right away. Have fun!"""

class ShellModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShellModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "shell"
		self.priorities = {
			"student@home": -1,
			"student@school": -1,
			"teacher": -1,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": -1,
			"codedocumentation": -1,
			"all": -1,
			"update-translations": -1,
			"testserver": -1,
			"shell": 0
		}
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="metadata"),
		)

	def _run(self):
		banner = BANNER_TEMPL.format(**{
			"appname": self._metadata["name"],
			"appversion": self._metadata["version"],
		})
		args = {
			"banner": banner,
			"local": {
				"mm": self._mm,
				"modules": self._modules,
			}
		}
		try:
			code.interact(**args)
		except SystemExit:
			#exit the OpenTeacher way.
			print "Have a nice day!"

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._metadata = self._modules.default(type="metadata").metadata
		self._execute = self._modules.default(type="execute")
		self._execute.startRunning.handle(self._run)

		self.active = True

	def disable(self):
		self.active = False
		del self._modules
		del self._metadata
		del self._execute

def init(moduleManager):
	return ShellModule(moduleManager)
