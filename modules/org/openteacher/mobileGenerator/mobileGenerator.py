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

import shutil
import sys
import os
try:
	import simplejson as json
except ImportError:
	import json

class MobileGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MobileGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "mobileGenerator"
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(subType="languageChooser"),
			self._mm.mods("javaScriptImplementation", type="wordsStringParser"),
			self._mm.mods("javaScriptImplementation", type="wordsStringComposer"),
			self._mm.mods("javaScriptImplementation", type="wordsStringChecker"),
			self._mm.mods("javaScriptImplementation", type="wordListStringParser"),
			self._mm.mods("javaScriptImplementation", type="wordListStringComposer"),
		)
		self.priorities = {
			"default": -1,
			"generate-mobile": 0,
		}
		self.filesWithTranslations = ("scr/gui.js",)

	def enable(self):
		global pyratemp
		global polib
		try:
			import pyratemp
			import polib
		except ImportError:
			return #remain disabled
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self._run)

		self.active = True

	@property
	def languages(self, cache={}):
		if "languages" not in cache:
			cache["languages"] = self._modules.default("active", subType="languageChooser").languages
		return cache["languages"]

	def _run(self):
		#get path to save to
		try:
			path = sys.argv[1]
		except IndexError:
			print >> sys.stderr, "Please specify a path to safe the mobile site to as last command line argument."
			return
		#ask if overwrite
		if os.path.isdir(path):
			confirm = raw_input("There is already a directory at '%s'. Do you want to remove it and continue (y/n). " % path)
			if confirm != "y":
				return
			shutil.rmtree(path)

		#copy static resources
		shutil.copytree(self._mm.resourcePath("css"), os.path.join(path, "css"))
		shutil.copytree(self._mm.resourcePath("scr"), os.path.join(path, "scr"))

		#generate translation json files from po files
		translationIndex = {}

		os.mkdir(os.path.join(path, "translations"))
		for poname in os.listdir(self._mm.resourcePath("translations")):
			data = {}
			if not poname.endswith(".po"):
				continue
			popath = os.path.join(self._mm.resourcePath("translations"), poname)
			po = polib.pofile(popath)
			for entry in po.translated_entries():
				data[entry.msgid] = entry.msgstr

			lang = poname[:len(".po") -1].replace("_", "-")
			jsonname = lang + ".json"
			translationIndex[lang] = {
				"url": os.path.join("translations", jsonname),
				#the language code as fallback
				"name": self.languages.get(lang, lang),
			}

			with open(os.path.join(path, "translations", jsonname), "w") as f:
				json.dump(data, f, encoding="UTF-8")

		translationIndex["en"] = {"name": self.languages["C"]}
		with open(os.path.join(path, "translations", "index.js"), "w") as f:
			data = json.dumps(translationIndex, f, encoding="UTF-8")
			f.write("var translationIndex = (%s);" % data)

		#generate logic.js
		logic = ""
		for type in ["wordsStringParser", "wordsStringComposer", "wordsStringChecker", "wordListStringParser", "wordListStringComposer"]:
			mod = self._modules.default("active", "javaScriptImplementation", type=type)
			#add to logic code var with an additional tab before every
			#line
			logic += "\n\n\n\t" + "\n".join(map(lambda s: "\t" + s, mod.code.split("\n"))).strip()
		logic = logic.strip()

		template = pyratemp.Template(filename=self._mm.resourcePath("logic.js.templ"))
		with open(os.path.join(path, "scr", "logic.js"), "w") as f:
			f.write(template(code=logic))

		#generate html
		headerTemplate = pyratemp.Template(filename=self._mm.resourcePath("header.html.templ"))
		footerTemplate = pyratemp.Template(filename=self._mm.resourcePath("footer.html.templ"))

		template = pyratemp.Template(filename=self._mm.resourcePath("index.html.templ"))
		result = template(**{
			"enterTabHeader": headerTemplate(titleHeader="<h1 id='enter-list-header'></h1>"),
			"teachTabHeader": headerTemplate(titleHeader="<h1 id='teach-me-header'></h1>"),
			"enterTabFooter": footerTemplate(tab="enter"),
			"teachTabFooter": footerTemplate(tab="teach"),
		})
		#write html to index.html
		with open(os.path.join(path, "index.html"), "w") as f:
			f.write(result)

	def disable(self):
		self.active = False

		self._modules.default(type="execute").startRunning.unhandle(self._run)
		del self._modules

def init(moduleManager):
	return MobileGeneratorModule(moduleManager)
