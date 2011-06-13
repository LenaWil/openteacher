#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2008-2011, Milan Boers
#    Copyright 2009-2011, Marten de Vries
#    Copyright 2008, Roel Huybrechts
#    Copyright 2010-2011, Cas Widdershoven
#    Copyright 2010, David D. Lowe
#
#    This file is part of OpenTeacher.
#
#    OpenTeacher is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenTeacher is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtWebKit

import os
import time
import mimetypes

class Result(str):
	def __init__(self, *args, **kwargs):
		super(Result, self).__init__(*args, **kwargs)
		
		self.itemId = int()
		
		#optional
		self.active = list()

class List(object):
	def __init__(self, *args, **kwargs):
		super(List, self).__init__(*args, **kwargs)
		
		self.words = []
		self.tests = []

class Picture():
	def __init__(self,filename,hints = "",desc = ""):
		self.name = os.path.splitext(os.path.basename(str(filename)))[0]
		self.filename = filename
		self.hints = hints
		self.desc = desc

class EnterPictureListModel(QtCore.QAbstractListModel):
	def __init__(self,pictures,parent=None,*args):
		QtCore.QAbstractListModel.__init__(self,parent,*args)
		
		self.listdata = []
		
		for picture in pictures.words:
			self.listdata.append(picture.name)
	
	def update(self,pictures):
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
		
		self.listdata = []
		
		for picture in pictures.words:
			self.listdata.append(picture.name)
		
		self.endInsertRows()
	
	def rowCount(self,parent=QtCore.QModelIndex()):
		return len(self.listdata)

	def data(self,index,role):
		if index.isValid() and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.listdata[index.row()])
		else:
			return QtCore.QVariant()
	
	def textAtIndex(self,index):
		return self.listdata[index]

class EnterPictureList(QtGui.QListView):
	def __init__(self,parent):
		QtGui.QListView.__init__(self,parent)
		self.parent = parent
		
		self.lm = EnterPictureListModel(parent.items,self)
		self.setModel(self.lm)
	
	def update(self):
		self.lm.update(base.enterWidget.items)
	
	def selectionChanged(self,current,previous):
		current = self.lm.textAtIndex(self.selectedIndexes()[0].row())
		
		for picture in base.enterWidget.items.words:
			if picture.name == current:
				self.parent.setActivePicture(picture)

class MediaDisplay(QtWebKit.QWebView):
	def __init__(self,autoplay,*args, **kwargs):
		super(MediaDisplay, self).__init__(*args, **kwargs)
		self.autoplay = autoplay
		
	def showMedia(self, path):
		type = mimetypes.guess_type(str(path))[0].split('/')[0]
		
		if type == 'video':
			self._showVideo(path)
		elif type == 'image':
			self._showPicture(path)
		elif type == 'audio':
			self._showAudio(path)
	
	def _showPicture(self, path):
		self.setUrl(QtCore.QUrl(path))
		
	def _showVideo(self, path):
		addition = ''
		if self.autoplay:
			addition = ' autoplay="autoplay"'
		self.setHtml('''
		<html>
		<head>
		<title>OpenTeacher Video Preview</title>
		</head>
		<body style="margin: 0">
		<video id="videoTag" src="''' + path + '''" controls="controls" ''' + addition + ''' />
		<script type="text/javascript">
		var elem = document.getElementById("videoTag");
		function setVideoDimensions() {
			elem.style.width = window.innerWidth;
			elem.style.height = window.innerHeight;
		}
		window.onresize = setVideoDimensions;
		setVideoDimensions()
		</script>
		</body>
		</html>
		''')
	
	def _showAudio(self, path):
		addition = ''
		if self.autoplay:
			addition = ' autoplay="autoplay"'
		self.setHtml('''
		<html>
		<head>
		<title>OpenTeacher Audio Preview</title>
		</head>
		<body style="margin: 0">
		<audio id="videoTag" src="''' + path + '''" controls="controls" ''' + addition + ''' />
		<script type="text/javascript">
		var elem = document.getElementById("videoTag");
		function setVideoDimensions() {
			elem.style.width = window.innerWidth;
		}
		window.onresize = setVideoDimensions;
		setVideoDimensions()
		</script>
		</body>
		</html>
		''')
	
	def clear(self):
		self.setHtml('''
		<html><head><title>Nothing</title></head><body></body></html>
		''')

