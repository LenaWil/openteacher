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

import moduleManager
import sys
import os

MODULES_PATH = os.path.join(os.path.dirname(__file__), "modules")

class OpenTeacher(object):
	def run(self):
		mm = moduleManager.ModuleManager(MODULES_PATH)

		for module in mm.mods.supporting("execute"):
			module.run()
		return 0

if __name__ == "__main__":
	openTeacher = OpenTeacher()
	sys.exit(openTeacher.run())
