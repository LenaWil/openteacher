#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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
import inspect
import time

class ModulesModule(object):
	_lowestPriority = 10000

	def __init__(self, moduleManager, *args, **kwargs):
		super(ModulesModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "modules"
		self.requires = (
			self._mm.mods(type="event"),
		)

	@property
	def profile(self):
		return self.default("active", type="profile").name
	
	def _getPriority(self, mod):
		try:
			return mod.priorities[self._profile]
		except (AttributeError, KeyError):
			#return a negative priority to the sort algorithm so the
			#module gets on top of the list. The negative integer
			#needs to be a number, that makes sure the last
			#installed module is on the top of the list. This just
			#uses seconds since installation.
			path = mod.__class__.__file__
			return - int(os.path.getmtime(path))
	
	def sort(self, *args, **kwargs):
		mods = set(self._mm.mods(*args, **kwargs))
		return sorted(mods, key=self._getPriority)

	def default(self, *args, **kwargs):
		"""Raises IndexError if no modules remain after filtering with
		   the arguments

		"""
		mods = set(self._mm.mods(*args, **kwargs))
		try:
			return min(mods, key=self._getPriority)
		except ValueError:
			raise IndexError()

	#Enabling/disabling modules
	def _hasPositivePriority(self, mod):
		try:
			return mod.priorities[self._modules.profile] >= 0
		except AttributeError:
			return True #If no priorities-stuff, just enable

	def updateToProfile(self):
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
		
		#enable modules
		for mod in reversed(sorted_tree):
			try:
				active = mod.active
			except AttributeError:
				active = False
			if self._hasPositivePriority(mod) and not active:
				depsactive = True
				if hasattr(mod, "requires"):
					for dep in mod.requires:
						depsactive = len(filter(
							lambda x: not hasattr(x, "active") or bool(getattr(x, "active")),
							dep
						)) != 0
						if not depsactive:
							break
				if hasattr(mod, "enable") and depsactive:
					mod.enable()
		
		#disable modules
		for mod in sorted_tree:
			try:
				active = mod.active
			except AttributeError:
				active = False
			if not self._hasPositivePriority(mod) and active:
				depsactive = True
				if hasattr(mod, "requires"):
					for dep in mod.requires:
						depsactive = len(filter(
							lambda x: not hasattr(x, "active") or bool(getattr(x, "active")),
							dep
						)) != 0
						if not depsactive:
							break
				if hasattr(mod, "disable") and depsactive:
					mod.disable()

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return ModulesModule(moduleManager)
