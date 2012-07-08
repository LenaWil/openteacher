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

	def build(self, target):
		#FIXME: put all files into one tar file where you link to.
		source = self._modules.default(type="sourceSaver").saveSource()
		exe = os.path.join(source, os.path.basename(sys.argv[0]))
		if target == "windows":
			pythonPath = "C:\Python{0}{1}".format(*sys.version_info)
		elif target == "macosx":
			pythonPath = "/opt/local/Library/Frameworks/Python.framework/Versions/{0}.{1}".format(*sys.version_info)
		else:
			raise ValueError("target should be 'windows' or 'macosx'!")

		pd = pydist.PyDist(source)
		lib = pd.createPythonLibrary(**{
			"exe": exe,
			"pythonLib": pythonPath,
			"includes": [],
			"compile": False,
		})
		#mark for removal atexit
		self._temp.add(lib)

		if target == "windows":
			if os.path.isfile(os.path.join(os.environ["SYSTEMROOT"], "SysWOW64\python27.dll")):
				winDllPath = os.path.join(os.environ["SYSTEMROOT"], "SysWOW64\python27.dll")
			elif os.path.join(os.environ["SYSTEMROOT"], "System32\python27.dll"):
				winDllPath = os.path.join(os.environ["SYSTEMROOT"], "System32\python27.dll")
			else:
				raise Exception("No python DLL found.")
			pd.createWindowsPackage(**{
				"exe": exe,
				"libLocation": lib,
				"pythonPath": pythonPath,
				"winDllPath": winDllPath,
				"console": False,
				"compile": False,
			})
			return pd.winDistDir
		elif target == "macosx":
			qtLibsPath = "/opt/local/lib"
			if not os.path.isfile(qtLibsPath):
				raise ValueError("Dir doesn't exist...")
			pdf.createOSXPackage(**{
				"exe": exe,
				"name": self._metadata["name"],
				"libLocation": lib,
				"pythonPath": pythonPath,
				"iconPath": self._generateIcns(self._metadata["iconPath"]),
				"qtLibsPath": qtLibsPathh,
				"qtMenuPath": "qtmenu.nib", #orsomethinglikethat.
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
