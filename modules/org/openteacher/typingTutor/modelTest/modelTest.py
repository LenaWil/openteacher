#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import unittest

class TestCase(unittest.TestCase):
	@property
	def models(self):
		return [m.model for m in self._mm.mods("active", type="typingTutorModel")]

	def setUp(self):
		for m in self.models:
			m.registerUser("_modeltest")

	def tearDown(self):
		for m in self.models:
			m.deregisterUser("_modeltest")

	def testRegisterUnregisterErrors(self):
		for m in self.models:
			with self.assertRaises(m.UsernameEmptyError):
				m.registerUser("")
			with self.assertRaises(m.UsernameTakenError):
				m.registerUser("_modeltest", "COLEMAK_LAYOUT")
			m.deregisterUser("_modeltest")
			with self.assertRaises(KeyError):
				m.deregisterUser("_modeltest")
			#for tearDown
			m.registerUser("_modeltest")

	def testUsernames(self):
		for m in self.models:
			self.assertIn("_modeltest", m.usernames)

	def testSession(self):
		"""This test has some lines commented out which can be very
		   useful while debugging.

		"""
		argList = [
			None,
			("_modeltest", 20, 0),
			("_modeltest", 10, 3),
			("_modeltest", 30, 2),
			None,
			("_modeltest", 10, 0),
		]
		for i in range(50):
			argList.append(("_modeltest", 10, 0))
		argList.append(None)
		argList.append(("_modeltest", 5, 3))
		argList.append(None)
		for i in range(10):
			argList.append(("_modeltest", 5, 0))

		for m in self.models:
			for i, args in enumerate(argList):
				if args:
					m.setResult(*args)
				#the first iteration, no test results are known yet.
				if i == 0:
					with self.assertRaises(IndexError):
						m.amountOfMistakes("_modeltest")
				else:
					self.assertIsInstance(m.amountOfMistakes("_modeltest"), int)

				instruction = m.currentInstruction("_modeltest")
				if self._showInfo:
					print "INSTRUCTION:", instruction
				self.assertIsInstance(instruction, basestring)
				self.assertTrue(instruction)

				exercise = m.currentExercise("_modeltest")
				if self._showInfo:
					print "NEW EXERCISE:", exercise
				self.assertIsInstance(exercise, basestring)
				self.assertTrue(exercise)

				self.assertEqual(m.layout("_modeltest"), m.QWERTY_LAYOUT)

				level = m.level("_modeltest")
				if self._showInfo:
					print "LEVEL:", level
				self.assertIsInstance(level, int)
				self.assertTrue(level >= 0)

				maxLevel = m.maxLevel("_modeltest")
				self.assertIsInstance(maxLevel, int)
				self.assertTrue(maxLevel >= 0)

				if i == 0:
					with self.assertRaises(IndexError):
						m.speed("_modeltest")
				else:
					speed = m.speed("_modeltest")
					if self._showInfo:
						print "SPEED PREVIOUS EXERCISE: %s wpm" % speed
					self.assertIsInstance(speed, int)
					self.assertTrue(speed >= 0)

				targetSpeed = m.targetSpeed("_modeltest")
				self.assertIsInstance(targetSpeed, int)
				self.assertTrue(targetSpeed >= 0)

				if self._showInfo:
					print ""

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "test"
		self.requires = (
			self._mm.mods(type="typingTutorModel"),
		)

	def enable(self):
		self.TestCase = TestCase
		#you can temporily activate this to get debugging info.
		self.TestCase._showInfo = False
		self.TestCase._mm = self._mm
		self.active = True

	def disable(self):
		self.active = False
		del self.TestCase

def init(moduleManager):
	return TestModule(moduleManager)