class EnterWidget(QtGui.QSplitter):
	def __init__(self,*args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self.items = List()
		
		self.enterpicturelist = EnterPictureList(self)
		
		removeButton = QtGui.QPushButton("Remove")
		removeButton.clicked.connect(self.removePicture)
		addButton = QtGui.QPushButton("Add")
		addButton.clicked.connect(self.addPictures)
		
		leftBottom = QtGui.QHBoxLayout()
		leftBottom.addWidget(removeButton)
		leftBottom.addWidget(addButton)
		
		left = QtGui.QVBoxLayout()
		left.addWidget(self.enterpicturelist)
		left.addLayout(leftBottom)
		leftW = QtGui.QWidget()
		leftW.setLayout(left)
		
		self.enterpreview = MediaDisplay(False)
		
		self.entername = QtGui.QLineEdit()
		self.entername.textChanged.connect(self.changeName)
		self.entername.setEnabled(False)
		
		nameL = QtGui.QHBoxLayout()
		nameL.addWidget(QtGui.QLabel("Name:"))
		nameL.addWidget(self.entername)
		
		descl = QtGui.QLabel("Description:")
		
		self.enterdesc = QtGui.QTextEdit()
		self.enterdesc.textChanged.connect(self.changeDesc)
		self.enterdesc.setEnabled(False)
		
		desceditL = QtGui.QVBoxLayout()
		desceditL.addLayout(nameL)
		desceditL.addWidget(descl)
		desceditL.addWidget(self.enterdesc)
		
		desceditW = QtGui.QWidget()
		desceditW.setLayout(desceditL)
		
		rightSplitter = QtGui.QSplitter(2)
		rightSplitter.addWidget(self.enterpreview)
		rightSplitter.addWidget(desceditW)
		
		right = QtGui.QVBoxLayout()
		right.addWidget(rightSplitter)
		rightW = QtGui.QWidget()
		rightW.setLayout(right)
		
		splitter = QtGui.QSplitter(self)
		splitter.addWidget(leftW)
		splitter.addWidget(rightW)
		
		layout = QtGui.QHBoxLayout()
		layout.addWidget(splitter)
		
		self.setLayout(layout)
	
	def addPictures(self):
		filenames = QtGui.QFileDialog.getOpenFileNames(self,"Select file(s)",QtCore.QDir.homePath(),"Media (*.bmp *.jpg *.jpeg *.png *.wmv *.mp3)")
		for filename in filenames:
			self.addPicture(filename)
	
	def addPicture(self,filename):
		picture = Picture(filename)
		self.items.words.append(picture)
		self.enterpicturelist.update()
	
	def removePicture(self):
		items.words.remove(self.activepicture)
		self.enterpicturelist.update()
		self.enterpreview.clear()
		self.entername.setText("")
		self.entername.setEnabled(False)
		self.enterdesc.setText("")
		self.enterdesc.setEnabled(False)
	
	def setActivePicture(self,picture):
		self.activepicture = picture
		self.entername.setEnabled(True)
		self.entername.setText(picture.name)
		self.enterdesc.setEnabled(True)
		self.enterdesc.setText(picture.desc)
		self.enterpreview.showMedia(picture.filename)
	
	def changeName(self):
		self.activepicture.name = self.entername.text()
		self.enterpicturelist.update()
		
	def changeDesc(self):
		self.activepicture.desc = self.enterdesc.toPlainText()
	
	def showEvent(self, event):
		if base.inlesson:
			warningD = QtGui.QMessageBox()
			warningD.setIcon(QtGui.QMessageBox.Warning)
			warningD.setWindowTitle("Warning")
			warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
			warningD.setText("Are you sure you want to go back to the teach tab? This will end your lesson!")
			feedback = warningD.exec_()
			if feedback == QtGui.QMessageBox.Ok:
				base.teachWidget.stopLesson()
			else:
				base.api.setCurrentTab(self.parent.teachWidget)
				return

class LessonTypeChooser(QtGui.QComboBox):
	def __init__(self):
		QtGui.QComboBox.__init__(self)
		
		self.currentIndexChanged.connect(self.changeLessonType)
		
		self._lessonTypeModules = list(
			base.api.mods.supporting("lessonType")
		)
		
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)
	
	def currentLessonType(self):
		for lessontype in self._lessonTypeModules:
			if lessontype.name == self.currentText():
				return lessontype
		
	def changeLessonType(self, index):
		try:
			base.teachWidget.initiateLesson()
		except AttributeError:
			pass

