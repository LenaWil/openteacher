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
			self._mm.mods(type="devDocs"),
			self._mm.mods(type="qtApp"),
		)
		self.uses = (
			self._mm.mods(type="profileDescription"),
		)
		self.priorities = {
			"code-documentation": 0,
			"default": -1,
		}
		self.devMod = True

	def showDocumentation(self):
		print "Serving at 0.0.0.0:8080. Ctrl + C to abort"
		self._impl.app.run(host="0.0.0.0", port=8080)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self.showDocumentation)

		self._impl = self._mm.import_("serverImpl")
		try:
			import flask
			import pygments
			import pygments.lexers
			import pygments.formatters
			import pygments.util
			import docutils.core
			import pyratemp

			from PyQt4 import QtGui
		except ImportError:
			sys.stderr.write("For this developer module to work, you need to have flask, pygments, pyratemp, PyQt4 and docutils installed. And indirectly, pygraphviz.\n")
			return #leave disabled

		#enable syntax highlighting
		self._mm.import_("rst-directive")

		self._impl.flask = flask
		self._impl.pygments = pygments
		self._impl.docutils = docutils
		self._impl.pyratemp = pyratemp
		self._impl.QtGui = QtGui

		metadata = self._modules.default("active", type="metadata").metadata
		class utilsMod:
			hue = metadata["mainColorHue"]
			templates = {
				"modules": self._mm.resourcePath("templ/modules.html"),
				"priorities": self._mm.resourcePath("templ/priorities.html"),
				"fixmes": self._mm.resourcePath("templ/fixmes.html"),
				"module": self._mm.resourcePath("templ/module.html"),
				"dev_docs": self._mm.resourcePath("templ/dev_docs.html"),
				"resources": self._mm.resourcePath("resources"),
				"style": self._mm.resourcePath("templ/style.css"),
				"logo": metadata["iconPath"],
			}
			buildModuleGraph = self._modules.default("active", type="moduleGraphBuilder").buildModuleGraph
			devDocsBaseDir = self._modules.default("active", type="devDocs").developerDocumentationBaseDirectory
			mm = self._mm

		self._impl.utils = utilsMod
		self._impl.initialize()

		self.active = True

	def disable(self):
		self.active = False

		self._modules.default(type="execute").startRunning.unhandle(self.showDocumentation)
		del self._modules
		del self._impl

def init(moduleManager):
	return CodeDocumentationModule(moduleManager)
