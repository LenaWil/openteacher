#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2008-2011, Roel Huybrechts
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

from PyQt4 import QtCore, QtGui
import random
import gettext
import weakref

class AboutTextLabel(QtGui.QLabel):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutTextLabel, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager

		self.setOpenExternalLinks(True)
		self.setAlignment(QtCore.Qt.AlignCenter)

	def retranslate(self):
		textPath = self._mm.resourcePath("about.html")
		pyratemp = self._mm.import_("pyratemp")

		for module in self._mm.mods("active", "name", type="metadata"):#FIXME and others
			name = module.name

		for module in self._mm.mods("active", "slogan", type="metadata"):
			firstLine, secondLine = self._splitLineCloseToMiddle(module.slogan)

		for module in self._mm.mods("active", "version", type="metadata"):
			version = module.version

		for module in self._mm.mods("active", "website", type="metadata"):
			website = module.website

		t = pyratemp.Template(open(textPath).read())
		data = {
			"name": name,
			"version": version,
			"first_line": firstLine,
			"second_line": secondLine,
			"copyright_years": "2008-2011", #FIXME: get from authors? Or from metadata?
			"openteacher_authors": _("OpenTeacher authors"), #FIXME: see above
			"project_website_link": website,
			"project_website": _("Project website")
		}
		self.setText(t(**data))

	def _splitLineCloseToMiddle(self, line):
		"""Used to split the slogan at the space closest to the middle of it."""

		#determine the middle and find the closest spaces
		middle = len(line) /2
		distanceFromLeft = line[:middle].find(" ")
		distanceFromRight = line[middle:].find(" ")

		#Check if spaces were found
		if distanceFromLeft == -1 and distanceFromRight == -1:
			return (line, "")
		elif distanceFromLeft == -1:
			pos = middle + distanceFromRight
			return (line[:pos], line[pos:])
		elif distanceFromRight == -1:
			pos = middle - distanceFromLeft
			return (line[:pos], line[pos:])
		else:
			#left is closest
			if distanceFromLeft < distanceFromRight:
				pos = middle - distanceFromLeft
				return (line[:pos], line[pos:])
			#right is closest
			else:
				pos = middle + distanceFromRight
				return (line[:pos], line[pos:])

class AboutImageLabel(QtGui.QLabel):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutImageLabel, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		for module in self._mm.mods("active", "comicPath", type="metadata"):
			self.setPixmap(QtGui.QPixmap(module.comicPath))

		self.setAlignment(QtCore.Qt.AlignCenter)

class AboutWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutWidget, self).__init__(*args, **kwargs)

		imageLabel = AboutImageLabel(moduleManager)#FIXME: translatable?
		self.textLabel = AboutTextLabel(moduleManager)

		layout = QtGui.QVBoxLayout()
		layout.addStretch()
		layout.addWidget(imageLabel)
		layout.addStretch()
		layout.addWidget(self.textLabel)
		layout.addStretch()
		self.setLayout(layout)

	def retranslate(self):
		self.textLabel.retranslate()

class ShortLicenseWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShortLicenseWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		for module in self._mm.mods("active", "licenseIntro", type="metadata"):#FIXME: and others near here
			shortLicense = module.licenseIntro

		label = QtGui.QLabel()
		label.setText(shortLicense)
		self.fullLicenseButton = QtGui.QPushButton()

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(label)
		vbox.addWidget(self.fullLicenseButton)
		
		self.layout = QtGui.QHBoxLayout()
		self.layout.addStretch()
		self.layout.addLayout(vbox)
		self.layout.addStretch()
		self.setLayout(self.layout)

	def retranslate(self):
		self.fullLicenseButton.setText(_("Full license text"))

class LongLicenseWidget(QtGui.QTextEdit):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LongLicenseWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		for module in self._mm.mods("active", "license", type="metadata"):
			longLicense = module.license

		self.setReadOnly(True)
		self.setText(longLicense)

class LicenseWidget(QtGui.QStackedWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LicenseWidget, self).__init__(*args, **kwargs)

		self.shortLicenseWidget = ShortLicenseWidget(moduleManager)
		self.longLicenseWidget = LongLicenseWidget(moduleManager)

		self.shortLicenseWidget.fullLicenseButton.clicked.connect(self.showFullLicense)

		self.addWidget(self.shortLicenseWidget)
		self.addWidget(self.longLicenseWidget)

	def retranslate(self):
		self.shortLicenseWidget.retranslate()

	def showFullLicense(self):
		self.setCurrentIndex(1) #longLicenseWidget

class PersonWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(PersonWidget, self).__init__(*args, **kwargs)

		self.taskLabel = QtGui.QLabel("")
		self.taskLabel.setStyleSheet("font-size:24pt;")
		self.nameLabel = QtGui.QLabel("")
		self.nameLabel.setStyleSheet("font-size:36pt;")

		palette = QtGui.QPalette()
		color = palette.windowText().color()
		color.setAlpha(0)
		palette.setColor(QtGui.QPalette.WindowText, color)

		self.taskLabel.setPalette(palette)
		self.nameLabel.setPalette(palette)

		self.taskLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.nameLabel.setAlignment(QtCore.Qt.AlignCenter)

		self.layout = QtGui.QVBoxLayout()
		self.layout.addWidget(self.taskLabel)
		self.layout.addStretch()
		self.layout.addWidget(self.nameLabel)
		self.setLayout(self.layout)

	def update(self, task, name):
		self.taskLabel.setText(task)
		self.nameLabel.setText(name)

	def fade(self, step):
		if step <= 255:
			alpha = step
		elif step > 765:
			alpha = 1020 - step
		else:
			return

		palette = QtGui.QPalette()
		color = palette.windowText().color()
		color.setAlpha(alpha)
		palette.setColor(QtGui.QPalette.WindowText, color)

		self.taskLabel.setPalette(palette)
		self.nameLabel.setPalette(palette)

class AuthorsWidget(QtGui.QWidget):
	def __init__(self, authors, *args, **kwargs):
		super(AuthorsWidget, self).__init__(*args, **kwargs)
		
		if len(authors) == 0:
			self.authors = None
		else:
			self.backupAuthors = list(authors)
			self.authors = []

		self.personWidget = PersonWidget()
		self.launchpadLabel = QtGui.QLabel()
		self.launchpadLabel.setAlignment(QtCore.Qt.AlignCenter)

		self.layout = QtGui.QVBoxLayout()
		self.layout.addWidget(self.personWidget)
		self.layout.addStretch()
		self.layout.addWidget(self.launchpadLabel)
		self.setLayout(self.layout)

	def retranslate(self):
		self.launchpadLabel.setText(
			_("Thanks to all Launchpad contributors!")
		)

	def startAnimation(self):
		self.nextAuthor()
		self.timeLine = QtCore.QTimeLine(8000)
		#4x 255; 2x for the alpha gradients, 2x for a pause
		self.timeLine.setFrameRange(0, 1020)
		self.timeLine.frameChanged.connect(self.personWidget.fade)
		self.timeLine.finished.connect(self.startAnimation)
		self.timeLine.start()

	def nextAuthor(self):
		if self.authors is None:
			return
		try:
			self.personWidget.update(*self.authors.pop())
		except IndexError:
			self.authors = self.backupAuthors[:]
			random.shuffle(self.authors)
			self.nextAuthor()

class AboutDialog(QtGui.QTabWidget):
	def __init__(self, authors, moduleManager, *args, **kwargs):
		super(AboutDialog, self).__init__(*args, **kwargs)

		self._mm = moduleManager

		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)

		self.aboutWidget = AboutWidget(self._mm)
		self.licenseWidget = LicenseWidget(self._mm)
		self.authorsWidget = AuthorsWidget(authors)

		self.addTab(self.aboutWidget, "")
		self.addTab(self.licenseWidget, "")
		self.addTab(self.authorsWidget, "")

		self.currentChanged.connect(self.startAnimation)

	def retranslate(self):
		self.setWindowTitle(_("About"))
		self.setTabText(0, _("About"))
		self.setTabText(1, _("License"))
		self.setTabText(2, _("Authors"))

		self.aboutWidget.retranslate()
		self.licenseWidget.retranslate()
		self.authorsWidget.retranslate()

	def startAnimation(self):
		if self.currentWidget() == self.authorsWidget:
			self.authorsWidget.startAnimation()

class AboutModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "about"

		self.requires = (
			self._mm.mods(type="ui"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="authors"),
		)

	def show(self):
		try:
			module = self._modules.default("active", type="authors")
		except IndexError:
			authors = set()
		else:
			authors = module.registeredAuthors
		dialog = AboutDialog(authors, self._mm)
		tab = self._modules.default("active", type="ui").addCustomTab(
			dialog.windowTitle(),
			dialog
		)
		tab.closeRequested.handle(tab.close)

		dialog.retranslate()
		self._activeDialogs.add(weakref.ref(dialog))

	def _retranslate(self):
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		for dialog in self._activeDialogs:
			r = dialog()
			if r is not None:
				r.retranslate()

		self.name = _("About module")

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self._activeDialogs = set()

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._activeDialogs
		del self.name

def init(moduleManager):
	return AboutModule(moduleManager)
