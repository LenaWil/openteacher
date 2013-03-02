#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012-2013, Marten de Vries
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

import subprocess
import platform
import tempfile
import atexit
import os
import shutil

class PyinstallerInterfaceModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(PyinstallerInterfaceModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "pyinstallerInterface"
		self.requires = (
			self._mm.mods(type="sourceSaver"),
			self._mm.mods(type="metadata")
		)
		self._tempPaths = set()
		atexit.register(self._cleanup)

	@property
	def _saveSource(self):
		return self._modules.default("active", type="sourceSaver").saveSource

	def build(self):
		path = tempfile.mkdtemp()
		self._tempPaths.add(path)
		shutil.copy(
			self._mm.resourcePath("icon.ico"),
			os.path.join(path, "icon.ico")
		)
		with open(os.path.join(path, "starter.py"), "w") as f:
			f.write("""
import sys
import os

if not sys.frozen:
	#import OT dependencies, so PyInstaller adds them to the build.
	#not required at runtime though, so that's why the if statement
	#above is here.
	from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork, phonon, QtScript, QtOpenGL
	import webbrowser
	import json
	import mimetypes
	import shutil
	import platform
	import atexit
	import urllib
	import urllib2
	import weakref
	import argparse
	import sqlite3
	import itertools
	import subprocess
	import zipfile
	import uuid
	import csv
	import code
	import xml.dom.minidom
	import docutils
	import chardet
	import contextlib
	import bisect
	#windows only, so wrapped.
	try:
		import win32com
	except ImportError:
		pass
	from xml.etree import ElementTree

sys.path.insert(0, os.path.join(os.path.dirname(sys.executable), 'source'))
sys.exit(__import__('openteacher').ModuleApplication().run())
			""")
		cwd = os.getcwd()
		os.chdir(path)
		subprocess.check_call([
			"C:\Python{0}{1}\python.exe".format(*platform.python_version_tuple()),
			os.path.join(cwd, "pyinstaller-2.0\pyinstaller.py"),
			"--windowed",
			"--name", self._metadata["name"].lower(),
			"--icon", "icon.ico",
			"starter.py"
		])
		os.chdir(cwd)

		resultPath = os.path.join(path, "dist", self._metadata["name"].lower())

		sourcePath = self._saveSource()
		shutil.copytree(sourcePath, os.path.join(resultPath, "source"))

		return resultPath

	def _cleanup(self):
		for path in self._tempPaths:
			shutil.rmtree(path)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._metadata = self._modules.default("active", type="metadata").metadata
		self.active = True

	def disable(self):
		self.active = False
		del self._modules
		del self._metadata

def init(moduleManager):
	return PyinstallerInterfaceModule(moduleManager)
