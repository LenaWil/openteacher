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

import webbrowser
import cherrypy
import inspect

class ModulesHandler(object):
	def __init__(self, mods, templates, *args, **kwargs):
		super(ModulesHandler, self).__init__(*args, **kwargs)

		self._mods = mods
		self._templates = templates

	@cherrypy.expose
	def index(self):
		t = pyratemp.Template(filename=self._templates["modules"])
		mods = sorted(mod.__class__.__module__ for mod in self._mods)
		return t(**{
			"mods": mods
		})

	@cherrypy.expose
	def default(self, module):
		return module

class CodeDocumentationModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(CodeDocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "codeDocumentationShower"

	def showDocumentation(self):
		#FIXME: this relies on the slowness of this method :P
		webbrowser.open("http://localhost:8080/")

		mods = self._modules.sort()
		templates = {
			"modules": self._mm.resourcePath("modules.html")
		}
		cherrypy.quickstart(ModulesHandler(mods, templates))

	def enable(self):
		global pyratemp
		pyratemp = self._mm.import_("pyratemp")
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.showDocumentation()

		self.active = True

	def disable(self):
		self.active = False

		global pyratemp
		del pyratemp
		del self._modules

def init(moduleManager):
	return CodeDocumentationModule(moduleManager)
