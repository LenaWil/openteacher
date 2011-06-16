#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

		self.supports = (
			"metadata",
			"name",
			"slogan",
			"version",
			"website",
			"userAgent",
			"documentationUrl",
			"iconPath",
			"licenseIntro",
			"license",
			"comicPath"
		)
		self.requires = (1, 0)
		self.active = False

	def enable(self):
		self.name = "OpenTeacher" #FIXME: translate
		self.slogan = "OpenTeacher helps you learn a foreign language vocabulary." #FIXME: translate
		self.version = "3.x"
		self.website = "http://openteacher.org/"
		self.userAgent = "%s/%s (+%s)" % (self.name, self.version, self.website)
		self.documentationUrl = "http://openteacher.org/documentation.html"
		self.iconPath = self._mm.resourcePath("openteacher.png")
		self.licenseIntro = open(self._mm.resourcePath("license_intro.txt")).read()
		self.license = open(self._mm.resourcePath("license.txt")).read()
		self.comicPath = self._mm.resourcePath("comic.png")

		self.active = True

	def disable(self):
		self.active = False

		del self.name
		del self.slogan
		del self.version
		del self.website
		del self.documentationUrl
		del self.iconPath
		del self.licenseIntro
		del self.license
		del self.comicPath

def init(moduleManager):
	return MetadataModule(moduleManager)
