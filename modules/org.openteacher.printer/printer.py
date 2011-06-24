#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

class Printer(object):
	def __init__(self, module, dataType, lesson, printer, *args, **kwargs):#FIXME: 'printer' creation (as in the argument) should be handled by a separate module.
		super(Printer, self).__init__(*args, **kwargs)

		self.module = module
		self.dataType = dataType
		self.lesson = lesson
		self.printer = printer

	def print_(self):
		self.module.print_(self.dataType, self.lesson.list, self.printer)

	def __str__(self): #FIXME
		return str(self.module)

class PrinterModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(PrinterModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "printer"

##################FIXME: DUPLICATE WITH SAVER.PY!
	def _modulesUpdated(self):
		#Keeps track of all created lessons
		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreated.handle(self._lessonAdded)

	@property
	def _currentLesson(self):
		uiModule = set(self._mm.mods("active", type="ui")).pop()
		try:
			return self._lessons[uiModule.currentFileTab]
		except KeyError:
			return

	def _lessonAdded(self, lesson):
		self._lessons[lesson.fileTab] = lesson
		lesson.stopped.handle(
			lambda: self._removeLesson(lesson.fileTab)
		)

	def _removeLesson(self, fileTab):
		del self._lessons[fileTab]
##################END DUPLICATE

	def print_(self, printer):
		#print
		printers = set()
		try:
			self._currentLesson.list
		except AttributeError:
			raise NotImplementedError()

		dataType = self._currentLesson.module.dataType
		for module in self._mm.mods("active", type="print"):
			if dataType in module.prints:
				printers.add(Printer(module, dataType, self._currentLesson, printer))

		if len(printers) == 0:
			raise NotImplementedError()

		#Choose item
		printer = self._modules.chooseItem(printers)
		#Save
		printer.print_()

	@property
	def printSupport(self):
		#Checks for printer modules, and if there is a gui module for
		#the data type(s) they can provide
		try:
			dataType = self._currentLesson.module.dataType
		except AttributeError:
			return False
		for module in self._mm.mods("active", type="print"):
			if dataType in module.prints:
				return True
		return False

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.modulesUpdated.handle(self._modulesUpdated) #FIXME: DUPLICATE WITH SAVER.PY
		self._lessons = {}
		self.active = True

	def disable(self):
		self._modules.modulesUpdated.unhandle(self._modulesUpdated) #FIXME: DUPLICATE WITH SAVER.PY
		del self._modules
		self.active = False
		del self._lessons

def init(moduleManager):
	return PrinterModule(moduleManager)
