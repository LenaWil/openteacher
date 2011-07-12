#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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

from PyQt4 import QtGui

class TeachWidget(QtGui.QStackedWidget):
	def __init__(self, keyboardWidget, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)

		self.settingsWidget = TeachSettingsWidget()
		self.lessonWidget = TeachLessonWidget(keyboardWidget)

		self.addWidget(self.settingsWidget)
		self.addWidget(self.lessonWidget)

class TeachSettingsWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(TeachSettingsWidget, self).__init__(*args, **kwargs)

		self.lessonTypeComboBox = QtGui.QComboBox()

		#Word modifiers
		self.modifyWordListView = QtGui.QListView()
		self.modifyWordUpButton = QtGui.QPushButton(_("Up"))
		self.modifyWordDownButton = QtGui.QPushButton(_("Down"))

		modifyWordButtonsLayout = QtGui.QVBoxLayout()
		modifyWordButtonsLayout.addStretch()
		modifyWordButtonsLayout.addWidget(self.modifyWordUpButton)
		modifyWordButtonsLayout.addWidget(self.modifyWordDownButton)
		modifyWordButtonsLayout.addStretch()
		modifyWordLayout = QtGui.QHBoxLayout()
		modifyWordLayout.addWidget(self.modifyWordListView)
		modifyWordLayout.addLayout(modifyWordButtonsLayout)

		#Word list modifiers
		self.modifyWordListListView = QtGui.QListView()
		self.modifyWordListUpButton = QtGui.QPushButton(_("Up"))
		self.modifyWordListDownButton = QtGui.QPushButton(_("Down"))

		modifyWordListButtonsLayout = QtGui.QVBoxLayout()
		modifyWordListButtonsLayout.addStretch()
		modifyWordListButtonsLayout.addWidget(self.modifyWordListUpButton)
		modifyWordListButtonsLayout.addWidget(self.modifyWordListDownButton)
		modifyWordListButtonsLayout.addStretch()
		modifyWordListLayout = QtGui.QHBoxLayout()
		modifyWordListLayout.addWidget(self.modifyWordListListView)
		modifyWordListLayout.addLayout(modifyWordListButtonsLayout)
		
		self.dontShowAgainCheckBox = QtGui.QCheckBox(
			_("Don't show this screen again when I start a lesson.")
		)
		self.startLessonButton = QtGui.QPushButton(
			_("I'm ready, start the lesson!")
		)

		gb = QtGui.QGroupBox()
		gb.setTitle(_("Lesson settings"))
		formLayout = QtGui.QFormLayout()
		formLayout.addRow(_("Lesson type"), self.lessonTypeComboBox)
		formLayout.addRow(_("Modify word"), modifyWordLayout)
		formLayout.addRow(_("Modify word list"), modifyWordListLayout)
		formLayout.addRow("", self.dontShowAgainCheckBox)
		formLayout.addRow("", self.startLessonButton)

		gb.setLayout(formLayout)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(gb)
		self.setLayout(mainLayout)

class TeachLessonWidget(QtGui.QSplitter):
	def __init__(self, keyboardWidget, *args, **kwargs):
		super(TeachLessonWidget, self).__init__(*args, **kwargs)

		self.changeSettingsButton = QtGui.QPushButton(
			_("Change lesson settings")
		)
		wordLabel = QtGui.QLabel(_("Word:"))
		self.questionLabel = QtGui.QLabel()
		self.questionLabel.setWordWrap(True)
		if keyboardWidget is not None:
			self.keyboardWidget = keyboardWidget
		self.teachTabWidget = QtGui.QTabWidget()
		self.progressBar = QtGui.QProgressBar()

		leftLayout = QtGui.QVBoxLayout()
		leftLayout.addWidget(wordLabel)
		leftLayout.addWidget(self.questionLabel)
		leftLayout.addStretch()
		leftLayout.addWidget(self.teachTabWidget)
		leftLayout.addWidget(self.progressBar)

		leftWidget = QtGui.QWidget()
		leftWidget.setLayout(leftLayout)
		
		rightLayout = QtGui.QVBoxLayout()
		try:
			rightLayout.addWidget(self.keyboardWidget)
		except AttributeError:
			pass
		rightLayout.addWidget(self.changeSettingsButton)
		
		rightWidget = QtGui.QWidget()
		rightWidget.setLayout(rightLayout)

		self.addWidget(leftWidget)
		self.addWidget(rightWidget)
