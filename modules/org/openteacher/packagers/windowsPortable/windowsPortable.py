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

import zipfile
import sys

class WindowsPortablePackagerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WindowsPortablePackagerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "windowsPortablePackager"
		self.requires = (
			self._mm.mods(type="pydistInterface"),
			self._mm.mods(type="execute"),
		)
		self.priorities = {
			"package-windows-portable": 0,
			"default": -1,
		}

	def _run(self):
		try:
			zipLoc = sys.argv[1]
		except IndexError:
			sys.stderr.write("Please specify a filename to write to as the last command line argument.\n")
			return
		#build to exe, dll etc.
		resultDir = self._pydist.build("windows")

		#create zip file
		with zipfile.ZipFile(zipLoc, "w", zipfile.ZIP_DEFLATED) as f:
			for root, dirs, files in os.listdir(resultDir):
				for file in files:
					f.write(os.path.join(root, f))

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._pydist = self._modules.default("active", type="pydistInterface")

		self._modules.default(type="execute").startRunning.handle(self._run)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._pydist

def init(moduleManager):
	return WindowsPortablePackagerModule(moduleManager)
