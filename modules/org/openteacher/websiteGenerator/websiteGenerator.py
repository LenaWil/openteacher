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

import sys
import os
import shutil
import glob

DOWNLOAD_LINK = "http://sourceforge.net/projects/openteacher/files/openteacher/3.1/openteacher-3.1-windows-setup.msi/download"

class WebsiteGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebsiteGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "websiteGenerator"

		self.requires = (
			self._mm.mods(type="execute"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)

		self.priorities = {
			"generate-website": 0,
			"default": -1,
		}

		self._templatesDir = self._mm.resourcePath("templates")
		self._docsTemplatesDir = self._mm.resourcePath("docsTemplates")

		templatesFiles = glob.glob(os.path.join(self._templatesDir, "/*"))
		docTemplatesFiles = glob.glob(os.path.join(self._docsTemplatesDir, "/*"))
		self.filesWithTranslations = templatesFiles + docTemplatesFiles

	def generateWebsite(self):
		"""Generates the complete OT website into a directory specified
		   as the first command line argument.

		"""
		self._path = self._makeOutputDir()
		if not self._path:
			return

		self._copyResources()
		self._generateHtml()

		print "Writing OpenTeacher website to '%s' is now done." % self._path

	def _makeOutputDir(self):
		"""Gets the output directory name and creates it. Asks if
		   overwriting it is allowed in case that's needed. Returns True
		   on success, otherwise False.

		"""
		#get path to save to
		try:
			path = sys.argv[1]
		except IndexError:
			print >> sys.stderr, "Please specify a path to save the website to. (e.g. -p generate-website website-debug)"
			return
		#ask if overwrite
		if os.path.exists(path):
			confirm = raw_input("There is already a directory at '%s'. Do you want to remove it and continue (y/n). " % path)
			if confirm != "y":
				return
			shutil.rmtree(path)

		os.mkdir(path)
		return path

	def _copyResources(self):
		"""Copies all static website resources into place."""

		copyTree = lambda name: shutil.copytree(
			self._mm.resourcePath(name),
			os.path.join(self._path, name)
		)
		copy = lambda name: shutil.copy(
			self._mm.resourcePath(name),
			os.path.join(self._path, name)
		)
		# Copy images, scripts etc.
		copyTree("images")
		copyTree("scripts")
		copy("style.css")
		copy("index.php")

	def _generateHtml(self):
		"""Generates all html files: first for US English and then for
		   all the available translations.

		"""
		# The default (US English) (unicode as translate function)
		self._tr = unicode
		self._generatePages("en")

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			# All the other languages
			for poname in os.listdir(self._mm.resourcePath('translations')):
				if not poname.endswith('.po'):
					continue
				langCode = os.path.splitext(poname)[0]

				# Set translation function
				_, ngettext = translator.gettextFunctions(self._mm.resourcePath("translations"), language=langCode)
				self._tr = _

				# Generate
				self._generatePages(langCode)

	def _generatePages(self, lang):
		"""Generates all pages in a certain language in a subdirectory
		   of the main output path. First it generates the normal pages,
		   then the documentation ones.

		"""
		self._langDir = os.path.join(self._path, lang)
		os.mkdir(self._langDir)

		templates = ["about.html", "download.html", "documentation.html", "index.html", "contribute.html"]
		for pageName in templates:
			self._generatePage(pageName)

		docsDir = os.path.join(self._langDir, "documentation")
		os.mkdir(docsDir)
		documentationTemplates = os.listdir(self._docsTemplatesDir)
		for filename in documentationTemplates:
			self._generateDocumentationPage(filename)

	def _generateDocumentationPage(self, filename):
		"""Combines the documentation text, with the stuff shared
		   between all documentation pages, and wraps the result in a
		   page.

		"""
		#the documentation text
		templatePath = os.path.join(self._docsTemplatesDir, filename)
		pageName = "documentation/" + filename
		docContent = self._evaluateTemplate(templatePath, pageName)

		#the documentation wrapper
		templatePath = os.path.join(self._templatesDir, "docpage.html")
		content = self._evaluateTemplate(templatePath, pageName, docContent=docContent)

		self._writePage(pageName, content)

	def _generatePage(self, pageName):
		"""Gets the content of the page, and writes it into a page."""

		filename = os.path.join(self._templatesDir, pageName)
		content = self._evaluateTemplate(filename, pageName, downloadLink=DOWNLOAD_LINK)

		self._writePage(pageName, content)

	def _writePage(self, pageName, content):
		"""Wraps content into a page template and writes the result to
		   disk

		"""
		page = self._wrapContent(pageName, content)

		with open(os.path.join(self._langDir, pageName), "w") as f:
			f.write(page)

	def _wrapContent(self, pageName, content):
		"""Wraps content into a page template"""

		filename = os.path.join(self._templatesDir, "base.html")
		return self._evaluateTemplate(filename, pageName, pageName=pageName, content=content)

	def _evaluateTemplate(self, templatePath, thisPage, **kwargs):
		class EvalPseudoSandbox(pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)
				self2.register("tr", self._tr)
				currentDir = os.path.dirname(thisPage)
				self2.register("url", lambda name: os.path.relpath(name, currentDir))

		t = pyratemp.Template(filename=templatePath, eval_class=EvalPseudoSandbox)
		return t(**kwargs)

	def enable(self):
		global pyratemp
		try:
			import pyratemp
		except ImportError:
			sys.stderr.write("For this developer module to work, you need to have pyratemp installed.\n")

		self._modules = set(self._mm.mods(type="modules")).pop()

		self._modules.default(type="execute").startRunning.handle(self.generateWebsite)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return WebsiteGeneratorModule(moduleManager)
