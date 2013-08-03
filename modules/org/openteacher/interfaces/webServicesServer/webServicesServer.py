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

import contextlib
import json

class WebServicesServerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebServicesServerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "webServicesServer"
		self.requires = (
			self._mm.mods("javaScriptImplementation", type="safeHtmlChecker"),
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("serverImpl.py", "register-template.html")

	def enable(self):
		try:
			self._server = self._mm.import_("serverImpl")
			self._server.otCouch = self._mm.import_("otCouch")
		except ImportError:
			return

		self.app = self._server.app
		with contextlib.ignored(IOError):
			with open(self._mm.resourcePath("ot-web-config.json")) as f:
				self.app.config.update(json.load(f))

		self.app.config["REGISTER_TEMPLATE_PATH"] = self._mm.resourcePath("register-template.html")

		modules = next(iter(self._mm.mods(type="modules")))
		self.app.config["IS_SAFE_HTML_JS"] = modules.default("javaScriptImplementation", type="safeHtmlChecker").code
		self.app.config["TRANSLATIONS_DIR"] = self._mm.resourcePath("translations")

		def gettextFunctions(language):
			translator = modules.default("active", type="translator")
			translationDir = self._mm.resourcePath("translations")
			return translator.gettextFunctions(translationDir, language)
		self._server.gettextFunctions = gettextFunctions

		self.active = True

	def disable(self):
		self.active = False

		del self.app
		del self._server

def init(moduleManager):
	return WebServicesServerModule(moduleManager)
