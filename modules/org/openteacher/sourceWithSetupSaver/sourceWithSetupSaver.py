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
import shutil

from PyQt4 import QtCore, QtGui

class SourceWithSetupSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SourceWithSetupSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "sourceWithSetupSaver"
		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="sourceSaver"),
		)

	def saveSource(self):
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

		imagePaths = [
			"linux/application-x-%s.png" % packageName,
			"linux/application-x-teach2000.png",
			"linux/application-x-wrts.png",
			"linux/application-x-openteachingwords.png",
			"linux/application-x-openteachingtopography.png",
			"linux/application-x-openteachingmedia.png",
		]

		data = self._metadata.copy()
		data.update({
			"package": packageName,
			"package_data": packageData,
			"image_paths": repr(imagePaths)
		})

		#bin/package
		os.mkdir(os.path.join(sourcePath, "bin"))
		with open(os.path.join(sourcePath, "bin", packageName), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("runner.templ"))
			#ascii since the file doesn't have a encoding directive
			f.write(templ(name=packageName).encode("ascii"))

		#linux/package.desktop
		os.mkdir(os.path.join(sourcePath, "linux"))
		with open(os.path.join(sourcePath, "linux", packageName + ".desktop"), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("desktop.templ"))
			f.write(templ(package=packageName, **self._metadata).encode("UTF-8"))

		#linux/package.menu
		with open(os.path.join(sourcePath, "linux", packageName), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("menu.templ"))
			f.write(templ(package=packageName, **self._metadata).encode("UTF-8"))

		with open(os.path.join(sourcePath, "linux", packageName + ".1"), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("manpage.templ"))
			f.write(templ(package=packageName, **self._metadata).encode("UTF-8"))

		#linux/package.xml
		shutil.copy(
			self._mm.resourcePath("mimetypes.xml"),
			os.path.join(sourcePath, "linux", packageName + ".xml")
		)

		#generate png icons
		image = QtGui.QImage(self._metadata["iconPath"])
		image128 = image.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
		for path in ["linux/openteacher.png"] + imagePaths:
			image128.save(os.path.join(sourcePath, path))

		#generate openteacher.xpm
		image32 = image.scaled(32, 32, QtCore.Qt.KeepAspectRatio)
		image32.save(os.path.join(sourcePath, "linux/" + packageName + ".xpm"))

		#setup.py
		with open(os.path.join(sourcePath, "setup.py"), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("setup.py.templ"))
			f.write(templ(**data).encode("UTF-8"))

		return sourcePath

	def enable(self):
		global pyratemp
		try:
			import pyratemp
		except ImportError:
			return #fail silently: stay inactive
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._metadata = self._modules.default("active", type="metadata").metadata

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._metadata

def init(moduleManager):
	return SourceWithSetupSaverModule(moduleManager)
