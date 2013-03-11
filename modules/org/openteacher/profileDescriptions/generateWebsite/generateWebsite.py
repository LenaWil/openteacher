#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Milan Boers
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

import os

class ProfileDescriptionModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ProfileDescriptionModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "profileDescription"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("generateWebsite.py",)

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.desc = {
			"name": "generate-website",
			"niceName": _("Generates OpenTeacher's website."),
			"advanced": True,
		}

	def enable(self):
		if len(set(self._mm.mods(type="websiteGenerator"))) == 0: # pragma: no cover
			return #remain inactive
		try:
			import pyratemp
		except ImportError:
			return #remain inactive
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
		del self._modules
		del self.desc

def init(moduleManager):
	return ProfileDescriptionModule(moduleManager)
