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
		self.requires = (
			self._mm.mods(type="uiController"),
			self._mm.mods(type="modulesActivator"),
		)

	def execute(self):
		parser = optparse.OptionParser()
		#FIXME: add options, or remove this parser :P
		options, args = parser.parse_args()
		try:
			path = args[0]
		except IndexError:
			path = None

		modules = set(self._mm.mods(type="modules")).pop()
		modules.default(type="modulesActivator").activateModules()

		uiController = modules.default("active", type="uiController")
		uiController.run(path)

def init(moduleManager):
	return ExecuteModule(moduleManager)
