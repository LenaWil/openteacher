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
import subprocess
import os
import shutil
import glob
import platform
from PyQt4 import QtGui

class RpmPackagerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(RpmPackagerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "rpmPackager"
		self.requires = (
			self._mm.mods(type="sourceWithSetupSaver"),
			self._mm.mods(type="metadata"),
			self._mm.mods(type="execute"),
		)
		self.priorities = {
			"package-rpm": 0,
			"default": -1,
		}

	def enable(self):
		if not platform.linux_distribution()[0].strip() in ("Fedora", "openSUSE"):
			return #rpm based distro only module, remain inactive
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._metadata= self._modules.default("active", type="metadata").metadata
		self._modules.default(type="execute").startRunning.handle(self._run)

		self._platform = platform.linux_distribution()[0].strip()

		self.active = True

	def _run(self):
		try:
			release = sys.argv[1]
			path = sys.argv[2]
		except IndexError:
			sys.stderr.write("Please specify a .rpm release number and a path for the rpm file (ending in .rpm) as the last command line arguments.\n")
			return
		sourcePath = self._modules.default("active", type="sourceWithSetupSaver").saveSource()

		#set install prefix to /usr
		with open(os.path.join(sourcePath, "setup.cfg"), "w") as f:
			f.write("[install]\nprefix = /usr")

		#determine requirements based on distribution
		if self._platform == "Fedora":
			requirements = "PyQt4, espeak, rpm-build, python-cherrypy, gettext"
		elif self._platform == "openSUSE":
			requirements = "python-qt4, espeak, python-cherrypy, gettext"

		oldCwd = os.getcwd()
		os.chdir(sourcePath)
		subprocess.check_call([
			sys.executable or "python",
			"setup.py",
			"bdist_rpm",
			"--group", "Applications/Productivity",
			"--packager", "%s <%s>" % (self._metadata["authors"], self._metadata["email"]),
			"--release", release,
			#temporarily not needed: python-django, python-django-guardian
			#add if packaged somewhere in the future: python-graphviz
			"--requires", requirements,
		])
		os.chdir(oldCwd)
		shutil.copy(
			glob.glob(os.path.join(sourcePath, "dist/*.noarch.rpm"))[0],
			path
		)
		print "Please keep in mind that an rpm built on one distro, might not work on another."

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return RpmPackagerModule(moduleManager)