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

import sys

class OpenTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "openteacher-core"
		self.requires = ( #FIXME: let modules registering themselves (so they're not longer dependencies)
			self._mm.mods(type="testRunner"),
			self._mm.mods(type="execute"),
		)

	def run(self):
		try:
			mode = sys.argv[1]
		except IndexError:
			mode = "execute"
		else:
			if mode in ("execute", "test"):
				del sys.argv[1]

		modulesMods = set(self._mm.mods(type="modules"))
		if len(modulesMods) != 1:
			raise ValueError("There has to be exactly one modules module installed.")
		modules = modulesMods.pop()
		modules.enable()

		if mode == "test":
			modules.default(type="testRunner").run()
		else:
			#execute
			modules.default(type="execute").execute()

def init(moduleManager):
	return OpenTeacherModule(moduleManager)
