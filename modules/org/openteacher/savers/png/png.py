#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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

import zipfile
import os
import tempfile
try:
	import json
except:
	import simplejson

class OpenTeachingTopoSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingTopoSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"

	def enable(self):		
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("Open Teaching Topo Image (.png) saver", self)
		self.saves = {"topo": ["png"]}
		
		self.active = True

	def disable(self):
		self.active = False

	def save(self, type, list, path, resources):
		resources["mapScreenshot"].save(path, "PNG")

def init(moduleManager):
	return OpenTeachingTopoSaverModule(moduleManager)
