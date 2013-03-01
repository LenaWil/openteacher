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

import os

MODULES_PATH = os.path.join(os.path.dirname(__file__), "modules")

class ModuleApplication(object):
	def run(self):
		import moduleManager

		mm = moduleManager.ModuleManager(MODULES_PATH)

		#check if there's only one execute module
		mods = set(mm.mods(type="execute"))
		if len(mods) != 1:
			raise ValueError("There has to be exactly one execute module installed.")
		#start that module
		mods.pop().execute()
		#nothing crashed, so exit code's 0.
		return 0

if __name__ == "__main__":
	#Used for development only. All packaged versions should call the
	#ModuleApplication class directly, to circumvent pyximport.
	import sys
	import pyximport
	pyximport.install()

	app = ModuleApplication()
	sys.exit(app.run())
