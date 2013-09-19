#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Milan Boers
#	Copyright 2013, Marten de Vries
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
import posixpath
import shutil
import tempfile
import atexit
import json
import glob

DOWNLOAD_LINKS = {
	"windows": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher-3.2-windows-setup.msi/download",
	"windows-portable": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher-3.2-windows-portable.zip/download",
	"osx": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher_3.2_mac.dmg/download",
	"ubuntu": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher_3.2.deb/download",
	"fedora": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher_3.2_fedora.rpm/download",
	"opensuse": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher_3.2_opensuse.rpm/download",
	"arch": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher_3.2_archlinux.pkg.tar.xz/download",
	"linux": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher_3.2_linux.tar.gz/download",
	"source": "http://sourceforge.net/projects/openteacher/files/openteacher/3.2/openteacher-3.2-source.zip/download",
}

#image generators
class ButtonImagesGenerator(object):
	def __init__(self, hue, *args, **kwargs):
		super(ButtonImagesGenerator, self).__init__(*args, **kwargs)

		self._hue = hue

	def generateButtons(self, logoAndOutputNames):
		for logoPath, outputBasename in logoAndOutputNames:
			self._generateHoveredAndNormalButtons(logoPath, outputBasename)

	def _generateHoveredAndNormalButtons(self, logoPath, basename):
		gradientTopColor = QtGui.QColor.fromHsv(self._hue, 46, 246)
		gradientBottomColor = QtGui.QColor.fromHsv(self._hue, 58, 229)
		self._generateDownloadButton(gradientTopColor, gradientBottomColor, logoPath, basename + ".png")

		hoveredGradientTopColor = QtGui.QColor.fromHsv(self._hue, 47, 251)
		hoveredGradientBottomColor = QtGui.QColor.fromHsv(self._hue, 57, 236)
		self._generateDownloadButton(gradientTopColor, gradientBottomColor, logoPath, basename + "-h.png")

	def _generateDownloadButton(self, gradientTopColor, gradientBottomColor, logoPath, path):
		width = 382
		height = 66
		radius = 9
		xMargin = 9
		yMargin = 10
		logoHeight = 44

		borderColor = QtGui.QColor.fromHsv(-1, 0, 146)

		gradient = QtGui.QLinearGradient(0, 0, 0, height)
		gradient.setColorAt(0, gradientTopColor)
		gradient.setColorAt(1, gradientBottomColor)

		logo = QtGui.QImage(logoPath).scaledToHeight(logoHeight, QtCore.Qt.SmoothTransformation)

		img = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
		img.fill(QtCore.Qt.transparent)
		painter = QtGui.QPainter(img)

		painter.setPen(borderColor)
		painter.setBrush(gradient)
		painter.drawRoundedRect(0, 0, width -1, height -1, radius, radius)
		painter.drawImage(xMargin, yMargin, logo)

		painter.end()
		img.save(path)

class LightImage(object):
	def __init__(self, hue, *args, **kwargs):
		super(LightImage, self).__init__(*args, **kwargs)

		self._hue = hue

	def save(self, path):
		"""Generates a half circle filled with a gradient to be used to
		   show which menu item the mouse is at/which page is active.

		"""
		width = 26
		height = 13
		color = QtGui.QColor.fromHsv(self._hue, 59, 240, 255)

		img = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
		img.fill(QtCore.Qt.transparent)
		painter = QtGui.QPainter(img)

		gradient = QtGui.QRadialGradient(width / 2, 0, height / 4 * 3)
		gradient.setColorAt(0, color)
		gradient.setColorAt(0.4, color)
		gradient.setColorAt(1, QtCore.Qt.transparent)

		painter.setPen(QtCore.Qt.NoPen)
		painter.setBrush(gradient)

		painter.drawRect(0, 0, width, height)

		painter.end()
		img.save(path)

class BackgroundImagesGenerator(object):
	def __init__(self, hue, generateBodyBackgroundImage, *args, **kwargs):
		super(BackgroundImagesGenerator, self).__init__(*args, **kwargs)

		self._hue = hue
		self._generateBodyBackgroundImage = generateBodyBackgroundImage

	def generateBackground(self, path):
		"""Generates the background file: a small bug high file with
		   nothing but a gradient inside.

		"""
		width = 1
		height = 1000
		startColor = QtGui.QColor.fromHsv(self._hue, 43, 250)
		endColor = QtGui.QColor.fromHsv(self._hue, 21, 227)

		img = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
		img.fill(QtCore.Qt.transparent)

		gradient = QtGui.QLinearGradient(0, 0, 0, height)
		gradient.setColorAt(0, startColor)
		gradient.setColorAt(1, endColor)

		painter = QtGui.QPainter(img)
		painter.setBrush(gradient)
		painter.setPen(QtCore.Qt.NoPen)
		painter.drawRect(0, 0, width, height)
		painter.end()
		img.save(path)

	def generateBodyBackground(self, path):
		img = self._generateBodyBackgroundImage()

		#and save it.
		img.save(path)

