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

	def _modsFor(self, selector):
		try:
			return self._mm.mods(*selector[0], **selector[1])
		except IndexError:
			return self._mm.mods(**selector[0])

	def _modsWithTypeOf(self, selector):#FIXME: better name
		try:
			return self._mm.mods(**selector[1])
		except IndexError:
			return self._mm.mods(**selector[0])

	def _inactiveModsFor(self, selector):
		mods = set(self._modsWithTypeOf(selector))
		activeMods = set(self._mm.mods("active"))
		return mods - activeMods

	def _activateModule(self, mod, fail=True):
		#only mods that fit the profile	
		if not self._hasPositivePriority(mod):
			return
		#and that aren't enabled already
		try:
			if mod.active:
				return
		except AttributeError:
			pass
		#enable all requirements
		try:
			mod.requires
		except AttributeError:
			pass
		else:
			#run through all requirement selectors
			for selector in mod.requires:
				#they can have different forms, this gets the corresponding ModuleFilterer object
				requiredMods = self._inactiveModsFor(selector)

				#really activate them
				for requiredMod in requiredMods:
					self._activateModule(requiredMod, fail)

				#check if the requirements are satisfied now, if not, raise an error
				if len(set(self._modsFor(selector))) == 0:
					if fail:
						raise NotImplementedError("Mod %s's requirements couldn't be satisfied." % mod)
					else:
						return

		#also enable the mods the module can use (but doesn't need)
		try:
			mod.uses
		except AttributeError:
			pass
		else:
			for selector in mod.uses:
				usableMods = self._inactiveModsFor(selector)
				for usableMod in usableMods:
					self._activateModule(usableMod, False)

		#enable the module itself
		#
		#enable() isn't obligatory, use hasattr because an
		#AttributeError is too common at this functions and will
		#probably be masked with a try/except.
		if hasattr(mod, "enable"):
			mod.enable()

	def activateModules(self):
		for module in self._mm.mods:
			try:
				self._activateModule(module)
			except NotImplementedError:
				continue

def init(moduleManager):
	return ModulesActivatorModule(moduleManager)
