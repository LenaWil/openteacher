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

import tarfile
import sys
import os

class SourcePackagerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SourcePackagerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "sourcePackager"

		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="sourceSaver"),
		)
		self.priorities = {
			"default": -1,
			"package-source": 0,
		}

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self._run)

		self.active = True

	def _run(self):
		try:
			path = sys.argv[1]
		except IndexError:
			sys.stderr.write("Please specify a path for the source tarball (ending in .tar.gz) as the last command line argument.\n")
			return

		sourcePath = self._modules.default("active", type="sourceSaver").saveSource()
		with tarfile.open(path, "w:gz") as f:
			for item in os.listdir(sourcePath):
				f.add(item)

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return SourcePackagerModule(moduleManager)
