#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

class MetadataModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MetadataModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "metadata"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("metadata.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

	def _retranslate(self):
		#Translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.metadata = {
			#TRANSLATORS: OpenTeacher is a name, so please only
			#translate or transliterate it if you've got a good reason
			#to do so.
			"name": _("OpenTeacher"),
			"slogan": _("The easiest way to learn a new language"),
			"version": _("3.0"),
			"authors": _("OpenTeacher authors"),
			"copyrightYears": _("2008-2012"),
			#TRANSLATORS: If you want to change this to another, e.g.
			#localized website, please contact us
			#(openteachermaintainers@lists.launchpad.net) first.
			"website": _("http://openteacher.org/"),
			"email": "openteachermaintainers@lists.launchpad.net",
			#TRANSLATORS: If you want to change this to another, e.g.
			#localized website, please contact us
			#(openteachermaintainers@lists.launchpad.net) first.
			"documentationUrl": _("http://openteacher.org/documentation.html"),
			"updatesUrl": "http://openteacher.org/updates/updates.json",
			"updatesSignatureUrl": "http://openteacher.org/updates/updates.json.asc",
			"iconPath": self._mm.resourcePath("openteacher.png"),
			"licenseIntro": open(self._mm.resourcePath("license_intro.txt")).read(),
			"license": open(self._mm.resourcePath("license.txt")).read(),
			"comicPath": self._mm.resourcePath("comic.png"),
		}
		self.metadata["userAgent"] = "%s/%s (+%s)" % (
			self.metadata["name"],
			self.metadata["version"],
			self.metadata["website"]
		)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.metadata

def init(moduleManager):
	return MetadataModule(moduleManager)

