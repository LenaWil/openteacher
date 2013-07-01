#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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
import os

class AutoPackagerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AutoPackagerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "autoPackager"
		self.priorities = {
			"package-all": 0,
			"default": -1,
		}
		self.requires = (
			self._mm.mods(type="execute"),
		)

	def _run(self):
		try:
			outputDir = sys.argv[1]
		except IndexError:
			print("Please specify a (preferably empty) directory to save the resultive packages to.")
			return
		print("This script requires an exactly right environment. It needs ssh, VirtualBox and properly installed VM's to start with. See the script source for more details. Otherwise, it'll probably crash in 3. 2. 1...")
		os.makedirs(outputDir)
		self._packageAll.main(outputDir)

	def enable(self):
		self._modules = next(iter(self._mm.mods(type="modules")))
		self._modules.default("active", type="execute").startRunning.handle(self._run)
		self._packageAll = self._mm.import_("package-all")

		self.active = True

	def disable(self):
		self.active = False

		del self._packageAll
		self._modules.default("active", type="execute").startRunning.unhandle(self._run)
		del self._modules

def init(moduleManager):
	return AutoPackagerModule(moduleManager)
