#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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

class OpenTeachingTopoLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingTopoLoaderModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "load"

		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="otxxLoader"),
		)

	def enable(self):
		self.name = "Open Teaching Topo (.ottp) loader"
		self.loads = {"ottp": ["topo"]}

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._otxxLoader = self._modules.default("active", type="otxxLoader")

		self.active = True

	def disable(self):
		self.active = False

		del self.name
		del self.loads

		del self._modules
		del self._otxxLoader

	def getFileTypeOf(self, path):
		if path.endswith(".ottp"):
			return "topo"

	def load(self, path):
		return self._otxxLoader.load(path, {"mapPath": "map.image"})

def init(moduleManager):
	return OpenTeachingTopoLoaderModule(moduleManager)
