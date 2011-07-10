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

import optparse

class ExecuteModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ExecuteModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "execute"

	def execute(self):
		parser = optparse.OptionParser()
		parser.add_option(
			"-u",
			"--ui",
			dest="ui",
			help="tells OpenTeacher to load the specified UI",
			default="qt" #FIXME: should Qt be fixed?
		)
		options, args = parser.parse_args()
		try:
			path = args[0]
		except IndexError:
			path = None

		for module in self._mm.mods(type="uiController"): #FIXME: choose a uiController. Maybe obligatory one like openteacher-core? Or command line setting?
			module.enable()
			module.initialize(options.ui)

		for module in self._mm.mods(type="modules"): #FIXME: choose a 'modules'. Maybe obligatory one like openteacher-core? Or command line setting?
			module.enable()
			module.activateModules()

		for module in self._mm.mods("active", type="uiController"):
			module.run(path)

def init(moduleManager):
	return ExecuteModule(moduleManager)
