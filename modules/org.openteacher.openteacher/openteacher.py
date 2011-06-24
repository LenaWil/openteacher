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

class OpenTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "openteacher-core"

	def run(self): #FIXME: should options and modes be added dynamically? If so, how?
		parser = optparse.OptionParser()
		parser.add_option(
			"-m",
			"--mode",
			dest="mode",
			help="teels OpenTeacher to operate in the specified MODE.",
			default="execute"
		)
		parser.add_option(
			"-u",
			"--ui",
			dest="ui",
			help="tells OpenTeacher to load the specified UI",
			default="qt" #FIXME: should Qt be fixed?
		)
		options, args = parser.parse_args()
		if options.mode == "execute":
			try:
				args[0]
			except IndexError:
				for module in self._mm.mods(type="execute"): #FIXME: choose an executor. Maybe obligatory one like openteacher-core? Or command line setting?
					module.execute(options.ui)
			else:
				for module in self._mm.mods(type="execute"): #FIXME: choose an executor. Maybe obligatory one like openteacher-core? Or command line setting?
					module.execute(options.ui, args[0])
		elif options.mode == "test":
			for module in self._mm.mods(type="testRunner"): #FIXME: choose a test runner. Maybe obligatory one like openteacher-core? Or command line setting?
				module.run()

def init(moduleManager):
	return OpenTeacherModule(moduleManager)
