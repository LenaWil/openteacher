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

import __builtin__

class ReverseModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ReverseModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "listModifier"

	def modifyList(self, indexes, list):
		#always work on the indexes, and return a list object
		return __builtin__.list(reversed(indexes))

	def enable(self):
		self.dataType = "all"
		self.name = "Reverse" #FIXME: translate
		self.active = True

	def disable(self):
		self.active = False
		del self.dataType
		del self.name

def init(moduleManager):
	return ReverseModule(moduleManager)
