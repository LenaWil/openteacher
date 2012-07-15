#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
#	Copyright 2012, Marten de Vries
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
from PyQt4 import QtCore

import os
import uuid
import urllib2
import copy

try:
	import json
except:
	import simplejson as json

class PropertyLabel(QtGui.QLabel):
	def __init__(self, *args, **kwargs):
		super(PropertyLabel, self).__init__(*args, **kwargs)
		
		self.setAlignment(QtCore.Qt.AlignRight)

class TestsWidget(QtGui.QWidget):
	"""Widget that shows all the tests"""

	testSelected = QtCore.pyqtSignal(dict)
	message = QtCore.pyqtSignal(str)
	def __init__(self, connection, upload, testSelecter, *args, **kwargs):
		super(TestsWidget, self).__init__(*args, **kwargs)
		
		# fixme: create event when test is created so it can be added here
		
		self.connection = connection
		
		# Setup layout
		layout = QtGui.QVBoxLayout()
		
		layout.addWidget(QtGui.QLabel("Tests"))
		
		testSelecter.testChosen.connect(self.testSelected.emit)
		
		layout.addWidget(testSelecter)
		
		addLessonButton = QtGui.QPushButton("Add lesson")
		addLessonButton.clicked.connect(upload)
		
		layout.addWidget(addLessonButton)
		
		self.setLayout(layout)