class MediaLesson(object):
	def __init__(self,items):
		#stop media playing in the enter widget
		base.enterWidget.enterpreview.clear()
		
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType().createLessonType(items,range(len(items.words)))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.endLesson)
		
		self.lessonType.start()
		
		#set the progress bar
		base.teachWidget.progress.setMinimum(0)
		base.teachWidget.progress.setMaximum(self.lessonType.totalItems)
		base.teachWidget.progress.setValue(0)
	
	def checkAnswer(self):
		if self.currentItem.name == base.teachWidget.answerfield.text():
			# Answer was right
			self.lessonType.setResult(Result("right"))
			# Progress bar
			base.teachWidget.progress.setValue(self.lessonType.askedItems)
		else:
			# Answer was wrong
			self.lessonType.setResult(Result("wrong"))
			
	
	def nextQuestion(self, item):
		#set the next question
		self.currentItem = item
		#set the mediawidget to the right location
		base.teachWidget.mediaDisplay.showMedia(self.currentItem.filename)
	
	def endLesson(self):
		# FIXME : message with results
		# stop media
		base.teachWidget.mediaDisplay.clear()
		# return to enter tab
		base.fileTab.currentTab = base.enterWidget

class TeachWidget(QtGui.QWidget):
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		#draw the GUI
		
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel("Lesson type:")
		self.lessonTypeChooser = LessonTypeChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		self.mediaDisplay = MediaDisplay(True)
		
		self.answerfield = QtGui.QLineEdit()
		self.answerfield.returnPressed.connect(self.checkAnswerButtonClick)
		checkButton = QtGui.QPushButton("Check")
		checkButton.clicked.connect(self.checkAnswerButtonClick)
		self.progress = QtGui.QProgressBar()
		
		bottomL = QtGui.QHBoxLayout()
		bottomL.addWidget(self.answerfield)
		bottomL.addWidget(checkButton)
		bottomL.addWidget(self.progress)
		
		layout = QtGui.QVBoxLayout()
		layout.addLayout(top)
		layout.addWidget(self.mediaDisplay)
		layout.addLayout(bottomL)
		
		self.setLayout(layout)
	
	def initiateLesson(self):
		self.lesson = MediaLesson(base.enterWidget.items)
		self.answerfield.setFocus()
	
	def stopLesson(self):
		self.lesson.endLesson(False)
		del self.lesson
	
	def checkAnswerButtonClick(self):
		self.lesson.checkAnswer()
		self.answerfield.clear()
		self.answerfield.setFocus()
	
	def showEvent(self,event):
		self.initiateLesson()

class MediaLessonModule(object):
	def __init__(self, api):
		global base
		base = self
		self.api = api
		self.counter = 1
		# is the lesson going on?
		self.inlesson = False
		
		self.supports = ("lesson", "list", "loadList", "initializing")
		self.requires = (1, 0)
	
	def initialize(self):
		for module in self.api.activeMods.supporting("settings"):
			module.registerModule("Media Lesson", self)
	
	def enable(self):
		self.type = "Items"
		
		self.lessonCreated = self.api.createEvent()
		
		for module in self.api.mods.supporting("ui"):
			event = module.addLessonCreateButton("Create media lesson")
			event.handle(self.createLesson)
		
		self.active = True

	def disable(self):
		del self.type
		self.active = False

	def close(self):
		print "Closed!"
	
	def createLesson(self):		
		lessons = set()
		
		for module in self.api.activeMods.supporting("ui"):
			self.enterWidget = EnterWidget()
			self.teachWidget = TeachWidget()
			
			self.fileTab = module.addFileTab(
				"Media lesson %s" % self.counter,
				self.enterWidget,
				self.teachWidget
			)
			
			lesson = Lesson(self, self.fileTab, self.enterWidget, self.teachWidget)
			self.lessonCreated.emit(lesson)
			
			lessons.add(lesson)
		self.counter += 1
		return lessons

class Lesson(object):
	def __init__(self, moduleManager, fileTab, enterWidget, teachWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		self.fileTab = fileTab
		self.stopped = base.api.createEvent()
		
		fileTab.closeRequested.handle(self.stop)
	
	def stop(self):
		self.fileTab.close()
		self.stopped.emit()

def init(moduleManager):
	return MediaLessonModule(moduleManager)