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

class OpenTeacherAuthorsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherAuthorsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "openteacherAuthors"
		self.uses = (
			self._mm.mods(type="authors"),
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("openteacherAuthors.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		self._authors = self._modules.default("active", type="authors")
		self._removers = set()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

	def _retranslate(self):
		#setup translation
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		a = self._authors
		r = self._removers

		for remove in self._removers.copy():
			#remove all authors with the wrong translated roles
			remove()
			self._removers.remove(remove)

		#Add all the contributors. With their newly translated role

		#Core development team
		r.add(a.registerAuthor(_("Core developer"), u"Milan Boers"))
		r.add(a.registerAuthor(_("Core developer"), u"Cas Widdershoven"))
		r.add(a.registerAuthor(_("Core developer"), u"Marten de Vries"))

		#Patches
		r.add(a.registerAuthor(_("Patches contributor"), u"Roel Huybrechts"))
		r.add(a.registerAuthor(_("Patches contributor"), u"David D Lowe"))

		#Packaging
		r.add(a.registerAuthor(_("Debian/Ubuntu packager"), u"Charlie Smotherman"))

		#Artwork
		r.add(a.registerAuthor(_("Artwork"), u"Yordi de Graaf"))

		#IRC channel spammers
		r.add(a.registerAuthor(_("Chat channel spammer"), u"Stefan de Vries"))

		#Translators
		r.add(a.registerAuthor(_("Translator (%s)") % "Arabic", u"Aminos Amigos"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Arabic", u"El Achèche ANIS"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Arabic", u"REKIK Iskander"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Arabic", u"Slim Khan"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Chinese (Traditional)", u"Louie Chen"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Creek", u"Macedon"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Dutch", u"Guus"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Dutch", u"Marten de Vries"))
		r.add(a.registerAuthor(_("Translator (%s)") % "English (Australia)", u"Joel Pickett"))
		r.add(a.registerAuthor(_("Translator (%s)") % "French", u"EmmanuelLeNormand"))
		r.add(a.registerAuthor(_("Translator (%s)") % "French", u"Glyca"))
		r.add(a.registerAuthor(_("Translator (%s)") % "French", u"Messer Kevin"))
		r.add(a.registerAuthor(_("Translator (%s)") % "French", u"SarahSlean"))
		r.add(a.registerAuthor(_("Translator (%s)") % "French", u"c3d"))
		r.add(a.registerAuthor(_("Translator (%s)") % "French", u"demonipuch"))
		r.add(a.registerAuthor(_("Translator (%s)") % "German", u"Alexander Haack"))
		r.add(a.registerAuthor(_("Translator (%s)") % "German", u"Daniel Winzen"))
		r.add(a.registerAuthor(_("Translator (%s)") % "German", u"Dennis Baudys"))
		r.add(a.registerAuthor(_("Translator (%s)") % "German", u"Sascha Biermanns"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Greek", u"Yannis Kaskamanidis"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Hungarian", u"Richard Somlói"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Slovak", u"Alexander Suchan"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Spanish", u"Fitoschido"))
		r.add(a.registerAuthor(_("Translator (%s)") % "Spanish", u"Javier Blanco"))

		self.active = True

	def disable(self):
		self.active = False

		del self._authors
		del self._removers

def init(moduleManager):
	return OpenTeacherAuthorsModule(moduleManager)
