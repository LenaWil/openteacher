#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

class WebGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "webGenerator"
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="webLogicGenerator"),
			self._mm.mods(type="jsLib", name="tmpl"),
			self._mm.mods(type="translationIndexBuilder"),
			self._mm.mods(type="translationIndexesMerger"),
			self._mm.mods(type="translationIndexJSONWriter"),
			self._mm.mods(type="metadata"),
		)
		self.priorities = {
			"default": -1,
			"generate-web": 0,
		}
		#all files directly in the scr directory are web-specific and
		#thus ui related and thus contain translations. (In theory ;))
		self.filesWithTranslations = (
			"static/scr/learn-list.js",
			"static/scr/lists-overview.js",
			"static/scr/login.js",
			"static/scr/main.js",
			"static/scr/view-list.js",
		)
		self.devMod = True

	def enable(self):
		global pyratemp
		global QtGui
		try:
			import pyratemp
			from PyQt4 import QtGui
		except ImportError:
			return
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self._run)
		self._logicGenerator = self._modules.default("active", type="webLogicGenerator")

		self._metadata = self._modules.default("active", type="metadata").metadata

		self.active = True

	def _run(self):
		#get path to save to
		try:
			path = sys.argv[1]
			couchdbHost = sys.argv[2]
			servicesHost = sys.argv[3]
		except IndexError:
			print >> sys.stderr, "Please specify a path to save the site to, the couchdb hostname and the services server hostname as last command line arguments. (e.g. -p generate-web web-debug http://localhost:5984 http://localhost:5000)"
			return
		#ask if overwrite
		if os.path.isdir(path):
			confirm = raw_input("There is already a directory at '%s'. Do you want to remove it and continue (y/n). " % path)
			if confirm != "y":
				return
			shutil.rmtree(path)

		#copy all static stuff
		shutil.copytree(self._mm.resourcePath("static"), path)

		#copy global libraries
		with open(os.path.join(path, "scr/library/tmpl.js"), "w") as f:
			f.write(self._modules.default(type="jsLib", name="tmpl").code)

		#create the config file
		template = pyratemp.Template(filename=self._mm.resourcePath("config.templ.js"))
		with open(os.path.join(path, "scr/generated/config.js"), "w") as f:
			f.write(template(
				couchdbHost=couchdbHost,
				servicesHost=servicesHost,
				appName=self._metadata
			).encode("UTF-8"))

		#create the style file
		template = pyratemp.Template(filename=self._mm.resourcePath("style.templ.css"))
		hue = self._metadata["mainColorHue"]
		data = {
			"headerBgColor": QtGui.QColor.fromHsv(hue, 41, 250).name(),
			"footerBgColor": QtGui.QColor.fromHsv(hue, 30, 228).name(),
		}
		with open(os.path.join(path, "css/style.css"), "w") as f:
			f.write(template(**data).encode("UTF-8"))

		#create the logic file
		logicPath = os.path.join(path, "scr/generated/logic.js")
		self._logicGenerator.writeLogicCode(logicPath)

		#write the translation index
		buildIndex = self._modules.default("active", type="translationIndexBuilder").buildTranslationIndex
		mergeIndexes = self._modules.default("active", type="translationIndexesMerger").mergeIndexes
		writeJSONIndex = self._modules.default("active", type="translationIndexJSONWriter").writeJSONIndex

		index = buildIndex(self._mm.resourcePath("translations"))
		masterIndex = mergeIndexes(index, self._logicGenerator.translationIndex)
		url = "scr/generated/translations"
		writeJSONIndex(masterIndex, os.path.join(path, url), url)

		#copy the logo
		shutil.copy(self._metadata["iconPath"], os.path.join(path, "img/logo"))

		print "Writing OpenTeacher web to '%s' is now done." % path

	def disable(self):
		self.active = False

		self._modules.default(type="execute").startRunning.unhandle(self._run)
		del self._logicGenerator
		del self._modules
		del self._metadata

def init(moduleManager):
	return WebGeneratorModule(moduleManager)
