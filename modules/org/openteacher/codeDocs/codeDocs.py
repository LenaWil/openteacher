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
import sys

class ModulesHandler(object):
	def __init__(self, moduleManager, templates, *args, **kwargs):
		super(ModulesHandler, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._mods = {}
		for mod in self._mm.mods:
			#get the path of the module
			id = os.path.dirname(mod.__class__.__file__)
			#make sure the path is relative to the modules root for easier recognition
			common = os.path.commonprefix([sys.argv[0], id])
			id = id[len(common):]
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
	def resources(self, *args):
		path = "/".join(args)
		if path == "logo":
			path = self._templates["logo"]
		else:
			#construct the path
			path = os.path.normpath(
				os.path.join(self._templates["resources"], path)
			)
			#check if the path is valid (i.e. is in the resources
			#directory.)
			if not path.startswith(self._templates["resources"]):
				#404
				raise cherrypy.HTTPError(404)
		mimetype = mimetypes.guess_type(path, strict=False)[0]
		if mimetype:
			cherrypy.response.headers["Content-Type"] = mimetype
		try:
			return open(path).read()
		except IOError:
			#404
			raise cherrypy.HTTPError(404)

	@cherrypy.expose
	def index(self):
		t = pyratemp.Template(filename=self._templates["modules"])
		return t(**{
			"mods": sorted(self._mods.keys())
		})

	@cherrypy.expose
	def priorities_html(self):
		profiles = self._mm.mods("active", type="profileDescription")
		profiles = sorted(profiles, key=lambda p: p.desc["name"])

		mods = {}
		for mod in self._mm.mods("priorities"):
			mods[mod.__class__.__file__] = mod
		mods = sorted(mods.iteritems())

		t = pyratemp.Template(filename=self._templates["priorities"])
		return t(**{
			"mods": mods,
			"profiles": profiles,
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
		self.uses = (
			self._mm.mods(type="profileDescription"),
		)
		self.priorities = {
			"student@home": -1,
			"student@school": -1,
			"teacher": -1,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": -1,
			"codedocumentation": 0,
			"all": -1,
			"update-translations": -1,
			"testserver": -1,
		}

	def showDocumentation(self):
		templates = {
			"modules": self._mm.resourcePath("templ/modules.html"),
			"priorities": self._mm.resourcePath("templ/priorities.html"),
			"module": self._mm.resourcePath("templ/module.html"),
			"resources": self._mm.resourcePath("resources"),
			"logo": self._modules.default("active", type="metadata").metadata["iconPath"],
		}
		root = ModulesHandler(self._mm, templates)

		cherrypy.tree.mount(root)
		cherrypy.config.update({
			"environment": "production",
		})
		cherrypy.engine.start()
		webbrowser.open("http://localhost:8080/")
		print "Serving at http://localhost:8080/"
		print "Type 'quit' and press enter to stop the server"
		while True:
			try:
				if raw_input("> ") in ("q", "Q", "quit", "Quit"):
					break
			except KeyboardInterrupt:
				break
		cherrypy.engine.exit()

	def enable(self):
		global pyratemp
		pyratemp = self._mm.import_("pyratemp")
		self._modules = set(self._mm.mods(type="modules")).pop()

		self._modules.default(type="execute").startRunning.handle(self.showDocumentation)

		self.active = True

	def disable(self):
		self.active = False

		global pyratemp
		del pyratemp
		del self._modules

def init(moduleManager):
	return CodeDocumentationModule(moduleManager)
