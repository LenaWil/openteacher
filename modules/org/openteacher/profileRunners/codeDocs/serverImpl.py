#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2013, Marten de Vries
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

import inspect
import os
import types
import mimetypes
import sys
import re
import tempfile

import __builtin__
BUILTIN_TYPES = [t for t in __builtin__.__dict__.itervalues() if isinstance(t, type)]

#handled by main module (but only added after import of this file!):
#import flask
#import pygments
#import pygments.lexers
#import pygments.formatters
#import pygments.util
#import docutils.core
#import pyratemp
#from PyQt4 import QtGui

#import utils #some functions, constants, etc.

import sys

def initialize():
	global app
	app = flask.Flask(__name__)

	def formatter(path):
		return pygments.formatters.HtmlFormatter(**{
			"linenos": "table",
			"anchorlinenos": True,
			"lineanchors": pathToUrl(path),
		})

	def pathToUrl(path):
		path = os.path.abspath(path)

		sourceBase = os.path.abspath(os.path.dirname(__file__))
		while not sourceBase.endswith("modules"):
			sourceBase = os.path.normpath(os.path.join(sourceBase, ".."))
		sourceBase = os.path.normpath(os.path.join(sourceBase, ".."))		

		if sourceBase != os.curdir:
			common = os.path.commonprefix([sourceBase, path])
			url = path[len(common) +1:]
			return url
		return path

	def formatRst(text):
		if text:
			return docutils.core.publish_parts(
				text.replace("\t", "").replace("   ", ""),
				writer_name="html",
				settings_overrides={"report_level": 5}
			)["html_body"]
		else:
			return text

	@app.route("/module_graph.svg")
	def module_graph_svg():
		try:
			fd, path = tempfile.mkstemp(".svg")
			os.close(fd)
			utils.buildModuleGraph(path)
			return flask.send_file(path)
		finally:
			os.remove(path)

	@app.route("/style.css")
	def style_css():
		t = pyratemp.Template(filename=utils.templates["style"])
		data = t(**{
			"headerBackgroundColor": QtGui.QColor.fromHsv(utils.hue, 41, 250).name(),
			"bodyBackgroundColor": QtGui.QColor.fromHsv(utils.hue, 7, 253, 255).name(),
			"footerBackgroundColor": QtGui.QColor.fromHsv(utils.hue, 30, 228).name(),
			"pygmentsStyle": formatter(".").get_style_defs('.highlight'),
		})
		resp = flask.make_response(data)
		resp.headers["Content-Type"] = "text/css"
		return resp

	@app.route("/resources/<path:path>")
	def resources(path):
		if path == "logo":
			path = utils.templates["logo"]
		else:
			#construct the path
			path = os.path.normpath(
				os.path.join(utils.templates["resources"], path)
			)
			#check if the path is valid (i.e. is in the resources
			#directory.)
			if not path.startswith(os.path.normpath(utils.templates["resources"])):
				flask.abort(404)

		try:
			return flask.send_file(path)
		except IOError:
			flask.abort(404)

	@app.route("/")
	def index():
		t = pyratemp.Template(filename=utils.templates["modules"])
		return t(**{
			"mods": sorted(mods.keys())
		})

	@app.route("/priorities.html")
	def priorities_html():
		profileMods = utils.mm.mods("active", type="profileDescription")
		profiles = (profileMod.desc["name"] for profileMod in profileMods)
		profiles = ["default"] + sorted(profiles)

		mods = {}
		for mod in utils.mm.mods("priorities"):
			mods[pathToUrl(os.path.dirname(mod.__class__.__file__))] = mod
		mods = sorted(mods.iteritems())

		t = pyratemp.Template(filename=utils.templates["priorities"])
		return t(**{
			"mods": mods,
			"profiles": profiles,
		})

	def fixmePaths():
		#get base directory
		def upOne(p):
			return os.path.normpath(os.path.join(p, ".."))

		basePath = os.path.abspath(os.path.dirname(__file__))
		while not basePath.endswith("modules"):
			basePath = upOne(basePath)

		#get all paths
		paths = (
			os.path.join(root, file)
			for root, dirs, files in sorted(os.walk(basePath))
			for file in files
		)
		#and filter them, return the results
		return (
			p for p in paths
			if not (
				os.path.splitext(p)[1] in (".png", ".gif", ".bmp", ".ico", ".pyc", ".mo", ".psd", ".gpg", ".pem", ".sqlite3", ".rtf", ".po", ".pot")
				or p.endswith("~")
				or "jquery" in p
				or "admin_files" in p
				or "codeDocs" in p
				or "ircBot" in p
				or "words.txt" in p
				or "dev_tools.rst" in p
				or "pouchdb.js" in p
			)
		)

	@app.route("/fixmes.html")
	def fixmes_html():
		rePattern = re.compile("fixme|todo", re.IGNORECASE)
		fixmes = []
		for fpath in fixmePaths():
			with open(fpath, "r") as f:
				lines = f.readlines()

			lines = [
				unicode(line, encoding="UTF-8", errors="replace")
				for line in lines
			]
			for i, line in enumerate(lines):
				match = rePattern.search(line)
				if not match:
					continue
				if i - 2 > 0:
					startNumber = i - 2
				else:
					startNumber = 0
				try:
					lines[i + 5]
				except IndexError:
					endNumber = len(lines)
				else:
					endNumber = i + 5
				relevantLines = lines[startNumber:endNumber]
				relevantCode = u"".join(relevantLines)

				try:
					lexer = pygments.lexers.get_lexer_for_filename(fpath)
				except pygments.util.ClassNotFound:
					lexer = pygments.lexers.TextLexer()
				formatter = pygments.formatters.HtmlFormatter()
				fixmes.append({
					"path": pathToUrl(unicode(fpath, sys.getfilesystemencoding())),
					"line_number": i + 1,
					"relevant_code": pygments.highlight(relevantCode, lexer, formatter),
				})

		t = pyratemp.Template(filename=utils.templates["fixmes"])
		return t(**{
			"fixmes": fixmes,
		})

	def isFunction(mod, x):
		try:
			obj = getattr(mod.__class__, x)
		except AttributeError:
			obj = getattr(mod, x)
		return isinstance(obj, types.MethodType)

	def modsForRequirement(selectors):
		for selector in selectors:
			selectorResults = set()
			requiredMods = set(selector)
			for requiredMod in requiredMods:
				selectorResults.add((
					pathToUrl(os.path.dirname(requiredMod.__class__.__file__)),
					requiredMod.__class__.__name__
				))
			yield selectorResults

	def renderRstPage(rstPath):
		with open(rstPath) as f:
			parts = docutils.core.publish_parts(
				f.read(),
				writer_name="html",
				settings_overrides={
					"report_level": 5,
					"initial_header_level": 2
				}
			)

		t = pyratemp.Template(filename=utils.templates["dev_docs"])
		return t(**{
			"page": parts["fragment"],
			"title": parts["title"]
		})

	@app.route("/dev_docs/", defaults={"path": "index.rst"})
	@app.route("/dev_docs/<path:path>")
	def dev_docs(path):
		requestedPath = os.path.normpath(path)
		if os.path.isabs(requestedPath) or requestedPath.startswith(os.pardir):
			#invalid path
			flask.abort(404)
		path = os.path.join(utils.devDocsBaseDir, requestedPath)

		if not os.path.exists(path):
			flask.abort(404)

		if path.endswith(".rst"):
			return renderRstPage(path)
		else:
			return flask.send_file(os.path.abspath(path))

		#if all else fails
		flask.abort(404)

	def propertyDocs(property):
		#first try if the class attribute has a doc string. This
		#catches e.g. @property-decorated function docstrings.
		try:
			return formatRst(getattr(mod.__class__, property).__doc__)
		except:
			#all errors aren't important enough to fail for
			pass
		#then try to get the docstring of the object itself.
		try:
			propertyObj = getattr(mod, property)
		except:
			#errors aren't important enough to fail for.
			return
		if propertyObj.__class__ != type and propertyObj.__class__ in BUILTIN_TYPES:
			#docstring is uninteresting
			return
		try:
			return formatRst(propertyObj.__doc__)
		except AttributeError:
			#no docstring.
			return

	def fileDataForMod(mod):
		for root, dirs, files in os.walk(os.path.dirname(mod.__class__.__file__)):
			for f in sorted(files):
				ext = os.path.splitext(f)[1]
				if ext not in [".html", ".py", ".js", ".css", ".po", ".pot"]:
					continue
				if "jquery" in f.lower():
					continue
				path = os.path.join(root, f)
				if os.path.getsize(path) > 1.0/4.0 * 1024 * 1024:
					#> 0.25MB
					continue

				code = open(path).read()

				lexer = pygments.lexers.get_lexer_for_filename(path)
				source = pygments.highlight(code, lexer, formatter(path))
				commonLength = len(os.path.commonprefix([
					path,
					os.path.dirname(mod.__class__.__file__)
				]))
				yield path[commonLength:], source

	@app.route("/modules/<path:path>")
	def modules(path):
		path = path[:-len(".html")]
		try:
			mod = mods["modules/" + path]
		except KeyError:
			flask.abort(404)

		attrs = set(dir(mod))
		methods = set(func for func in attrs if isFunction(mod, func))
		properties = attrs - methods

		isPublic = lambda x: not x.startswith("_")
		methods = set(m for m in methods if isPublic(m))

		methodDocs = {}
		methodArgs = {}
		for method in methods:
			methodObj = getattr(mod, method)
			methodDocs[method] = formatRst(methodObj.__doc__)
			methodArgs[method] = constructSignature(inspect.getargspec(methodObj))

		properties = set(p for p in properties if isPublic(p))

		#remove special properties
		properties -= set(["type", "uses", "requires", "priorities", "filesWithTranslations"])
		propertyDocstrings = dict(
			(p, propertyDocs(p))
			for p in properties
			if propertyDocs(p) is not None
		)

		#uses
		uses = modsForRequirement(getattr(mod, "uses", []))

		#requires
		requires = modsForRequirement(getattr(mod, "requires", []))

		fileData = fileDataForMod(mod)

		t = pyratemp.Template(filename=utils.templates["module"])
		return t(**{
			"name": mod.__class__.__name__,
			"moddoc": formatRst(mod.__doc__),
			"type": getattr(mod, "type", None),
			"uses": uses,
			"requires": requires,
			"methods": sorted(methods),
			"methodDocs": methodDocs,
			"methodArgs": methodArgs,
			"properties": sorted(properties),
			"propertyDocs": propertyDocstrings,
			"files": fileData,
		})

	def constructSignature(data):
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

	mods = {}
	for mod in utils.mm.mods:
		#get the path of the module
		path = os.path.dirname(mod.__class__.__file__)
		#make sure the path is relative to the modules root for easier recognition
		mods[pathToUrl(path)] = mod
