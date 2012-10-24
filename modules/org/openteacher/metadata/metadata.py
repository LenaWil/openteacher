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
		#FIXME 3.1: move some colors in here for codeDocs and
		#moduleGraph. (The blue OT website colors.)
		self.metadata = {
			#TRANSLATORS: OpenTeacher is a name, so please only
			#translate or transliterate it if you've got a good reason
			#to do so.
			"name": _("OpenTeacher"),
			"version": _("3.1"),
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
			#Not translated because this is for the packaging only,
			#packages are normally translated in other ways.
			"short_description": "Your personal tutor",
			"description": """OpenTeacher is an opensource application that helps you learning a variety
of subjects. You just enter the questions and the answers, or download them from
the internet, and OpenTeacher tests you.

OpenTeacher 3.1 has the following features:
 * Viewing both recent and past results of tests with graphs
 * Smart question asking and interval training
 * Reverse rehearsal (the answer is asked, and you need to give the question)
 * Read and write Teach2000, WRDS and OpenTeacher 2.x files and read ABBYY
   Lingvo Tutor files
 * Save and open your online WRDS vocabulary lists
 * Print your word lists or topography maps
 * (Partly) available in Arabic, Brazilian Portuguese, Simplified Chinese,
   Traditional Chinese, Czech, Dutch, Finnish, French, Frisian, German, Greek,
   Japanese and Spanish

OpenTeacher is available for Linux, Windows and Mac OS X."""
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

