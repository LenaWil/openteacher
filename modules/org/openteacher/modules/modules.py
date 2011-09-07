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

class ModulesModule(object):
	_lowestPriority = 10000

	def __init__(self, moduleManager, *args, **kwargs):
		super(ModulesModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "modules"
		self.requires = (
			(
				{"type": "event"},
			),
		)

	@property
	def profile(self):
		return self.default("active", type="profile").name #FIXME: (question) implementation ok?

	def sort(self, *args, **kwargs):
		def getPriority(mod):
			try:
				return mod.priorities[self._profile]
			except (AttributeError, KeyError):
				#return a negative priority to the sort algorithm so the
				#module gets on top of the list. The negative integer
				#needs to be a number, that makes sure the last
				#installed module is on the top of the list. Maybe just
				#use minutes since installation?
				#
				#FIXME: needs a different implementation. In the
				#meantime, let randomness decide!
				import random
				return -random.randint(1, self._lowestPriority)

		mods = set(self._mm.mods(*args, **kwargs))
		return sorted(mods, key=getPriority)

	def default(self, *args, **kwargs):
		"""Raises IndexError if no modules remain after filtering with
		   the arguments

		"""
		#Look if the user chose one #FIXME: make a replacement module
#		preffered = self._registry.prefferedModule(*args, **kwargs)
#		if preffered:
#			return preffered
		#Otherwise base it on our priority algorithm
		return self.sort(*args, **kwargs)[0]

	def enable(self):
		self.modulesUpdated = self.default( #FIXME: does the event have to exist?
			type="event"
		).createEvent()

		self.active = True

	def disable(self):
		self.active = False

		del self.modulesUpdated

def init(moduleManager):
	return ModulesModule(moduleManager)
