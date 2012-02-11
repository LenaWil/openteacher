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

class RecentlyOpenedModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(RecentlyOpenedModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "recentlyOpened"
		
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="dataStore"),
		)

	def add(self, **kwargs):
		"""This method adds 'something that was recently opened' to the
		   list. The arguments should be:
		    * identifier
		     * preferably the domain syntax (com.example.module.unique_name)
		    * label
		     * text describing the recently opened thing. E.g. a title
		       or, if nothing better exists, a file name.
		    * icon
			 * path to an icon file, optional
		    * moduleArgsSelectors, moduleKwargsSelectors
		     * used to select the module that can re-open the recently
		       opened thing. Same as in:
		        self._mm.mods(*moduleArgsSelectors, **moduleKwargselectors)
			* method
			 * the method that should be called on the earlier selected
			   module to re-open the recently opened thing.
			* args
			 * the positional arguments that need to be passed to
			   'method'
			* kwargs
			 * the keyword arguments that need to be passed to 'method'

		"""
		self._recentlyOpened.insert(0, kwargs)
		if len(self._recentlyOpened) > 10: #FIXME: setting?
			self._recentlyOpened.pop()
		self.updated.send()
		
		#debug
		self.store.write()

	def remove(self, uniqueName):
		for i in range(len(self._recentlyOpened)):
			if self._recentlyOpened[i]["uniqueName"] == uniqueName:
				del self._recentlyOpened[i]
				return
		self.updated.send()

	def getRecentlyOpened(self):
		return self._recentlyOpened

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.store = self._modules.default(type="dataStore").store
		try:
			self._recentlyOpened = self.store["org.openteacher.recentlyOpened"]
		except KeyError:
			self._recentlyOpened = self.store["org.openteacher.recentlyOpened"] = []

		self.updated = self._modules.default(type="event").createEvent()

		self.active = True

	def disable(self):
		self.active = False

		del self._recentlyOpened

def init(moduleManager):
	return RecentlyOpenedModule(moduleManager)
