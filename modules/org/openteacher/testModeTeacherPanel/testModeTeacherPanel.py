#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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

try:
	import json
except:
	import simplejson as json

class PropertyLabel(QtGui.QLabel):
	def __init__(self, *args, **kwargs):
		super(PropertyLabel, self).__init__(*args, **kwargs)
		
		self.setAlignment(QtCore.Qt.AlignRight)

"""
Widget that shows all the tests
"""
class TestsWidget(QtGui.QWidget):
	testSelected = QtCore.pyqtSignal(dict)
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

"""
The widget you see when you press "Add student"
"""
class PersonAdderWidget(QtGui.QWidget):
	"""
	Init parameters:
	- Connection object (like in the testModeConnection module)
	- The dictionary representing the test this adds persons for
	- Students view object (like in the testModeStudentsView module)
	- Students list object (like an object of the StudentsInTestWidget class here)
	"""
	back = QtCore.pyqtSignal()
	def __init__(self, connection, info, studentsView, studentsList, *args, **kwargs):
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
		addButton.clicked.connect(self._addPersonGroup)
		buttonLayout.addWidget(addButton)
		
		backButton = QtGui.QPushButton("Back")
		backButton.clicked.connect(self.back.emit)
		buttonLayout.addWidget(backButton)
		
		layout.addLayout(buttonLayout)
		
		self.setLayout(layout)
	
	# Adds the current person or group of the studentsView to the studentsList, but keeps unique
	def _addPersonGroup(self):
		student = self.studentsView.getCurrentStudent()
		# fixme: make adding groups possible
		
		# Add to the list (uniquely)
		if len(self.studentsInTest.findItems(student["username"], QtCore.Qt.MatchExactly)) == 0:
			# Add to the remote list
			self.connection.post(self.info["students"], {"student_id":student["id"]})
			
			# Add to the local list
			self.studentsInTest.addItem(student["username"])
		else:
			pass
			#fixme: give nice message
		
		self.back.emit()

