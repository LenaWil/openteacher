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

# cherrypy, pygments & pyratemp are imported in enable()

import webbrowser
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
			path = os.path.dirname(mod.__class__.__file__)
			#make sure the path is relative to the modules root for easier recognition
			self._mods[self._pathToUrl(path)] = mod
		self._templates = templates

	def _pathToUrl(self, path):
		path = os.path.normpath(path)

		sourceBase = os.path.dirname(__file__)
		while not sourceBase.endswith("modules"):
			sourceBase = os.path.normpath(os.path.join(sourceBase, ".."))
		sourceBase = os.path.normpath(os.path.join(sourceBase, ".."))		

		if sourceBase != os.curdir:
			common = os.path.commonprefix([sourceBase, path])
			url = path[len(common) +1:]
			return url
		return path

	def _newlineToBr(self, text):
		if text:
			return text.replace("\n", "<br />\n")
		else:
			return text

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
			if not path.startswith(os.path.normpath(self._templates["resources"])):
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
	resources.exposed = True

	def index(self):
		t = pyratemp.Template(filename=self._templates["modules"])
		return t(**{
			"mods": sorted(self._mods.keys())
		})
	index.exposed = True

	def priorities_html(self):
		profiles = self._mm.mods("active", type="profileDescription")
		profiles = sorted(profiles, key=lambda p: p.desc["name"])

		mods = {}
		for mod in self._mm.mods("priorities"):
			mods[self._pathToUrl(os.path.dirname(mod.__class__.__file__))] = mod
		mods = sorted(mods.iteritems())

		t = pyratemp.Template(filename=self._templates["priorities"])
		return t(**{
			"mods": mods,
			"profiles": profiles,
		})
	priorities_html.exposed = True

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
					self._pathToUrl(os.path.dirname(requiredMod.__class__.__file__)),
					requiredMod.__class__.__name__
				))
		requirements.append(selectorResults)
		return requirements

	def modules(self, *args):
		args = list(args)
		args[-1] = args[-1][:-len(".html")]
		try:
			mod = self._mods["modules/" + "/".join(args)]
		except KeyError:
			raise cherrypy.HTTPError(404)

		attrs = dir(mod)
		methods = filter(lambda x: self._isFunction(mod, x), attrs)
		properties = set(attrs) - set(methods)

		checkPublic = lambda x: not x.startswith("_")
		methods = filter(checkPublic, methods)
		properties = filter(checkPublic, properties)

		#remove special properties
		properties = set(properties) - set(["type", "uses", "requires"])

		propertyDocs = {}
		for property in properties:
			try:
				propertyObj = getattr(mod.__class__, property)
			except AttributeError:
				#no @property
				continue
			try:
				propertyDocs[property] = self._newlineToBr(propertyObj.__doc__)
			except AttributeError:
				#also no @property
				continue

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

		fileData = []
		for root, dirs, files in os.walk(os.path.dirname(mod.__class__.__file__)):
			for f in sorted(files):
				ext = os.path.splitext(f)[1]
				if ext not in [".html", ".py", ".js", ".css", ".po", ".pot"]:
					continue
				path = os.path.join(root, f)

				code = open(path).read()
				lexer = pygments.lexers.get_lexer_for_filename(path)
				formatter = pygments.formatters.HtmlFormatter(**{
					"linenos": "table",
					"anchorlinenos": True,
					"lineanchors": path,
				})

				source = pygments.highlight(code, lexer, formatter)
				commonLength = len(os.path.commonprefix([
					path,
					os.path.dirname(mod.__class__.__file__)
				]))
				fileData.append((path[commonLength:], source))

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
			"propertyDocs": propertyDocs,
			"files": fileData,
			#last formatter is still there
			"pygmentsStyle": formatter.get_style_defs('.source'),
		})
	modules.exposed = True

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
			"codedocumentation": 0,
			"default": -1,
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
			"server.socket_host": "0.0.0.0",
			"environment": "production",
		})
		cherrypy.engine.start()
		webbrowser.open("http://localhost:8080/")
		print "Serving at http://localhost:8080/"
		print "Type 'quit' and press enter to stop the server"
		while True:
			try:
				if raw_input("> ").lower() in ("q", "quit"):
					break
			except KeyboardInterrupt:
				break
		cherrypy.engine.exit()

	def enable(self):
		global cherrypy, pygments, pyratemp
		try:
			import cherrypy
			import pygments
			import pygments.lexers
			import pygments.formatters
			import pygments.util
			import pyratemp
		except ImportError:
			return #leave disabled

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