class PersonAdderWidget(QtGui.QWidget):
	"""The widget you see when you press 'Add student'"""

	back = QtCore.pyqtSignal()
	def __init__(self, connection, info, studentsView, studentsList, *args, **kwargs):
		"""Init parameters:
		    - Connection object (like in the testModeConnection module)
		    - The dictionary representing the test this adds persons for
		    - Students view object (like in the testModeStudentsView module)
		    - Students list object (like an object of the StudentsInTestWidget class here)

		"""
		super(PersonAdderWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.info = info
		self.studentsView = studentsView
		self.studentsInTest = studentsList
		
		layout = QtGui.QVBoxLayout()
		
		label = QtGui.QLabel("Select a student/group:")
		layout.addWidget(label)
		
		layout.addWidget(self.studentsView)
		
		buttonLayout = QtGui.QHBoxLayout()
		
		addButton = QtGui.QPushButton("Add person/group")
		addButton.clicked.connect(self._addPersons)
		buttonLayout.addWidget(addButton)
		
		backButton = QtGui.QPushButton("Back")
		backButton.clicked.connect(self.back.emit)
		buttonLayout.addWidget(backButton)
		
		layout.addLayout(buttonLayout)
		
		self.setLayout(layout)
	
	# Adds the current person or group of the studentsView to the studentsList, but keeps unique
	def _addPersons(self):
		students = self.studentsView.getCurrentStudents()
		
		for student in students:
			# Add to the list (uniquely)
			if len(self.studentsInTest.findItems(student["username"], QtCore.Qt.MatchExactly)) == 0:
				# Add to the remote list
				self.connection.post(self.info["students"], {"student_id":student["id"]})
				
				# Add to the local list
				self.studentsInTest.update()
			else:
				# Student has already been added. Let's not say anything about it.
				pass
		
		self.back.emit()

class StudentsInTestWidget(QtGui.QListWidget):
	"""Widget with the students in a test (second column, middle)"""

	def __init__(self, connection, testInfo, answerChecker, *args, **kwargs):
		super(StudentsInTestWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.testInfo = testInfo
		self.answerChecker = answerChecker
		
		# If an answer in the answersChecker changes, I need to be updated
		self.answerChecker.answersChanged.connect(self.update)
		
		# Widget keeps a local buffer of info
		# list of tests/<id>/students/<id>
		self.studentInTests = []
		# list of users/<id>
		self.studentInfos = []
		
		self.update()
	
	# Initial adding of people to the list
	def update(self):
		# Clear self
		self.clear()
		
		# tests/<id>/students
		self.studentsInTest = self.connection.get(self.testInfo["students"])
		
		# tests/<id>/checked_answers
		checkedAnswers = self.connection.get(self.testInfo["checked_answers"])
		checkedAnswersIds = map(lambda x: int(os.path.basename(x)), checkedAnswers)
		# tests/<id>/answers
		answers = self.connection.get(self.testInfo["answers"])
		answersIds = map(lambda x: int(os.path.basename(x)), answers)
		
		for student in self.studentsInTest:
			studentInTest = self.connection.get(student)
			# Remember this, so the server can rest next time
			self.studentInTests.append(studentInTest)
			
			studentInfo = self.connection.get(studentInTest["student"])
			# Remember this, so the server can rest next time
			self.studentInfos.append(studentInfo)
			
			
			# Set appended text
			appender = "(DNP)"
			# Look if answers have already been checked
			if studentInfo["id"] in checkedAnswersIds:
				checkedAnswers = self.answerChecker.getCheckedAnswer(self.testInfo["id"], studentInfo["id"])
				appender = "(" + str(checkedAnswers["note"]) + ")"
			elif studentInfo["id"] in answersIds:
				appender = "(Handed in)"
			
			self.addItem(studentInfo["username"] + " " + appender)
	
	def getCurrentStudentInTest(self):
		return self.studentInTests[self.currentRow()]

class TestInfoWidget(QtGui.QWidget):
	# Parameter = dictionary as parsed tests/<id>/students/<id>
	takenTestSelected = QtCore.pyqtSignal(dict)
	def __init__(self, connection, info, list, answerChecker, *args, **kwargs):
		super(TestInfoWidget, self).__init__(*args, **kwargs)
		
		layout = QtGui.QVBoxLayout()
		
		fl = QtGui.QFormLayout()
		fl.addRow("Questions:", PropertyLabel(str(len(list["items"]))))
		layout.addLayout(fl)
		
		layout.addWidget(QtGui.QLabel("People in this test:"))
		
		self.studentsInTest = StudentsInTestWidget(connection, info, answerChecker)
		self.studentsInTest.currentItemChanged.connect(self.selectedStudentChanged)
		
		layout.addWidget(self.studentsInTest)
		
		self.addPersonButton = QtGui.QPushButton("Add person")
		layout.addWidget(self.addPersonButton)
		
		self.setLayout(layout)
	
	def selectedStudentChanged(self, current, previous):
		self.takenTestSelected.emit(self.studentsInTest.getCurrentStudentInTest())

class TestActionWidget(QtGui.QStackedWidget):
	# Parameter = dictionary as parsed tests/<id>/students/<id>
	takenTestSelected = QtCore.pyqtSignal(dict)
	def __init__(self, connection, studentsView, info, list, answerChecker, *args, **kwargs):
		super(TestActionWidget, self).__init__(*args, **kwargs)
		
		self.testInfoWidget = TestInfoWidget(connection, info, list, answerChecker)
		self.testInfoWidget.addPersonButton.clicked.connect(self._addPerson)
		
		self.personAdderWidget = PersonAdderWidget(connection, info, studentsView, self.testInfoWidget.studentsInTest)
		self.personAdderWidget.back.connect(self._personAdded)
		
		self.addWidget(self.testInfoWidget)
		self.addWidget(self.personAdderWidget)
		
		self.testInfoWidget.takenTestSelected.connect(self.takenTestSelected.emit)
	
	def _addPerson(self):
		self.setCurrentWidget(self.personAdderWidget)
	
	def _personAdded(self):
		self.setCurrentWidget(self.testInfoWidget)

class TestWidget(QtGui.QWidget):
	"""Widget that shows the currently selected test (second column)"""

	# Parameter = dictionary as parsed tests/<id>/students/<id>
	takenTestSelected = QtCore.pyqtSignal(dict)
	message = QtCore.pyqtSignal(str)
	def __init__(self, connection, info, studentsView, answerChecker, *args, **kwargs):
		super(TestWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.info = info
		self.list = self.info["list"]
		self.answerChecker = answerChecker
		
		layout = QtGui.QVBoxLayout()
		
		layout.addWidget(QtGui.QLabel("Test"))
		
		name = QtGui.QLabel()
		name.setStyleSheet("font-size: 18px;")
		layout.addWidget(name)
		
		testActionWidget = TestActionWidget(connection, studentsView, self.info, self.list, answerChecker)
		testActionWidget.takenTestSelected.connect(self.takenTestSelected.emit)
		
		layout.addWidget(testActionWidget)
		
		self.checkButton = QtGui.QPushButton("(Re)check answers")
		self.checkButton.clicked.connect(self.checkAnswers)
		layout.addWidget(self.checkButton)
		
		self.publishButton = QtGui.QPushButton("(Re)publish answers")
		self.publishButton.clicked.connect(self.publishAnswers)
		
		# If no answers in the test are checked, the publish button should be disabled.
		# Get checked answers for this test
		checkedAnswers = self.connection.get(info["checked_answers"])
		if len(checkedAnswers) == 0:
			self.publishButton.setEnabled(False)
		
		layout.addWidget(self.publishButton)
		
		self.setLayout(layout)
		
		# Fill widget with contents
		name.setText(self.list["title"])
	
	def checkAnswers(self):
		givenAnswers = self.connection.get(self.info["answers"])
		rightAnswers = self.list
		# Check results
		self.answerChecker.checkAnswers(self.info["id"], givenAnswers, rightAnswers)
		# Enable publish button
		self.publishButton.setEnabled(True)
		# Show message
		self.message.emit("Student's answers have been checked!")
	
	def publishAnswers(self):
		# Publish results
		self.answerChecker.publishAnswers(self.info["id"])
		# Show message
		self.message.emit("Student's results have been (re)published!")

class AnswerChecker(QtCore.QObject):
	answersChanged = QtCore.pyqtSignal()
	def __init__(self, connection, testChecker, *args, **kwargs):
		super(AnswerChecker, self).__init__(*args, **kwargs)
		self.connection = connection
		self.testChecker = testChecker
		
		self.results = dict()
	
	def checkAnswers(self, testId, givenAnswersUrls, rightAnswers):
		for givenAnswersUrl in givenAnswersUrls:
			results = []
			givenAnswers = self.connection.get(givenAnswersUrl)
			givenAnswers =  json.loads(givenAnswers["list"])
			
			studentId = int(os.path.basename(givenAnswersUrl))
			
			# Loop over all answers
			for rightAnswer in rightAnswers["items"]:
				results.append(self.testChecker((self.lookupItem(rightAnswer["id"], givenAnswers["items"]))["answer"], rightAnswer))
			
			# Add results to list
			rightAnswers["results"] = results
			
			self.update(testId, {"list": json.dumps(rightAnswers), "note": self.calculateNote(results), "answer_id": studentId}, False)
		
		self.answersChanged.emit()
	
	def update(self, testid, result, emit=True):
		if not testid in self.results:
			self.results[testid] = dict()
		self.results[testid][result["answer_id"]] = result
		
		if emit:
			self.answersChanged.emit()
	
	def getCheckedAnswer(self, testid, studentid):
		# Check if it's already buffered locally
		if testid in self.results and studentid in self.results[testid]:
			return self.results[testid][studentid]
		else:
			# Otherwise, get it
			checkedAnswer = self.connection.get("tests/" + str(testid) + "/checked_answers/" + str(studentid))
			if type(checkedAnswer) == urllib2.HTTPError:
				return None
			result = {"list": checkedAnswer["list"], "note": checkedAnswer["note"], "answer_id": studentid}
			self.update(testid, result, False)
			return result
	
	def correctAnswer(self, testid, studentid, questionid):
		list = json.loads(self.results[testid][studentid]["list"])
		for result in list["results"]:
			if result["itemId"] == questionid:
				result["result"] = "right"
				break
		
		self.update(testid, {"list": json.dumps(list), "note": self.calculateNote(list["results"]), "answer_id": studentid})
	
	def publishAnswers(self, testid):
		for studentResult in self.results[testid].values():
			e = self.connection.post("tests/" + str(testid) + "/checked_answers", studentResult)
			if type(e) == urllib2.HTTPError:
				studentid = studentResult["answer_id"]
				newStudentResult = copy.deepcopy(studentResult)
				del newStudentResult["answer_id"]
				self.connection.put("tests/" + str(testid) + "/checked_answers/" + str(studentid), newStudentResult)
	
	def calculateNote(self, results):
		results = map(lambda x: 1 if x["result"] == "right" else 0, results)
		total = len(results)
		amountRight = sum(results)
		
		return int(float(amountRight) / float(total) * 100)
	
	def lookupItem(self, id, items):
		for item in items:
			if item["id"] == id:
				return item

class TakenTestWidget(QtGui.QWidget):
	"""Widget that shows the currently selected person in a test (third column)"""

	message = QtCore.pyqtSignal(str)
	def __init__(self, connection, studentInTest, compose, answerChecker, *args, **kwargs):
		super(TakenTestWidget, self).__init__(*args, **kwargs)
		
		self.answerChecker = answerChecker
		
		self.studentInTest = studentInTest
		self.student = connection.get(studentInTest["student"])
		self.test = connection.get(studentInTest["test"])
		
		layout = QtGui.QVBoxLayout()
		
		layout.addWidget(QtGui.QLabel("Person"))
			
		name = QtGui.QLabel(self.student["username"])
		name.setStyleSheet("font-size: 18px;")
		layout.addWidget(name)
		
		# Get the checked answers
		self.checkedAnswers = self.answerChecker.getCheckedAnswer(self.test["id"], self.student["id"])
		
		if self.checkedAnswers == None:
			l = QtGui.QLabel("Answers of this student have not been checked yet. Click the \"Check answers\" button in the second column.")
			l.setWordWrap(True)
			l.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
			layout.addWidget(l)
		else:
			list = json.loads(self.checkedAnswers["list"])
			# Add checked answer to the answer checker
			answerChecker.update(self.test["id"], {"list": self.checkedAnswers["list"], "note": self.checkedAnswers["note"], "answer_id": self.student["id"]})
						
			fl = QtGui.QFormLayout()
			self.answersRightLabel = PropertyLabel()
			fl.addRow("Answers right:", self.answersRightLabel)
			self.answersWrongLabel = PropertyLabel()
			fl.addRow("Answers wrong:", self.answersWrongLabel)
			self.markLabel = PropertyLabel()
			fl.addRow("OpenTeacher mark:", self.markLabel)
			layout.addLayout(fl)
			
			self.table = QtGui.QTableWidget(3,3)
			# Fill table
			self.questionIds = []
			for item in list["items"]:
				# Find result
				for result in list["results"]:
					if result["itemId"] == item["id"]:
						itemResult = result
						break
				
				resultWidget = QtGui.QTableWidgetItem()
				if itemResult["result"] == "right":
					resultWidget.setCheckState(QtCore.Qt.Checked)
				else:
					resultWidget.setCheckState(QtCore.Qt.Unchecked)
				resultWidget.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				
				self.table.setItem(len(self.questionIds), 0, resultWidget)
				qItem = QtGui.QTableWidgetItem(compose(item["questions"]))
				qItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.table.setItem(len(self.questionIds), 1, qItem)
				aItem = QtGui.QTableWidgetItem(itemResult["givenAnswer"])
				aItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				self.table.setItem(len(self.questionIds), 2, aItem)
				
				self.questionIds.append(item["id"])
			
			self.table.verticalHeader().setVisible(False)
			self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
			self.table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
			self.table.resizeRowsToContents()
			
			self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
			self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
			
			self.table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem(""))
			self.table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("Question"))
			self.table.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("Given answer"))
			self.table.cellClicked.connect(self.questionSelected)
			
			layout.addWidget(self.table)
			
			self.correctButton = QtGui.QPushButton("Correct")
			self.correctButton.setEnabled(False)
			self.correctButton.clicked.connect(self.correctAnswer)
			
			layout.addWidget(self.correctButton)
			
			self.finalMarkLabel = PropertyLabel()
			self.finalMarkLabel.setStyleSheet("font-size: 18px;")
			
			fm = QtGui.QFormLayout()
			fm.addRow("Final mark:", self.finalMarkLabel)
			layout.addLayout(fm)
			
			self.fillLabels()
		
		self.setLayout(layout)
	
	def fillLabels(self):
		checkedAnswer = self.answerChecker.getCheckedAnswer(self.test["id"], self.student["id"])
		list = json.loads(checkedAnswer["list"])
		results = map(lambda x: 1 if x["result"] == "right" else 0, list["results"])
		
		answersRight = sum(results)
		answersWrong = len(list["results"]) - answersRight
		note = checkedAnswer["note"]
		
		self.answersRightLabel.setText(str(answersRight))
		self.answersWrongLabel.setText(str(answersWrong))
		self.markLabel.setText(str(note))
		self.finalMarkLabel.setText(str(note))
	
	def questionSelected(self, row, column):
		if self.table.item(row, 0).text() == "X":
			self.correctButton.setEnabled(True)
		else:
			self.correctButton.setEnabled(False)
	
	def correctAnswer(self):
		resultWidget = QtGui.QTableWidgetItem("O")
		resultWidget.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
		
		self.answerChecker.correctAnswer(self.test["id"], self.student["id"], self.questionIds[self.table.currentRow()])
		
		self.table.setItem(self.table.currentRow(), 0, resultWidget)
		
		# Update labels
		self.fillLabels()

