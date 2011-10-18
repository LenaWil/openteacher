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

class ModulesActivatorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ModulesActivatorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "modulesActivator"

	def _hasPositivePriority(self, mod):
		try:
			return mod.priorities[self._modules.profile] >= 0 #FIXME: profile property?
		except AttributeError:
			return True #If no priorities-stuff, just enable

	def _inactiveModsFor(self, selector):
		mods = set(selector)
		activeMods = set(self._mm.mods("active"))
		return mods - activeMods

	def _activateModule(self, mod, fail=True):
		#only mods that fit the profile	
		if not self._hasPositivePriority(mod):
			return
		#and that aren't enabled already
		if hasattr(mod, "active") and mod.active:
			return
		#enable all requirements
		if hasattr(mod, "requires"):
			#run through all requirement selectors
			for selector in mod.requires:
				#they can have different forms, this gets the corresponding ModuleFilterer object
				requiredMods = self._inactiveModsFor(selector)

				#really activate them
				for requiredMod in requiredMods:
					self._activateModule(requiredMod, True)

				#check if the requirements are satisfied now, if not, raise an error
				if len(set(selector)) == 0:
					if fail:
						raise NotImplementedError("Mod %s's requirements couldn't be satisfied." % mod)
					else:
						return

		#also enable the mods the module can use (but doesn't need)
		if hasattr(mod, "uses"):
			for selector in mod.uses:
				usableMods = self._inactiveModsFor(selector)
				for usableMod in usableMods:
					try:
						self._activateModule(usableMod, False)
					except NotImplementedError:
						continue

		#enable the module itself. enable() an obligatory function, so
		#test for it.
		if hasattr(mod, "enable"):
			mod.enable()

	def activateModules(self):
		for module in sorted(self._mm.mods):
			try:
				self._activateModule(module)
			except NotImplementedError:
				continue

def init(moduleManager):
	return ModulesActivatorModule(moduleManager)
