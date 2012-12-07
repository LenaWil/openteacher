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

# cherrypy, pygments, pyratemp & docutils.core are imported in enable()

import webbrowser
import inspect
import os
import types
import mimetypes
import sys
import re
import tempfile

class ModulesHandler(object):
	def __init__(self, moduleManager, templates, buildModuleGraph, *args, **kwargs):
		super(ModulesHandler, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._mods = {}

		for mod in self._mm.mods:
			#get the path of the module
			path = os.path.dirname(mod.__class__.__file__)
			#make sure the path is relative to the modules root for easier recognition
			self._mods[self._pathToUrl(path)] = mod
		self._templates = templates
		self._buildModuleGraph = buildModuleGraph

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

	def _format(self, text):
		if text:
			return docutils.core.publish_parts(
				text.replace("\t", "").replace("   ", ""),
				writer_name="html",
				settings_overrides={"report_level": 5}
			)["html_body"]
		else:
			return text

	def module_graph_svg(self):
		cherrypy.response.headers["Content-Type"] = "image/svg+xml"
		try:
			path = tempfile.mkstemp(".svg")[1]
			self._buildModuleGraph(path)
			with open(path) as f:
				return f.read()
		finally:
			os.remove(path)
	module_graph_svg.exposed = True

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
		profileMods = self._mm.mods("active", type="profileDescription")
		profiles = (profileMod.desc["name"] for profileMod in profileMods)
		profiles = ["default"] + sorted(profiles)

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

	def fixmes_html(self):
		def upOne(p):
			return os.path.normpath(os.path.join(p, ".."))

		basePath = os.path.dirname(__file__)
		while not basePath.endswith("modules"):
			basePath = upOne(basePath)

		rePattern = re.compile("fixme|todo", re.IGNORECASE)
		fixmes = []
		for root, dirs, files in sorted(os.walk(basePath)):
			for file in sorted(files):
				fpath = os.path.join(root, file)
				if os.path.splitext(fpath)[1] in (".png", ".gif", ".bmp", ".ico", ".pyc", ".mo", ".psd", ".gpg", ".pem", ".sqlite3", ".rtf", ".po", ".pot"):
					#no fixme's etc. in there...
					continue
				if fpath.endswith("~"):
					#not in here too
					continue
				if "jquery" in fpath:
					#actually a lot of TODO's in there, but we don't care :)
					continue
				if "admin_files" in fpath:
					#some django files. Again, we don't care.
					continue
				if "codeDocs" in fpath:
					#this module mentions the words fixme and todo
					#while there aren't any. The rule is: no fixme's
					#here! :P
					continue
				with open(fpath, "r") as f:
					lines = f.readlines()

				def toUnicode(data):
					return unicode(data, encoding="UTF-8", errors="replace")
				lines = map(toUnicode, lines)
				for i, line in enumerate(lines):
					match = rePattern.search(line)
					if not match:
						continue
					try:
						lines[i - 2]
					except IndexError:
						startNumber = 0
					else:
						startNumber = i - 2
					try:
						lines[i + 5]
					except IndexError:
						endNumber = len(lines) - 1
					else:
						endNumber = i + 5
					relevantLines = lines[startNumber:endNumber]
					relevantCode = u"".join(relevantLines)

					lexer = pygments.lexers.get_lexer_for_filename(fpath)
					formatter = pygments.formatters.HtmlFormatter()
					fixmes.append({
						"path": self._pathToUrl(unicode(fpath, sys.getfilesystemencoding())),
						"line_number": i + 1,
						"relevant_code": pygments.highlight(relevantCode, lexer, formatter),
					})

		t = pyratemp.Template(filename=self._templates["fixmes"])
		return t(**{
			"fixmes": fixmes,
			#use last formatter if it's still there
			"pygmentsStyle": formatter.get_style_defs('.source') if "formatter" in vars() else "",
		})
	fixmes_html.exposed = True

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
				propertyDocs[property] = self._format(propertyObj.__doc__)
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
			methodDocs[method] = self._format(methodObj.__doc__)
			methodArgs[method] = self._constructSignature(inspect.getargspec(methodObj))

		fileData = []
		for root, dirs, files in os.walk(os.path.dirname(mod.__class__.__file__)):
			for f in sorted(files):
				ext = os.path.splitext(f)[1]
				if ext not in [".html", ".py", ".js", ".css", ".po", ".pot"]:
					continue
				if "jquery" in f.lower():
					continue
				path = os.path.normpath(os.path.join(root, f))

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
			"moddoc": self._format(mod.__doc__),
			"type": getattr(mod, "type", None),
			"uses": uses,
			"requires": requires,
			"methods": sorted(methods),
			"methodDocs": methodDocs,
			"methodArgs": methodArgs,
			"properties": sorted(properties),
			"propertyDocs": propertyDocs,
			"files": fileData,
			#use last formatter if it exists
			"pygmentsStyle": formatter.get_style_defs('.source') if "formatter" in vars() else "",
		})
	modules.exposed = True

	def _constructSignature(self, data):
		try:
			args = reversed(data.args)
		except TypeError:
			args = []
		try:
			defaults = list(reversed(data.defaults))
		except TypeError:
			defaults = []

		result = []
		for i, arg in enumerate(args):
			try:
				result.insert(0, "%s=%s" % (arg, defaults[i]))
			except IndexError:
				result.insert(0, arg)
		if data.varargs:
			result.append("*" + data.varargs)
		if data.keywords:
			result.append("**" + data.keywords)
		return result

class CodeDocumentationModule(object):
	"""This module generates code documentation for OpenTeacher
	   automatically based on the actual code. When the server crashes,
	   you can see the error message by adding the 'debug' parameter.
	   (i.e. ``python openteacher.py -p code-documentation debug``).

	   This module generates the following documentation:

	   - Overview of all modules
	   - Overview of the methods and properties of the module classes,
	     including docstrings.
	   - Source listing (including syntax highlighting)
	   - The module map (showing all dependencies between modules)
	   - FIXMEs/TODOs overview

	"""
	def __init__(self, moduleManager, *args, **kwargs):
		super(CodeDocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "codeDocumentationShower"

		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="execute"),
			self._mm.mods(type="moduleGraphBuilder"),
		)
		self.uses = (
			self._mm.mods(type="profileDescription"),
		)
		self.priorities = {
			"code-documentation": 0,
			"default": -1,
		}

	def showDocumentation(self):
		buildModuleGraph = self._modules.default("active", type="moduleGraphBuilder").buildModuleGraph
		templates = {
			"modules": self._mm.resourcePath("templ/modules.html"),
			"priorities": self._mm.resourcePath("templ/priorities.html"),
			"fixmes": self._mm.resourcePath("templ/fixmes.html"),
			"module": self._mm.resourcePath("templ/module.html"),
			"resources": self._mm.resourcePath("resources"),
			"logo": self._modules.default("active", type="metadata").metadata["iconPath"],
		}
		root = ModulesHandler(self._mm, templates, buildModuleGraph)

		cherrypy.tree.mount(root)
		cherrypy.config.update({"server.socket_host": "0.0.0.0"})
		if not (len(sys.argv) > 1 and sys.argv[1] == "debug"):
			cherrypy.config.update({"environment": "production"})
		cherrypy.engine.start()
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
		global cherrypy, pygments, pyratemp, docutils
		try:
			import cherrypy
			import pygments
			import pygments.lexers
			import pygments.formatters
			import pygments.util
			import pyratemp
			import docutils.core
		except ImportError:
			sys.stderr.write("For this developer module to work, you need to have cherrypy, pygments, pyratemp and docutils installed. And indirectly, pygraphviz.\n")
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