#style sheet
class StyleSheet(object):
	def __init__(self, hue, lineColor, template, *args, **kwargs):
		super(StyleSheet, self).__init__(*args, **kwargs)

		self._hue = hue
		self._lineColor = lineColor
		self._template = template

	def save(self, path):
		"""Generates the style sheet of OpenTeacher using ``self._hue``
		   (which comes from metadata) for the colors.

		"""
		t = pyratemp.Template(filename=self._template)
		with open(path, "w") as f:
			f.write(t(**{
				"aLinkColor": QtGui.QColor.fromHsv(self._hue, 63, 101).name(),
				"aHoverColor": QtGui.QColor.fromHsv(self._hue, 66, 159).name(),
				"bodyBackgroundColor": QtGui.QColor.fromHsv(self._hue, 30, 228).name(),
				"bodyTextColor": QtGui.QColor.fromHsv(self._hue, 64, 64).name(),
				"hrColor": self._lineColor,
				"downloadTableBorderColor": self._lineColor,
				"downloadRowBackgroundColor": QtGui.QColor.fromHsv(self._hue, 27, 234).name(),
				"downloadRowBorderColor": self._lineColor,
				"codeBlockBackgroundColor": QtGui.QColor.fromHsv(self._hue, 21, 240).name(),
			}).encode("UTF-8"))

class WebsiteGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebsiteGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "websiteGenerator"

		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="ui"),
			self._mm.mods(type="metadata"),
			self._mm.mods(type="userDocumentation"),
			self._mm.mods(type="userDocumentationWrapper"),
			self._mm.mods(type="backgroundImageGenerator"),
			self._mm.mods(type="friendlyTranslationNames"),
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

		templatesFiles = [os.path.join("templates", f) for f in os.listdir(self._templatesDir)]
		docTemplatesFiles = [os.path.join("docsTemplates", f) for f in os.listdir(self._docsTemplatesDir)]
		self.filesWithTranslations = templatesFiles + docTemplatesFiles

		self._tempPaths = []
		atexit.register(self._removeTempDirs)

	def _removeTempDirs(self):
		for path in self._tempPaths:
			shutil.rmtree(path)

	def generateWebsite(self):
		"""Generates the complete OT website into a directory specified
		   as the first command line argument.

		"""
		self._path = self._makeOutputDir()
		if not self._path:
			return

		self._copyResources()
		self._generateResources()
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

	@property
	def _userDocMod(self):
		return self._modules.default("active", type="userDocumentation")

	@property
	def _userDocWrapperMod(self):
		return self._modules.default("active", type="userDocumentationWrapper")

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
		copyTree("inAppDocs")
		copyTree("files")
		copy("index.php")
		copy("documentation.html")

		#Copy user documentation's static files
		shutil.copytree(
			self._userDocMod.resourcesPath,
			os.path.join(self._path, "images/docs/3"),
		)

	def _generateResources(self):
		"""Generates a few resources."""

		toPath = lambda part: os.path.join(self._path, part)
		fromPath = lambda part: self._mm.resourcePath(os.path.join("images/oslogos/", part))

		#stylesheet
		style = StyleSheet(self._hue, self._lineColor, template=self._mm.resourcePath("style.css"))
		style.save(toPath("style.css"))
		#images
		bgGenerator = BackgroundImagesGenerator(self._hue, self._modules.default("active", type="backgroundImageGenerator").generate)
		bgGenerator.generateBackground(toPath("images/bg.png"))
		bgGenerator.generateBodyBackground(toPath("images/body.png"))
		LightImage(self._hue).save(toPath("images/light.png"))
		#button backgrounds (which include logos)
		ButtonImagesGenerator(self._hue).generateButtons([
			(fromPath("fedoralogo.png"), toPath("images/downloadbuttons/fedora-button")),
			(fromPath("tuxlogo.png"), toPath("images/downloadbuttons/linux-button")),
			(fromPath("osxlogo.png"), toPath("images/downloadbuttons/osx-button")),
			(fromPath("ubulogo.png"), toPath("images/downloadbuttons/ubuntu-button")),
			(fromPath("winlogo.png"), toPath("images/downloadbuttons/windows-button")),
		])
		#icon
		shutil.copy(self._iconPath, toPath("images/openteacher-icon.png"))

	def _generateHtml(self):
		"""Generates all html files: first for US English and then for
		   all the available translations. If that's done, it generates
		   the in app documentation pages (that are in a separate
		   directory).

		"""
		# The default (US English) (unicode as translate function)
		self._tr = unicode
		self._langCode = "en"
		self._generatePages()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			# All the other languages
			for moname in os.listdir(self._mm.resourcePath('translations')):
				if not moname.endswith('.mo'):
					continue
				self._langCode = os.path.splitext(moname)[0]

				# Set translation function
				_, ngettext = translator.gettextFunctions(self._mm.resourcePath("translations"), language=self._langCode)
				self._tr = _

				# Generate
				self._generatePages()

		# Generate inAppDocumentation pages.
		for lang in list(self._userDocMod.availableTranslations) + ["en"]:
			destination = os.path.join(self._path, "inAppDocs", lang + ".html")
			html = self._getWrappedUserDocumentation(lang)
			with open(destination, "w") as f:
				f.write(html.encode("UTF-8"))

	def _generatePages(self):
		"""Generates all pages in a certain language in a subdirectory
		   of the main output path. First it generates the normal pages,
		   then the documentation ones.

		"""
		self._langDir = os.path.join(self._path, self._langCode)
		os.mkdir(self._langDir)

		templates = ["about.html", "news.html", "download.html", "documentation.html", "index.html", "contribute.html"]
		for pageName in templates:
			self._generatePage(pageName)

		docsDir = os.path.join(self._langDir, "documentation")
		os.mkdir(docsDir)
		documentationTemplatePaths = [
			os.path.join(self._docsTemplatesDir, f)
			for f in os.listdir(self._docsTemplatesDir)
		]
		documentationTemplatePaths.append(self._getUsingOpenTeacher3Path())
		for filename in documentationTemplatePaths:
			self._generateDocumentationPage(filename)

	def _getUsingOpenTeacher3Path(self):
		path = tempfile.mkdtemp()
		#make sure it's cleaned up...
		self._tempPaths.append(path)

		filePath = os.path.join(path, "using-openteacher-3.html")
		html = self._userDocMod.getHtml("../images/docs/3", self._langCode)
		with open(filePath, "w") as f:
			f.write(html.encode("UTF-8"))
		return filePath

	def _getWrappedUserDocumentation(self, lang):
		html = self._userDocMod.getHtml("../images/docs/3", lang)
		return self._userDocWrapperMod.wrap(html)

	def _generateDocumentationPage(self, templatePath):
		"""Combines the documentation text, with the stuff shared
		   between all documentation pages, and wraps the result in a
		   page.

		"""
		#the documentation text
		pageName = "documentation/" + os.path.basename(templatePath)
		docContent = self._evaluateTemplate(templatePath, pageName)

		#the documentation wrapper
		templatePath = os.path.join(self._templatesDir, "docpage.html")
		content = self._evaluateTemplate(templatePath, pageName, docContent=docContent)

		self._writePage(pageName, content)

	def _generatePage(self, pageName):
		"""Gets the content of the page, and writes it into a page."""

		filename = os.path.join(self._templatesDir, pageName)
		content = self._evaluateTemplate(filename, pageName, downloadLinks=DOWNLOAD_LINKS)

		self._writePage(pageName, content)

	def _writePage(self, pageName, content):
		"""Wraps content into a page template and writes the result to
		   disk

		"""
		#write content file (used by ajax)
		with open(os.path.join(self._langDir, os.path.splitext(pageName)[0] + ".contentonly.html"), "w") as f:
			f.write(content.encode("UTF-8"))
		page = self._wrapContent(pageName, content)

		#write html file (used on first page load)
		with open(os.path.join(self._langDir, pageName), "w") as f:
			f.write(page.encode("UTF-8"))

	@property
	def _languages(self, cache={}):
		if not cache:
			translationNames = self._modules.default("active", type="friendlyTranslationNames").friendlyNames

			cache["en"] = translationNames["C"]
			for mofile in glob.glob(self._mm.resourcePath("translations/*.mo")):
				name = os.path.splitext(os.path.basename(mofile))[0]
				cache[name] = translationNames.get(name, name)
		return cache

	def _wrapContent(self, pageName, content):
		"""Wraps content into a page template"""

		filename = os.path.join(self._templatesDir, "base.html")
		templatePath = pageName
		pageName = os.path.splitext(pageName)[0]
		return self._evaluateTemplate(filename, pageName,
			pageName=pageName,
			currentLanguage=self._langCode,
			languages=self._languages,
			content=content,
			downloadLinksJson=json.dumps(DOWNLOAD_LINKS)
		)

	def _evaluateTemplate(self, templatePath, thisPage, **kwargs):
		class EvalPseudoSandbox(pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)
				self2.register("tr", self._tr)
				currentDir = os.path.dirname(thisPage)
				self2.register("url", lambda name: posixpath.relpath(name, currentDir))

		t = pyratemp.Template(filename=templatePath, eval_class=EvalPseudoSandbox)
		return t(**kwargs)

	def enable(self):
		global pyratemp, QtCore, QtGui
		try:
			import pyratemp
			from PyQt4 import QtCore, QtGui
		except ImportError:
			sys.stderr.write("For this developer module to work, you need to have pyratemp & PyQt4 installed.\n")

		self._modules = next(iter(self._mm.mods(type="modules")))
		self._modules.default(type="execute").startRunning.handle(self.generateWebsite)

		metadata = self._modules.default("active", type="metadata").metadata
		self._iconPath = metadata["iconPath"]
		self._hue = metadata["mainColorHue"]
		self._lineColor = self._modules.default("active", type="backgroundImageGenerator").lineColor

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._iconPath
		del self._hue
		del self._lineColor

def init(moduleManager):
	return WebsiteGeneratorModule(moduleManager)
