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
import shutil

class SourcePackagerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SourcePackagerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "sourcePackager"

		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="metadata"),
			self._mm.mods(type="sourceSaver"),
		)
		self.priorities = {
			"default": -1,
			"package-source": 0,
		}

	def enable(self):
		global pyratemp
		try:
			import pyratemp
		except ImportError:
			return #fail silently: stay inactive
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self._run)
		self._metadata = self._modules.default("active", type="metadata").metadata

		self.active = True

	def _run(self):
		try:
			path = sys.argv[1]
		except IndexError:
			sys.stderr.write("Please specify a path for the source tarball (ending in .tar.gz) as the last command line argument.\n")
			return

		sourcePath = self._modules.default("active", type="sourceSaver").saveSource()

		#move into python package
		packageName = os.path.basename(sys.argv[0])
		if packageName.endswith(".py"):
			packageName = packageName[:-3]
		packagePath = os.path.join(sourcePath, packageName)
		os.mkdir(packagePath)
		for item in os.listdir(sourcePath):
			if item != packageName:
				os.rename(
					os.path.join(sourcePath, item),
					os.path.join(packagePath, item)
				)

		#write __init__.py
		open(os.path.join(packagePath, "__init__.py"), "a").close()

		#find all files for package_data
		modulePath = os.path.join(packagePath, "modules")
		def getDifference(root):
			return root[len(os.path.commonprefix([packagePath, root])) +1:]

		packageData = []
		for root, dirs, files in os.walk(modulePath):
			if len(files) == 0:
				continue
			root = getDifference(root)
			for file in files:
				packageData.append(os.path.join(root, file))

		data = self._metadata.copy()
		data.update({
			"package": packageName,
			"package_data": packageData,
		})

		os.mkdir(os.path.join(sourcePath, "bin"))
		with open(os.path.join(sourcePath, "bin", packageName), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("runner.templ"))
			#ascii since the file doesn't have a encoding directive
			f.write(templ(name=packageName).encode("ascii"))

		with open(os.path.join(sourcePath, "setup.py"), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("setup.py.templ"))
			f.write(templ(**data).encode("UTF-8"))

		with tarfile.open(path, "w:gz") as f:
			for item in os.listdir(sourcePath):
				f.add(os.path.join(sourcePath, item), item)

	def disable(self):
		self.active = False

		del self._modules
		del self._metadata

def init(moduleManager):
	return SourcePackagerModule(moduleManager)
