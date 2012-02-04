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

import webbrowser
import cherrypy
import inspect
import os
import types
import mimetypes

class ResourcesHandler(object):
	def __init__(self, templates, *args, **kwargs):
		super(ResourcesHandler, self).__init__(*args, **kwargs)

		self._templates = templates

	@cherrypy.expose
	def style_css(self):
		cherrypy.response.headers['Content-Type']= 'text/css'
		return open(self._templates["style"]).read()

	@cherrypy.expose
	def logo(self):
		mimetype = mimetypes.guess_type(self._templates["logo"], strict=False)[0]
		cherrypy.response.headers['Content-Type'] = mimetype
		return open(self._templates["logo"]).read()

	@cherrypy.expose
	def jquery_js(self):
		cherrypy.response.headers['Content-Type'] = 'text/javascript'
		return open(self._templates["jquery"]).read()

	@cherrypy.expose
	def jquery_quicksearch_js(self):
		cherrypy.response.headers['Content-Type'] = 'text/javascript'
		return open(self._templates["jquery_quicksearch"]).read()

class ModulesHandler(object):
	def __init__(self, mods, templates, *args, **kwargs):
		super(ModulesHandler, self).__init__(*args, **kwargs)

		self._mods = {}
		for mod in mods:
			id = os.path.split(mod.__class__.__file__)[0]
			self._mods[id] = mod
		self._templates = templates

	def _emptyMethod(self):
		pass

	def _newlineToBr(self, text):
		if text:
			return text.replace("\n", "<br />\n")
		else:
			return text

	@cherrypy.expose
	def index(self):
		t = pyratemp.Template(filename=self._templates["modules"])
		return t(**{
			"mods": sorted(self._mods.keys())
		})

	def _isFunction(self, mod, x):
		try:
			obj = getattr(mod.__class__, x)
		except AttributeError:
			obj = getattr(mod, x)
		return isinstance(obj, types.MethodType)

	def _modsForRequirement(self, selectors):
		requirements = []
		for selector in selectors:
			selectorResults = set()
			requiredMods = set(selector)
			for requiredMod in requiredMods:
				selectorResults.add((
					os.path.split(requiredMod.__class__.__file__)[0],
					requiredMod.__class__.__name__
				))
		requirements.append(selectorResults)
		return requirements

	@cherrypy.expose
	def modules(self, *args):
		args = list(args)
		args[-1] = args[-1][:-len(".html")]
		mod = self._mods["modules/" + "/".join(args)]

		attrs = dir(mod)
		methods = filter(lambda x: self._isFunction(mod, x), attrs)
		properties = set(attrs) - set(methods)

		checkPublic = lambda x: not x.startswith("_")
		methods = filter(checkPublic, methods)
		properties = filter(checkPublic, properties)

		#remove special properties
		properties = set(properties) - set(["type", "uses", "requires"])

		#uses
		try:
			uses = self._modsForRequirement(mod.uses)
		except AttributeError:
			uses = set()

		#requires
		try:
			requires = self._modsForRequirement(mod.requires)
		except AttributeError:
			requires = set()

		methodDocs = {}
		methodArgs = {}
		for method in methods:
			methodObj = getattr(mod, method)
			methodDocs[method] = self._newlineToBr(methodObj.__doc__)
			methodArgs[method] = inspect.getargspec(methodObj)[0]

		t = pyratemp.Template(filename=self._templates["module"])
		return t(**{
			"name": mod.__class__.__name__,
			"moddoc": self._newlineToBr(mod.__doc__),
			"type": getattr(mod, "type", None),
			"uses": uses,
			"requires": requires,
			"methods": sorted(methods),
			"methodDocs": methodDocs,
			"methodArgs": methodArgs,
			"properties": sorted(properties),
		})

class CodeDocumentationModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(CodeDocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "codeDocumentationShower"

		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="execute"),
		)

	def showDocumentation(self):
		mods = self._modules.sort()
		templates = {
			"modules": self._mm.resourcePath("templ/modules.html"),
			"module": self._mm.resourcePath("templ/module.html"),
			"style": self._mm.resourcePath("templ/style.css"),
			"logo": self._modules.default("active", type="metadata").metadata["iconPath"],
			"jquery": self._mm.resourcePath("templ/jquery.js"),
			"jquery_quicksearch": self._mm.resourcePath("templ/jquery.quicksearch.js")
		}
		root = ModulesHandler(mods, templates)
		root.resources = ResourcesHandler(templates)

		cherrypy.tree.mount(root)
		cherrypy.engine.start()
		webbrowser.open("http://localhost:8080/")
		cherrypy.engine.block()

	def enable(self):
		global pyratemp
		pyratemp = self._mm.import_("pyratemp")
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self._modules.default(type="execute").startRunning.handle(self.showDocumentation)

		self.active = True

	def disable(self):
		self.active = False

		global pyratemp
		del pyratemp
		del self._modules

def init(moduleManager):
	return CodeDocumentationModule(moduleManager)
