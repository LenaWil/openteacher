#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012-2014, Marten de Vries
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

import shutil
import sys
import os
import json
import urllib2
import urllib
import datetime
import posixpath

class MobileGeneratorModule(object):
	"""Generates the HTML of OpenTeacher Mobile as a command line
	   profile. Includes an option to compress the JavaScript and CSS
	   via web services. (So in that case, a network connection is
	   required.)

	"""
	def __init__(self, moduleManager, *args, **kwargs):
		super(MobileGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "mobileGenerator"

		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="metadata"),
			self._mm.mods(type="webLogicGenerator"),
			self._mm.mods(type="translationIndexBuilder"),
			self._mm.mods(type="translationIndexesMerger"),
			self._mm.mods(type="translationIndexJSONWriter"),
		)

		self.priorities = {
			"default": -1,
			"generate-mobile": 0,
		}
		self.filesWithTranslations = (
			"scr/copyrightInfoDialog.js",
			"scr/enterTab.js",
			"scr/gui.js",
			"scr/menuDialog.js",
			"scr/optionsDialog.js",
			"scr/practisingModeChoiceDialog.js",
			"scr/teachTab.js",
		)
		self.devMod = True

	def enable(self):
		global QtCore, QtGui
		global pyratemp
		global polib
		try:
			import pyratemp
			import polib
			from PyQt4 import QtCore, QtGui
		except ImportError:
			sys.stderr.write("For this developer profile to work, you need pyratemp, polib and PyQt4 (QtCore & QtGui) to be installed.\n")
			return #remain disabled
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self._run)

		self._metadata = self._modules.default("active", type="metadata").metadata
		self._logicGenerator = self._modules.default("active", type="webLogicGenerator")

		self.active = True

	def _buildSplash(self, width, height, iconPath):
		#build splash.png
		image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
		painter = QtGui.QPainter(image)

		#it currently is 128x128, but this way a new future icon render/
		#new icon won't mess up this code.
		icon = QtGui.QImage(iconPath).scaled(128, 128)
		painter.setBrush(QtGui.QColor(209, 233, 250))
		painter.drawRect(0, 0, image.width(), image.height())

		#horizontally centered, vertically at 1/4
		painter.drawImage(QtCore.QPointF(
			(image.width() - icon.width()) / 2.0,
			image.height() / 4.0,
		), icon)

		#text, at 2/3
		painter.setFont(QtGui.QFont("Ubuntu", 32))
		painter.drawText(QtCore.QRectF(
			0,
			image.height() / 3.0 * 2.0, image.width(),
			image.height() / 3.0
		), QtCore.Qt.AlignHCenter, self._metadata["name"])

		painter.end()
		return image

	def _getSavePath(self):
		#get path to save to
		try:
			path = sys.argv[1]
		except IndexError:
			print >> sys.stderr, "Please specify a path to save the mobile site to as last command line argument. (e.g. -p generate-mobile mobile-debug)"
			return
		#ask if overwrite
		if os.path.isdir(path):
			confirm = raw_input("There is already a directory at '%s'. Do you want to remove it and continue (y/n). " % path)
			if confirm != "y":
				return
			shutil.rmtree(path)
		return path

	def _copyCss(self, path):
		#copy css
		shutil.copytree(self._mm.resourcePath("css"), os.path.join(path, "css"))

	def _generateAppCacheManifest(self, path):
		#create the AppCache manifest file
		template = pyratemp.Template(filename=self._mm.resourcePath("otmobile.templ.appcache"))
		allFiles = sorted(
			posixpath.relpath(posixpath.join(root, file), path)
			for root, dirs, files in os.walk(path)
			for file in files
			if not file in [".htaccess", "config.xml", "splash.png"]
		)
		manifest = template(**{
			"now": datetime.datetime.now(),
			"files": allFiles,
		})
		with open(os.path.join(path, "otmobile.appcache"), "w") as f:
			f.write(manifest.encode("UTF-8"))
		shutil.copy(self._mm.resourcePath("htaccess"), os.path.join(path, ".htaccess"))

	def _generateTranslationFiles(self, path):
		buildIndex = self._modules.default("active", type="translationIndexBuilder").buildTranslationIndex
		mergeIndexes = self._modules.default("active", type="translationIndexesMerger").mergeIndexes
		writeJSONIndex = self._modules.default("active", type="translationIndexJSONWriter").writeJSONIndex

		index = buildIndex(self._mm.resourcePath("translations"))
		masterIndex = mergeIndexes(index, self._logicGenerator.translationIndex)
		writeJSONIndex(masterIndex, os.path.join(path, "translations"), "translations")

	def _writeScripts(self, path):
		os.mkdir(os.path.join(path, "scr"))

		logicPath = os.path.join(path, "scr", "logic.js")
		self._logicGenerator.writeLogicCode(logicPath)

		#copy scripts
		scripts = [
			#libs
			"jquery-1.8.2.js",
			"jquery.mobile-1.2.0.js",
			"taboverride.js",
			"jquery.taboverride.js",
			"jsdiff.js",
			#helper files
			"menuDialog.js",
			"copyrightInfoDialog.js",
			"optionsDialog.js",
			"enterTab.js",
			"teachTab.js",
			"practisingModeChoiceDialog.js",
			#main file
			"gui.js",
		]

		#copy scripts
		for script in scripts:
			shutil.copy(
				os.path.join(self._mm.resourcePath("scr"), script),
				os.path.join(path, "scr", script)
			)
		scripts.insert(0, "logic.js")
		return scripts

	def _writeHtml(self, path, scriptNames):
		#generate html
		headerTemplate = pyratemp.Template(filename=self._mm.resourcePath("header.html.templ"))

		template = pyratemp.Template(filename=self._mm.resourcePath("index.html.templ"))
		result = template(**{
			"scripts": scriptNames,
			"enterTabHeader": headerTemplate(titleHeader="<h1 id='enter-list-header'></h1>", tab="enter"),
			"teachTabHeader": headerTemplate(titleHeader="<h1 id='teach-me-header'></h1>", tab="teach"),
		})
		#write html to index.html
		with open(os.path.join(path, "index.html"), "w") as f:
			f.write(result)

	def _copyPhonegapConfig(self, path):
		#copy config.xml (phonegap config)
		shutil.copy(
			self._mm.resourcePath("config.xml"),
			os.path.join(path, "config.xml")
		)

	def _copyCopying(self, path):
		#copy COPYING
		shutil.copy(
			self._mm.resourcePath("COPYING.txt"),
			os.path.join(path, "COPYING.txt")
		)

	def _copyIcon(self, iconPath, path):
		#copy icon.png
		shutil.copy(
			iconPath,
			os.path.join(path, "icon.png")
		)

	def _writeSplash(self, iconPath, path):
		#splash screen
		self._buildSplash(320, 480, iconPath).save(
			os.path.join(path, "splash.png")
		)

	def _run(self):
		path = self._getSavePath()
		if not path:
			return

		self._copyCss(path)
		self._generateTranslationFiles(path)
		scriptNames = self._writeScripts(path)
		self._writeHtml(path, scriptNames)

		self._copyPhonegapConfig(path)
		self._copyCopying(path)

		#graphics
		iconPath = self._metadata["iconPath"]
		self._copyIcon(iconPath, path)
		self._writeSplash(iconPath, path)

		self._generateAppCacheManifest(path)

		print "Writing %s mobile to '%s' is now done." % (self._metadata["name"], path)

	def disable(self):
		self.active = False

		del self._metadata
		del self._logicGenerator
		self._modules.default(type="execute").startRunning.unhandle(self._run)
		del self._modules

def init(moduleManager):
	return MobileGeneratorModule(moduleManager)
