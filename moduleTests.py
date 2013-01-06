#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import moduleManager
import unittest
import openteacher
import json

class ModulesTest(unittest.TestCase):
	def setUp(self):
		self._mm = moduleManager.ModuleManager(openteacher.MODULES_PATH)

	def testEnablingAndDisabling(self):
		next(iter(self._mm.mods(type="settings"))).initialize()
		#inject an alternative execute module into the module system,
		#because we can't use the real one.
		class ExecuteMod(object):
			type = "execute"
			active = True
			startRunning = next(iter(self._mm.mods(type="event"))).createEvent()
			__file__ = "modules/org/openteacher/execute/execute.py"
		self._mm._modules.remove(next(iter(self._mm.mods(type="execute"))))
		self._mm._modules.add(ExecuteMod())
		next(iter(self._mm.mods(type="modules"))).profile = "default"

		#FIXME: shared with modules.py. By refactoring that module a
		#little bit it should be possible to call the needed code there.
		#Or maybe move it into a separate module. (Topological sort).

		#build dependency tree by topological sorting
		#http://en.wikipedia.org/wiki/Topological_sort ; second algorithm

		filterCache = {}
		def depFor(type, mod):
			attribute = getattr(mod, type)
			try:
				return filterCache[attribute]
			except KeyError:
				filterCache[attribute] = frozenset(
					(frozenset(dep) for dep in attribute
				))
				return filterCache[attribute]

		sorted_tree = []
		visited_mods = set()

		def visit(mod):
			if mod not in visited_mods:
				visited_mods.add(mod)
				for dep_mod in self._mm.mods:
					if hasattr(dep_mod, "requires"):
						for requirement in depFor("requires", dep_mod):
							if mod in requirement:
								visit(dep_mod)
					if hasattr(dep_mod, "uses"):
						for used in depFor("uses", dep_mod):
							if mod in used:
								visit(dep_mod)
				sorted_tree.append(mod)

		mods_without_dependencies = set()
		for mod in self._mm.mods:
			if not (hasattr(mod, "requires") and mod.requires and hasattr(mod, "uses") and mod.uses):
				mods_without_dependencies.add(mod)

		for mod in mods_without_dependencies:
			visit(mod)
		#END DUPLICATE CODE.

		startStates = {}
		for mod in reversed(sorted_tree):
			#active is meant to vary
			startStates[mod] = set(dir(mod)) - set(["active"])

			#FIXME: DUPLICATE CODE (modules.py)
			depsactive = True
			if hasattr(mod, "requires"):
				for dep in mod.requires:
					depsactive = len(filter(
						lambda x: getattr(x, "active", False),
						dep
					)) != 0
					if not depsactive:
						break
			if hasattr(mod, "enable") and depsactive:
				mod.enable()
			#END_DUPLICATE_CODE

		brokenMods = []
		for mod in sorted_tree:
			#False default is the same as in the modules module.
			if hasattr(mod, "disable") and getattr(mod, "active", False):
				mod.disable()
			#active is meant to vary
			endState = set(dir(mod)) - set(["active"])
			try:
				self.assertEqual(startStates[mod], endState)
			except AssertionError, e:
				brokenMods.append((mod.__class__.__file__, str(e)))
		self.assertFalse(brokenMods, msg=json.dumps(brokenMods, indent=4))

if __name__ == "__main__":
	unittest.main()
