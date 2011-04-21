#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2010-2011, Marten de Vries
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

class AboutTextLabel(QtGui.QLabel):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutTextLabel, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager

		textPath = self._mm.resourcePath(__file__, "about.html")
		pyratemp = self._mm.import_(__file__, "pyratemp")

		slogan = _("OpenTeacher helps you learn a foreign language vocabulary.")
		firstLine, secondLine = self._splitLineCloseToMiddle(unicode(slogan))

		t = pyratemp.Template(open(textPath).read())
		data = {
			"version": "3.x",
			"first_line": firstLine,
			"second_line": secondLine,
			"copyright_years": "2008-2011",
			"openteacher_authors": _("OpenTeacher authors"),
			"project_website_link": "http://openteacher.org/",
			"project_website": _("Project website")	
		}
		self.setText(t(**data))
		
		self.setOpenExternalLinks(True)
		self.setAlignment(QtCore.Qt.AlignCenter)

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
		
		path = self._mm.resourcePath(__file__, "OTcomic.png")
		self.setPixmap(QtGui.QPixmap(path))

		self.setAlignment(QtCore.Qt.AlignCenter)

class AboutWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutWidget, self).__init__(*args, **kwargs)
		
		self.imageLabel = AboutImageLabel(moduleManager)
		self.textLabel = AboutTextLabel(moduleManager)
		
		self.layout = QtGui.QVBoxLayout()
		self.layout.addStretch()
		self.layout.addWidget(self.imageLabel)
		self.layout.addStretch()
		self.layout.addWidget(self.textLabel)
		self.layout.addStretch()
		self.setLayout(self.layout)

class ShortLicenseWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShortLicenseWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		shortLicensePath = self._mm.resourcePath(__file__, "short_license.txt")

		label = QtGui.QLabel()
		label.setText(open(shortLicensePath).read())
		self.fullLicenseButton = QtGui.QPushButton(_("Full license text"))

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(label)
		vbox.addWidget(self.fullLicenseButton)
		
		self.layout = QtGui.QHBoxLayout()
		self.layout.addStretch()
		self.layout.addLayout(vbox)
		self.layout.addStretch()
		self.setLayout(self.layout)

class LongLicenseWidget(QtGui.QTextEdit):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LongLicenseWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		longLicensePath = self._mm.resourcePath(__file__, "long_license.txt")

		self.setReadOnly(True)
		self.setText(open(longLicensePath).read())

class LicenseWidget(QtGui.QStackedWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LicenseWidget, self).__init__(*args, **kwargs)

		self.shortLicenseWidget = ShortLicenseWidget(moduleManager)
		self.longLicenseWidget = LongLicenseWidget(moduleManager)

		self.shortLicenseWidget.fullLicenseButton.clicked.connect(self.showFullLicense)

		self.addWidget(self.shortLicenseWidget)
		self.addWidget(self.longLicenseWidget)

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
			self.backupAuthors = authors[:]
			self.authors = authors[:]
			random.shuffle(self.authors)

		self.personWidget = PersonWidget()
		launchpadLabel = QtGui.QLabel(_("Thanks to all Launchpad contributors!"))
		launchpadLabel.setAlignment(QtCore.Qt.AlignCenter)

		self.layout = QtGui.QVBoxLayout()
		self.layout.addWidget(self.personWidget)
		self.layout.addStretch()
		self.layout.addWidget(launchpadLabel)
		self.setLayout(self.layout)

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

		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)

		self.aboutWidget = AboutWidget(moduleManager)
		self.licenseWidget = LicenseWidget(moduleManager)
		self.authorsWidget = AuthorsWidget(authors)

		self.addTab(self.aboutWidget, _("About")) #FIXME: own translation (also the others down here)
		self.addTab(self.licenseWidget, _("License"))
		self.addTab(self.authorsWidget, _("Authors"))
		
		self.setWindowTitle(_("About"))

		self.currentChanged.connect(self.startAnimation)

	def startAnimation(self):
		if self.currentWidget() == self.authorsWidget:
			self.authorsWidget.startAnimation()