"""
Widget with the students in a test
"""
class StudentsInTestWidget(QtGui.QListWidget):
	def __init__(self, connection, studentsList, *args, **kwargs):
		super(StudentsInTestWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		# tests/<id>/students
		self.studentsInTest = studentsList
		# list of tests/<id>/students/<id>
		self.studentInTests = []
		# list of users/<id>
		self.studentInfos = []
		
		self._addPeopleToListWidget()
	
	# Initial adding of people to the list
	def _addPeopleToListWidget(self):
		for student in self.studentsInTest:
			#fixme: add students to the combobox
			studentInTest = self.connection.get(student)
			# Remember this, so the server can rest next time
			self.studentInTests.append(studentInTest)
			
			studentInfo = self.connection.get(studentInTest["student"])
			# Remember this, so the server can rest next time
			self.studentInfos.append(studentInfo)
			
			self.addItem(studentInfo["username"])
	
	def getCurrentStudentInTest(self):
		index = 0
		for studentInfo in self.studentInfos:
			studentInTest = self.studentInTests[index]
			if studentInfo["username"] == self.currentItem().text():
				return studentInTest
			index += 1

class TestInfoWidget(QtGui.QWidget):
	# Parameter = dictionary as parsed tests/<id>/students/<id>
	takenTestSelected = QtCore.pyqtSignal(dict)
	def __init__(self, connection, info, list, *args, **kwargs):
		super(TestInfoWidget, self).__init__(*args, **kwargs)
		
		layout = QtGui.QVBoxLayout()
		
		fl = QtGui.QFormLayout()
		fl.addRow("Questions:", PropertyLabel(str(len(list["items"]))))
		#fl.addRow("Questions:", PropertyLabel("20"))
		#fl.addRow("Mark calculation:", PropertyLabel("UNSET"))
		#fl.addRow("Published:", PropertyLabel("UNSET"))
		#fl.addRow("Deadline:", PropertyLabel("UNSET"))
		#fl.addRow("Avarage mark:", PropertyLabel("6.8"))
		layout.addLayout(fl)
		
		layout.addWidget(QtGui.QLabel("People in this test:"))
		
		studentsList = connection.get(info["students"])
		self.studentsInTest = StudentsInTestWidget(connection, studentsList)
		self.studentsInTest.currentItemChanged.connect(self.selectedStudentChanged)
		
		layout.addWidget(self.studentsInTest)
		
		self.addPersonButton = QtGui.QPushButton("Add person")
		layout.addWidget(self.addPersonButton)
		
		self.setLayout(layout)
	
	def selectedStudentChanged(self, current, previous):
		# fixme: emit takenTestSelected
		self.takenTestSelected.emit(self.studentsInTest.getCurrentStudentInTest())

class TestActionWidget(QtGui.QStackedWidget):
	# Parameter = dictionary as parsed tests/<id>/students/<id>
	takenTestSelected = QtCore.pyqtSignal(dict)
	def __init__(self, connection, studentsView, info, list, *args, **kwargs):
		super(TestActionWidget, self).__init__(*args, **kwargs)
		
		self.testInfoWidget = TestInfoWidget(connection, info, list)
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

"""
Widget that shows the currently selected test (second column)
"""
class TestWidget(QtGui.QWidget):
	# Parameter = dictionary as parsed tests/<id>/students/<id>
	takenTestSelected = QtCore.pyqtSignal(dict)
	def __init__(self, connection, info, studentsView, *args, **kwargs):
		super(TestWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.info = info
		self.list = self.info["list"]
		
		layout = QtGui.QVBoxLayout()
		
		layout.addWidget(QtGui.QLabel("Test"))
		
		name = QtGui.QLabel()
		name.setStyleSheet("font-size: 18px;")
		layout.addWidget(name)
		
		testActionWidget = TestActionWidget(connection, studentsView, self.info, self.list)
		testActionWidget.takenTestSelected.connect(self.takenTestSelected.emit)
		layout.addWidget(testActionWidget)
		
		publishButton = QtGui.QPushButton("Publish answers and results")
		layout.addWidget(publishButton)
		
		self.setLayout(layout)
		
		# Fill widget with contents
		name.setText(self.list["title"])

"""
Widget that shows the currently selected person in a test (third column)
"""
class TakenTestWidget(QtGui.QWidget):
	def __init__(self, connection, studentInTest, *args, **kwargs):
		super(TakenTestWidget, self).__init__(*args, **kwargs)
		
		self.studentInTest = studentInTest
		self.student = connection.get(studentInTest["student"])
		self.test = connection.get(studentInTest["test"])
		
		layout = QtGui.QVBoxLayout()
		
		layout.addWidget(QtGui.QLabel("Person"))
		
		name = QtGui.QLabel(self.student["username"])
		name.setStyleSheet("font-size: 18px;")
		layout.addWidget(name)
		
		fl = QtGui.QFormLayout()
		fl.addRow("Answers right:", PropertyLabel("14"))
		fl.addRow("Answers wrong:", PropertyLabel("6"))
		fl.addRow("OpenTeacher mark:", PropertyLabel("7.0"))
		fl.addRow("Handed in at:", PropertyLabel("11/11/11 11:53"))
		layout.addLayout(fl)
		
		table = QtGui.QTableWidget(3,3)
		table.setItem(0, 0, QtGui.QTableWidgetItem("O"))
		table.setItem(0, 1, QtGui.QTableWidgetItem("een"))
		table.setItem(0, 2, QtGui.QTableWidgetItem("one"))
		table.setItem(1, 0, QtGui.QTableWidgetItem("X"))
		table.setItem(1, 1, QtGui.QTableWidgetItem("twee"))
		table.setItem(1, 2, QtGui.QTableWidgetItem("twoo"))
		table.setItem(2, 0, QtGui.QTableWidgetItem("O"))
		table.setItem(2, 1, QtGui.QTableWidgetItem("drie"))
		table.setItem(2, 2, QtGui.QTableWidgetItem("three"))
		
		table.verticalHeader().setVisible(False)
		table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		table.resizeRowsToContents()
		
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		
		table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem(""))
		table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("Question"))
		table.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("Given answer"))
		
		layout.addWidget(table)
		
		layout.addWidget(QtGui.QPushButton("Correct"))
		
		mark = PropertyLabel("7.0")
		mark.setStyleSheet("font-size: 18px;")
		
		fm = QtGui.QFormLayout()
		fm.addRow("Final mark:", mark)
		layout.addLayout(fm)
		
		self.setLayout(layout)

class TeacherPanel(QtGui.QSplitter):
	def __init__(self, connection, studentsView, testSelecter, uploaderModule, *args, **kwargs):
		super(TeacherPanel, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.testSelecter = testSelecter
		
		# Add tests layoutumn
		self.testsWidget = TestsWidget(connection, uploaderModule, testSelecter)
		self.testsWidget.testSelected.connect(lambda testInfo: self.addTestlayoutumn(testInfo, studentsView))
		
		self.addWidget(self.testsWidget)
		self.addWidget(QtGui.QWidget())
	
	def addTestlayoutumn(self, testInfo, studentsView):
		testWidget = TestWidget(self.connection, testInfo, studentsView)
		testWidget.takenTestSelected.connect(self.addTakenTestlayoutumn)
		
		try:
			self.widget(1).setParent(None)
		except AttributeError:
			pass
		self.insertWidget(1, testWidget)
	
	def addTakenTestlayoutumn(self, studentInTest):
		takenTestWidget = TakenTestWidget(self.connection, studentInTest)
		
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
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="ui"),
			self._mm.mods(type="testModeUploader"),
			self._mm.mods(type="testModeStudentsView"),
			self._mm.mods(type="testModeConnection"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		
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
		
		# FIXME: make menu option
		module = self._modules.default("active", type="ui")
		event = module.addLessonCreateButton(_("Teacher panel"))
		event.handle(self.showPanel)
		
		self.active = True

	def disable(self):
		self.active = False
	
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
			
			self.teacherPanel = TeacherPanel(self.connection, studentsView, testSelecter, upload)
			
			tab = uiModule.addCustomTab(_("Teacher Panel"), self.teacherPanel)
			tab.closeRequested.handle(tab.close)

def init(moduleManager):
	return TestModeTeacherPanelModule(moduleManager)