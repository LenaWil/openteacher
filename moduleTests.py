#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012-2013, Marten de Vries
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

import moduleManager
import unittest
import openteacher
import json
import copy

class ModulesTest(unittest.TestCase):
	def setUp(self):
		self._mm = moduleManager.ModuleManager(openteacher.MODULES_PATH)

	def _enableIncludingDependencies(self, mod, minimalDependencies):
		enabledMods = []
		if getattr(mod, "active", False):
			return True, enabledMods

		for selector in getattr(mod, "requires", []):
			success = False
			for requirement in selector:
				subSuccess, otherMods = self._enableIncludingDependencies(requirement, minimalDependencies)
				enabledMods.extend(otherMods)
				if subSuccess:
					success = True
					if minimalDependencies:
						#dependencies met for this selector, stop trying
						break
			if not success:
				#dependencies couldn't be satisfied
				return False, enabledMods

		if not minimalDependencies:
			for selector in getattr(mod, "uses", []):
				for requirement in selector:
					success, otherMods = self._enableIncludingDependencies(requirement, minimalDependencies)
					enabledMods.extend(otherMods)

		#enable
		try:
			print "enabling ", mod.__class__.__file__
			mod.enable()
		except AttributeError:
			pass
		enabledMods.append(mod)
		return getattr(mod, "active", False), enabledMods

	def _disableDependencyTree(self, mods):
		for mod in reversed(mods):
			try:
				print "disabling", mod.__class__.__file__
				mod.disable()
			except AttributeError:
				pass

	def _fakeExecuteModule(self):
		#initialize settings (normally they're used by the execute
		#module)
		next(iter(self._mm.mods(type="settings"))).initialize()

		#inject an alternative execute module into the module system,
		#because we can't use the real one. (Every module capable of
		#doing that registers at startRunning.)
		class ExecuteMod(object):
			type = "execute"
			active = True
			startRunning = next(iter(self._mm.mods(type="event"))).createEvent()
			__file__ = "modules/org/openteacher/execute/execute.py"
		self._mm._modules.remove(next(iter(self._mm.mods(type="execute"))))
		self._mm._modules.add(ExecuteMod())
		#Set a profile. The execute module does that normally.
		next(iter(self._mm.mods(type="modules"))).profile = "default"

	def testMinimalDependencies(self):
		self._fakeExecuteModule()

		for mod in self._mm.mods:
			success, enabledMods = self._enableIncludingDependencies(mod, True)
			self._disableDependencyTree(enabledMods)
			print ""

	def testWithFullDependencies(self):
		self._fakeExecuteModule()

		for mod in self._mm.mods:
			success, enabledMods = self._enableIncludingDependencies(mod, False)
			self._disableDependencyTree(enabledMods)
			print ""

if __name__ == "__main__":
	#since this mod doesn't respect the 'uses' behaviour completely,
	#fix a possible conflict between gui and qtApp.
	from PyQt4 import QtGui
	app = QtGui.QApplication([])

	unittest.main()
