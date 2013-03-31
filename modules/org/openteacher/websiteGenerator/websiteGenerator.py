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
import shutil

DOWNLOAD_LINK = "http://sourceforge.net/projects/openteacher/files/openteacher/3.1/openteacher-3.1-windows-setup.msi/download"

class WebsiteGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebsiteGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "websiteGenerator"

		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="ui"),
			self._mm.mods(type="metadata"),
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
		copy("index.php")

	def _generateResources(self):
		"""Generates a few resources."""

		toPath = lambda part: os.path.join(self._path, part)
		fromPath = lambda part: self._mm.resourcePath(os.path.join("images/oslogos/", part))

		self._generateStyle(toPath("style.css"))
		self._generateBackground(toPath("images/bg.png"))
		self._generateBodyBackground(toPath("images/body.png"))
		self._generateLight(toPath("images/light.png"))
		self._generateButtons([
			(fromPath("fedoralogo.png"), toPath("images/downloadbuttons/fedora-button")),
			(fromPath("tuxlogo.png"), toPath("images/downloadbuttons/linux-button")),
			(fromPath("osxlogo.png"), toPath("images/downloadbuttons/osx-button")),
			(fromPath("ubulogo.png"), toPath("images/downloadbuttons/ubuntu-button")),
			(fromPath("winlogo.png"), toPath("images/downloadbuttons/windows-button")),
		])

	def _generateStyle(self, path):
		t = pyratemp.Template(filename=self._mm.resourcePath("style.css"))
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

	def _generateBackground(self, path):
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

	def _generateBodyBackground(self, path):
		width = 1000
		height = 5000
		sideMargin = 27
		topMargin = 64

		textColor = QtGui.QColor.fromHsv(self._hue, 119, 47)
		gradientTopColor = QtGui.QColor.fromHsv(self._hue, 7, 253)
		gradientBottomColor = QtGui.QColor.fromHsv(self._hue, 12, 243)

		xRadius = 9
		yRadius = xRadius * 0.7
		topLineY = 94

		logoTopX = 6
		logoSize = 107

		textXStart = 124
		textYBaseline = 58

		img = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32_Premultiplied)
		img.fill(QtCore.Qt.transparent)

		gradient = QtGui.QLinearGradient(0, 0, 0, height)
		gradient.setColorAt(0, gradientTopColor)
		gradient.setColorAt(1, gradientBottomColor)

		font = QtGui.QFont("Verdana", 37)
		font.setWeight(55)
		font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 95)

		smallFont = QtGui.QFont(font)
		smallFont.setPointSize(smallFont.pointSize() - 8)

		painter = QtGui.QPainter(img)
		painter.setPen(self._lineColor)
		painter.setBrush(gradient)
		painter.drawRoundedRect(
			sideMargin,
			topMargin,
			width - sideMargin * 2,
			height,
			xRadius,
			yRadius
		)
		painter.drawLine(
			sideMargin,
			topLineY,
			width - sideMargin,
			topLineY
		)
		painter.drawImage(
			QtCore.QPoint(logoTopX, 0),
			QtGui.QImage(self._logo).scaledToHeight(logoSize, QtCore.Qt.SmoothTransformation)
		)

		textPen = QtGui.QColor(textColor)
		textPen.setAlpha(200)
		painter.setPen(textPen)
		painter.setFont(font)
		textXPos = textXStart
		painter.drawText(textXPos, textYBaseline, "O")
		textXPos += QtGui.QFontMetrics(font).width("O")
		painter.setFont(smallFont)
		painter.drawText(textXPos, textYBaseline, "PEN")
		textXPos += QtGui.QFontMetrics(smallFont).width("PEN")
		painter.setFont(font)
		painter.drawText(textXPos, textYBaseline, "T")
		textXPos += QtGui.QFontMetrics(font).width("T")
		painter.setFont(smallFont)
		painter.drawText(textXPos, textYBaseline, "EACHER")
		painter.end()

		img.save(path)

	def _generateLight(self, path):
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

	def _generateButtons(self, logoAndOutputNames):
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
			for moname in os.listdir(self._mm.resourcePath('translations')):
				if not moname.endswith('.mo'):
					continue
				langCode = os.path.splitext(moname)[0]

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
		templatePath = pageName
		pageName = os.path.splitext(pageName)[0]
		return self._evaluateTemplate(filename, pageName, pageName=pageName, content=content)

	def _evaluateTemplate(self, templatePath, thisPage, **kwargs):
		class EvalPseudoSandbox(pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)
				self2.register("tr", self._tr)
				currentDir = os.path.dirname(thisPage)
				self2.register("url", lambda name: os.path.relpath(name, currentDir))

		t = pyratemp.Template(filename=templatePath, eval_class=EvalPseudoSandbox)
		return t(**kwargs).encode("UTF-8")

	def enable(self):
		global pyratemp, QtCore, QtGui
		try:
			import pyratemp
			from PyQt4 import QtCore, QtGui
		except ImportError:
			sys.stderr.write("For this developer module to work, you need to have pyratemp & PyQt4 installed.\n")

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self.generateWebsite)

		metadata = self._modules.default("active", type="metadata").metadata
		self._hue = metadata["mainColorHue"]
		self._lineColor = QtGui.QColor.fromHsv(self._hue, 28, 186)
		self._logo = metadata["iconPath"]

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._hue
		del self._lineColor
		del self._logo

def init(moduleManager):
	return WebsiteGeneratorModule(moduleManager)