class TeacherPanel(QtGui.QSplitter):
	message = QtCore.pyqtSignal(str)
	def __init__(self, connection, studentsView, testSelecter, uploaderModule, answerChecker, compose, *args, **kwargs):
		super(TeacherPanel, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.testSelecter = testSelecter
		self.compose = compose
		self.answerChecker = answerChecker
		
		# Add tests layoutumn
		self.testsWidget = TestsWidget(connection, uploaderModule, testSelecter)
		self.testsWidget.testSelected.connect(lambda testInfo: self.addTestlayoutumn(testInfo, studentsView, self.answerChecker))
		self.testsWidget.message.connect(self.message.emit)
		
		self.addWidget(self.testsWidget)
		self.addWidget(QtGui.QWidget())
	
	def addTestlayoutumn(self, testInfo, studentsView, answerChecker):
		testWidget = TestWidget(self.connection, testInfo, studentsView, answerChecker)
		testWidget.takenTestSelected.connect(self.addTakenTestlayoutumn)
		testWidget.message.connect(self.message.emit)
		
		try:
			self.widget(1).setParent(None)
		except AttributeError:
			pass
		self.insertWidget(1, testWidget)
	
	def addTakenTestlayoutumn(self, studentInTest):
		takenTestWidget = TakenTestWidget(self.connection, studentInTest, self.compose, self.answerChecker)
		takenTestWidget.message.connect(self.message.emit)
		
		try:
			self.widget(2).setParent(None)
		except AttributeError:
			pass
		self.insertWidget(2, takenTestWidget)
		
class TestModeTeacherPanelModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeTeacherPanelModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "testModeTeacherPanel"
		self.priorities = {
			"student@home": -1,
			"student@school": 492,
			"teacher": 492,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": 492,
			"codedocumentation": 492,
			"all": 492,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="ui"),
			self._mm.mods(type="testMenu"),
			self._mm.mods(type="testModeUploader"),
			self._mm.mods(type="testModeStudentsView"),
			self._mm.mods(type="testModeConnection"),
			self._mm.mods(type="wordsStringComposer"),
			self._mm.mods(type="dialogShower"),
		)
		self.filesWithTranslations = ("teacherPanel.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		#setup translation
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
		
		self._testMenu = self._modules.default("active", type="testMenu").menu

		self._action = self._testMenu.addAction(self.priorities["all"])
		self._action.triggered.handle(self.showPanel)
		self._action.text = _("Teacher panel") #FIXME: retranslate...

		self.dialogShower = self._modules.default("active", type="dialogShower")
		
		self.active = True

	def disable(self):
		self.active = False

		self._action.remove()

		del self._testMenu
		del self._action
		del self.dialogShower
	
	def showPanel(self):
		# First, login
		self.connection = self._modules.default("active", type="testModeConnection").getConnection()
		self.connection.loggedIn.handle(self.showPanel_)
		self.loginid = uuid.uuid4()
		self.connection.login(self.loginid)
	
	def showPanel_(self, loginid):
		# Check if this is indeed from the request I sent out
		if loginid == self.loginid:
			uiModule = self._modules.default("active", type="ui")
			
			studentsView = self._modules.default("active", type="testModeStudentsView").getStudentsView()
			upload = self._modules.default("active", type="testModeUploader").upload
			testSelecter = self._modules.default("active", type="testModeTestSelecter").getTestSelecter()
			testChecker = self._modules.default("active", type="wordsStringChecker").check
			compose = self._modules.default("active", type="wordsStringComposer").compose
			# Create an answer checker
			answerChecker = AnswerChecker(self.connection, testChecker)
			
			self.teacherPanel = TeacherPanel(self.connection, studentsView, testSelecter, upload, answerChecker, compose)
			
			self.tab = uiModule.addCustomTab(self.teacherPanel)
			self.tab.title = _("Teacher Panel") #FIXME: retranslate etc.
			self.tab.closeRequested.handle(self.tab.close)
			
			self.teacherPanel.message.connect(self.showMessage)
	
	def showMessage(self, text):
		self.dialogShower.showMessage.send(self.tab, text)

def init(moduleManager):
	return TestModeTeacherPanelModule(moduleManager)
