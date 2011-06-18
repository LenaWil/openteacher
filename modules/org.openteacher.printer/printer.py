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
	def __init__(self, module, type, lesson, printer, *args, **kwargs):#FIXME: 'printer' creation (as in the argument) should be handled by a separate module.
		super(Printer, self).__init__(*args, **kwargs)

		self.module = module
		self.type = type
		self.lesson = lesson
		self.printer = printer

	def print_(self):
		self.module.print_(self.type, self.lesson.list, self.printer)

	def __str__(self): #FIXME
		return str(self.module)

class PrinterModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(PrinterModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("printer",)
		self.requires = (1, 0)
		self.active = False

##################FIXME: DUPLICATE WITH SAVER.PY!
	def _modulesUpdated(self):
		#Keeps track of all created lessons
		for module in self._mm.activeMods.supporting("lesson"):
			module.lessonCreated.handle(self._lessonAdded)

	@property
	def _currentLesson(self):
		uiModule = self._mm.activeMods.supporting("ui").items.pop() #FIXME
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
		uiModule = self._mm.activeMods.supporting("ui").items.pop() #FIXME

		#print
		printers = set()
		if self._currentLesson.module not in self._mm.mods.supporting("list"):
			raise NotImplementedError()

		type = self._currentLesson.module.type
		for module in self._mm.activeMods.supporting("print"):
			if type in module.prints:
				printers.add(Printer(module, type, self._currentLesson, printer))

		if len(printers) == 0:
			raise NotImplementedError()

		#Choose item
		printer = uiModule.chooseItem(printers)
		#Save
		printer.print_()

	@property
	def printSupport(self):
		#Checks for printer modules, and if there is a gui module for
		#the type(s) they can provide
		try:
			type = self._currentLesson.module.type
		except AttributeError:
			return False
		for module in self._mm.activeMods.supporting("print"):
			if type in module.prints:
				return True
		return False

	def enable(self):
		for module in self._mm.activeMods.supporting("modules"): #FIXME: DUPLICATE WITH SAVER.PY
			module.modulesUpdated.handle(self._modulesUpdated)
		self._lessons = {}
		self.active = True

	def disable(self):
		for module in self._mm.activeMods.supporting("modules"): #FIXME: DUPLICATE WITH SAVER.PY
			module.modulesUpdated.unhandle(self._modulesUpdated)
		self.active = False
		del self._lessons

def init(moduleManager):
	return PrinterModule(moduleManager)
