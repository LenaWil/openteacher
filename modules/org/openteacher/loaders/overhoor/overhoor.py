#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
#	Copyright 2011-2013, Marten de Vries
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

class OverhoorLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OverhoorLoaderModule, self).__init__(*args, **kwargs)

		self.type = "load"
		self.priorities = {
			"default": 432,
		}
		self._mm = moduleManager
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="wordListStringParser"),
		)
		self.filesWithTranslations = ("overhoor.py",)

	@property
	def _parseList(self):
		return self._modules.default("active", type="wordListStringParser").parseList

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		#TRANSLATORS: This is one of the file formats OpenTeacher
		#TRANSLATORS: can read. It's named after the programs that uses
		#TRANSLATORS: it. See http://www.efkasoft.com/drillassistant-general-information
		#TRANSLATORS: and http://www.efkasoft.com/overhoor-algemene-informatie (dutch)
		#TRANSLATORS: for more info on these programs.
		self.name = _("Overhoor/Drill Assistant")

	def enable(self):
		self.loads = {
			"oh": ["words"],
			"ohw": ["words"],
			"oh4": ["words"],
		}
		self.mimetype = "application/x-overhoor"

		self._modules = set(self._mm.mods(type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def disable(self):
		self.active = False

		del self.name
		del self.loads
		del self.mimetype

		del self._modules

	def getFileTypeOf(self, path):
		if path.endswith(".oh") or path.endswith(".ohw") or path.endswith(".oh4"):
			return "words"

	def load(self, path):
		#encoding
		if path.endswith(".oh4"):
			encoding = "iso-8859-1"
		else:
			encoding= "cp850"
		#read file
		with open(path, "r") as f:
			data = unicode(f.read(), encoding=encoding)
		if data.startswith(u"[FONT"):
			data = data.split("\n", 1)[1]

		#parse file
		list = self._parseList(data)
		return list

def init(moduleManager):
	return OverhoorLoaderModule(moduleManager)
