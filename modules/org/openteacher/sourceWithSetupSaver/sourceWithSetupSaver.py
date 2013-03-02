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

import sys
import os
import shutil
import datetime
import subprocess
import glob

def check_output(command):
	#FIXME sometime: replace with subprocess.check_output
	process = subprocess.Popen(command, stdout=subprocess.PIPE)
	return process.communicate()[0]

class SourceWithSetupSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SourceWithSetupSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "sourceWithSetupSaver"
		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="sourceSaver"),
			self._mm.mods(type="translator"),
		)
		self.uses = (
			self._mm.mods(type="profileDescription"),
			self._mm.mods(type="authors"),
			self._mm.mods(type="load"),
			self._mm.mods(type="dataTypeIcons"),
		)
		self.filesWithTranslations = ("manpage.templ",)

	def _addSetupAndOtherFiles(self, sourcePath):
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

		mimetypes = []
		imagePaths = {}
		for mod in self._modules.sort("active", type="load"):
			if not hasattr(mod, "mimetype"):
				continue
			for ext in mod.loads.keys():
				mimetypes.append((ext, mod.name, mod.mimetype))
			imagePaths[mod.mimetype] = "linux/" + mod.mimetype.replace("/", "-") + ".png"

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

			mimetypeList = sorted(set((m[2] for m in mimetypes)))
			f.write(templ(package=packageName, mimetypes=";".join(mimetypeList), **self._metadata).encode("UTF-8"))

		#linux/package.menu
		with open(os.path.join(sourcePath, "linux", packageName), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("menu.templ"))
			f.write(templ(package=packageName, **self._metadata).encode("UTF-8"))

		#english man page
		self._buildManPage(sourcePath, packageName, "C")
		#other languages
		translator = self._modules.default("active", type="translator")
		for file in glob.glob(self._mm.resourcePath("translations/*.po")):
			lang = os.path.splitext(os.path.basename(file))[0]
			self._buildManPage(sourcePath, packageName, lang)

		#linux/package.xml
		with open(os.path.join(sourcePath, "linux", packageName + ".xml"), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("mimetypes.xml"))
			f.write(templ(data=mimetypes).encode("UTF-8"))

		#generate png icon
		image = QtGui.QImage(self._metadata["iconPath"])
		image128 = image.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
		image128.save(os.path.join(sourcePath, "linux/openteacher.png"))

		#generate openteacher.xpm
		image32 = image.scaled(32, 32, QtCore.Qt.KeepAspectRatio)
		image32.save(os.path.join(sourcePath, "linux/" + packageName + ".xpm"))

		#generate file icons
		def findSubIcon(type):
			try:
				return QtGui.QImage(self._modules.default("active", type="dataTypeIcons").findIcon(type))
			except (KeyError, IndexError):
				return QtGui.QImage()

		for mimeType, imagePath in imagePaths.iteritems():
			copy = image128.copy()
			if mimeType == "application/x-openteachingwords":
				otherImage = findSubIcon("words")
			elif mimeType == "application/x-openteachingtopography":
				otherImage = findSubIcon("topo")
			elif mimeType == "application/x-openteachingmedia":
				otherImage = findSubIcon("media")
			else:
				#nothing to project over the base icon
				otherImage = QtGui.QImage()
			if not otherImage.isNull():
				otherImage = otherImage.scaled(64, 64, QtCore.Qt.KeepAspectRatio)

			p = QtGui.QPainter(copy)
			p.drawImage(64, 64, otherImage)
			p.end()

			copy.save(os.path.join(sourcePath, imagePath))

		#make a COPYING file in place for the generated files
		with open(os.path.join(sourcePath, "linux/COPYING"), "w") as f:
			f.write("application-x-openteachingwords.png, application-x-openteachingtopo.png and application-x-openteachingmedia.png are based on the files words.png, topo.png and media.png of which the licenses are described elsewhere in this package.\n")

		#gather extensions to compile
		exts = []
		for f in os.listdir(packagePath):
			if f.endswith(".c"):
				exts.append((os.path.splitext(f)[0], f))

		data = self._metadata.copy()
		data.update({
			"package": packageName,
			"package_data": packageData,
			"image_paths": repr(imagePaths.values()),
			"extensions": exts
		})

		#setup.py
		with open(os.path.join(sourcePath, "setup.py"), "w") as f:
			templ = pyratemp.Template(filename=self._mm.resourcePath("setup.py.templ"))
			f.write(templ(**data).encode("UTF-8"))

		return sourcePath

	def saveSourceWithCExtensions(self):
		sourcePath = self._sourceSaver.saveSourceWithCExtensions()
		return self._addSetupAndOtherFiles(sourcePath)

	def saveSource(self):
		sourcePath = self._sourceSaver.saveSource()
		return self._addSetupAndOtherFiles(sourcePath)

	_sourceSaver = property(lambda self: self._modules.default("active", type="sourceSaver"))

	def _buildManPage(self, sourcePath, packageName, lang):
		translator = self._modules.default("active", type="translator")
		#temporarily switch the application language
		oldLanguage = translator.language
		translator.language = lang

		rstPath = os.path.join(sourcePath, "linux", "manpage.rst")
		with open(rstPath, "w") as f:
			_, ngettext = translator.gettextFunctions(self._mm.resourcePath("translations"))

			templ = pyratemp.Template(filename=self._mm.resourcePath("manpage.templ"))
			authors = self._modules.default("active", type="authors").registeredAuthors
			profileMods = self._modules.sort("active", type="profileDescription")
			args = {
				"package": packageName,
				"now": datetime.datetime.now(),
				#someone may appear in multiple categories, so set.
				"otAuthors": set([a[1] for a in authors]),
				"profiles": [m.desc for m in profileMods],
				"tr": _,
				#constructs a valid restructured text title.
				"titleify": lambda title: title + "\n" + (len(title) + 1) * "="
			}
			args.update(self._metadata)
			f.write(templ(**args).encode("UTF-8"))

		if lang == "C":
			manName = packageName + ".1"
		else:
			manName = packageName + "." + lang + ".1"
		subprocess.check_call(["rst2man", rstPath, os.path.join(sourcePath, "linux", manName)])
		os.remove(rstPath)

		#restore the default application language again.
		translator.language = oldLanguage

	def enable(self):
		global pyratemp
		global QtCore, QtGui
		try:
			import pyratemp
			from PyQt4 import QtCore, QtGui
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
