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

import shelve

class DataStoreModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(DataStoreModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "dataStore"

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.store = shelve.open(
			self._mm.resourcePath("store.shelve"),
			writeback=True
		)
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.store

def init(moduleManager):
	return DataStoreModule(moduleManager)
