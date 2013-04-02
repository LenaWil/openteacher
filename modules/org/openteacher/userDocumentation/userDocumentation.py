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

class UserDocumentationModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UserDocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "userDocumentation"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("getting-started.html",)

	def getHtml(self, resourceUrl):
		"""Returns the user documentation as an html snippet. All links
		   to resources (e.g. images) will be pointing to
		   ``resourceUrl``/resourceName. In other words, the caller
		   should make sure all files in ``self.resourcesPath`` are
		   available on the ``resourceUrl`` in some way.

		"""
		t = pyratemp.Template(filename=self._mm.resourcePath("getting-started.html"))
		return t(**{
			"resourceUrl": resourceUrl,
			"tr": _,
		})

	def enable(self):
		global pyratemp
		try:
			import pyratemp
		except ImportError:
			#remain inactive
			return
		self._modules = next(iter(self._mm.mods(type="modules")))
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.resourcesPath = self._mm.resourcePath("static")
		self.active = True

	def _retranslate(self):
		global _, ngettext
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

	def disable(self):
		self.active = False

		del self._modules
		del self.resourcesPath

def init(moduleManager):
	return UserDocumentationModule(moduleManager)
