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

import sys
import os
import atexit
import shutil
import tempfile
import subprocess
import tarfile

#pydist is imported in enable()

class PyDistInterfaceModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(PyDistInterfaceModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "pydistInterface"
		self.requires = (
			self._mm.mods(type="sourceSaver"),
			self._mm.mods(type="metadata"),
		)
		atexit.register(self._removeTemp)
		self._temp = set()

	def _removeTemp(self):
		for thing in self._temp:
			if os.path.isdir(thing):
				shutil.rmtree(thing)
			else:
				os.unlink(thing)

	def build(self, dataZip, target):
		dataPath = tempfile.mkdtemp()
		self._temp.add(dataPath)
		with tarfile.open(dataZip) as f:
			members = []
			#filter members trying to get out of the temp dir. (Just to
			#be sure.)
			for m in f.getmembers():
				if not os.path.normpath(m.name).startswith(os.pardir):
					members.append(m)
			f.extractall(dataPath, members)

		source = self._modules.default(type="sourceSaver").saveSource()
		exe = os.path.join(source, os.path.basename(sys.argv[0]))
		pythonPath = os.path.join(dataPath, "Python{0}{1}").format(*sys.version_info)

		pd = pydist.PyDist(source)
		lib = pd.createPythonLibrary(**{
			"exe": exe,
			"pythonLib": os.path.join(pythonPath, "Lib"),
			"includes": [],
			"compile": False,
		})
		#mark for removal atexit
		self._temp.add(lib)
		self._temp.add(os.path.join(os.path.dirname(source), "dist"))

		if target == "windows":
			pd.createWindowsPackage(**{
				"exe": exe,
				"libLocation": lib,
				"pythonPath": pythonPath,
				"dllPath": os.path.join(dataPath, "python{0}{1}.dll").format(*sys.version_info),
				"console": False,
				"compile": False,
			})
			return pd.winDistDir
		elif target == "macosx":
			pd.createOSXPackage(**{
				"exe": exe,
				"name": self._metadata["name"],
				"libLocation": lib,
				"pythonPath": pythonPath,
				"iconPath": self._generateIcns(self._metadata["iconPath"]),
				"qtLibsPath": os.path.join(dataPath, "qtLibs"),
				"qtMenuPath": os.path.join(dataPath, "qtMenu"),
				"compile": False
			})
			return pd.macDistDir

	def _generateIcns(self, path):
		icnsPath = tempfile.mkstemp(suffix=".icns")[1]
		self._temp.add(icnsPath)
		subprocess.check_call(["png2icns", icnsPath, path])
		return icnsPath

	def enable(self):
		global pydist
		try:
			import pydist
		except ImportError:
			return #stay disabled

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._metadata = self._modules.default("active", type="metadata").metadata
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._metadata

def init(moduleManager):
	return PyDistInterfaceModule(moduleManager)
