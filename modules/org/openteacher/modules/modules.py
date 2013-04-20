#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2013, Marten de Vries
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

import os

class ModulesModule(object):
	"""This module has two purposes:
	   1) selecting modules via its default() and sort() methods.
	   2) updating OT to self.profile (which should be set by a module
	      other than this one, normally the execute module, before this
	      module should be used by any module.)

	   Lowest (positive) priority: 1000
	"""

	def __init__(self, moduleManager, *args, **kwargs):
		super(ModulesModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "modules"
		self.requires = (
			self._mm.mods(type="event"),
		)

	def _getPriority(self, mod):
		try:
			return mod.priorities[self.profile]
		except (AttributeError, KeyError):
			try:
				return mod.priorities["default"]
			except (AttributeError, KeyError):
				#return a negative priority to the sort algorithm so the
				#module gets on top of the list. The negative integer
				#needs to be a number, that makes sure the last
				#installed module is on the top of the list. This just
				#uses seconds since installation.
				path = mod.__class__.__file__
				return - int(os.path.getmtime(path))

	def sort(self, *args, **kwargs):
		"""Sorts the modules returned by self._mm.mods(*args, **kwargs)
		   based on their priority in the current profile.

		"""
		mods = set(self._mm.mods(*args, **kwargs))
		return sorted(mods, key=self._getPriority)

	def default(self, *args, **kwargs):
		"""Selects one of the modules returned by
		   self._mm.mods(*args, **kwargs) based on their priority and
		   the current profile OT's running in.

		   Raises IndexError if no modules remain after filtering with
		   the arguments.

		"""
		mods = self._mm.mods(*args, **kwargs)
		try:
			return min(mods, key=self._getPriority)
		except ValueError:
			raise IndexError()

	#Enabling/disabling modules
	def _hasPositivePriority(self, mod):
		try:
			return mod.priorities[self.profile] >= 0
		except (AttributeError, KeyError):
			try:
				return mod.priorities["default"] >= 0
			except (AttributeError, KeyError):
				return True #If no priorities-stuff, just enable

	def updateToProfile(self):
		"""Enable()s and disable()s modules until only modules that have
		   a positive priority in the current profile remain. This takes
		   into account dependencies: if a module depends on one that
		   can't be enabled due to its priority in the current profile,
		   that module isn't enabled either.

		"""
		#build dependency tree by topological sorting
		#http://en.wikipedia.org/wiki/Topological_sort ; second algorithm

		self._filterCache = {}
		self._sorted_tree = []
		self._visited_mods = set()
		self._allMods = set(self._mm.mods)

		mods_without_dependencies = set(
			mod
			for mod in self._allMods
			if not (
				getattr(mod, "requires", None) and
				getattr(mod, "uses", None)
			)
		)

		for mod in mods_without_dependencies:
			self._visit(mod)

		self._enableModules()
		self._disableModules()

		del self._filterCache
		del self._sorted_tree
		del self._visited_mods
		del self._allMods

	def _visit(self, mod):
		if mod not in self._visited_mods:
			self._visited_mods.add(mod)
			for dep_mod in self._allMods:
				for requirement in self._depFor("requires", dep_mod):
					if mod in requirement:
						self._visit(dep_mod)
				for used in self._depFor("uses", dep_mod):
					if mod in used:
						self._visit(dep_mod)
			self._sorted_tree.append(mod)

	def _depFor(self, type, mod):
		attribute = getattr(mod, type, ())
		try:
			dep = self._filterCache[attribute]
		except KeyError:
			dep = self._filterCache[attribute] = set(
				frozenset(dep) for dep in attribute
			)
		return dep

	def _enableModules(self):
		#enable modules
		for mod in reversed(self._sorted_tree):
			active = getattr(mod, "active", False) #False -> default
			if not active and self._hasPositivePriority(mod):
				depsactive = True
				for dep in getattr(mod, "requires", []):
					depsactive = len([
						x for x in dep if getattr(x, "active", False)
					]) != 0
					if not depsactive:
						break
				if hasattr(mod, "enable") and depsactive:
					mod.enable()

	def _disableModules(self):
		#disable modules
		for mod in self._sorted_tree:
			active = getattr(mod, "active", False) #False -> default
			if active and not self._hasPositivePriority(mod):
				depsactive = True
				for dep in getattr(mod, "requires", []):
					depsactive = len([
						x for x in dep if getattr(x, "active", False)
					]) != 0
					if not depsactive:
						break
				if hasattr(mod, "disable") and depsactive:
					mod.disable()

def init(moduleManager):
	return ModulesModule(moduleManager)
