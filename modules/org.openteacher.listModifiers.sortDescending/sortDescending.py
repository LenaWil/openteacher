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

class SortDescendingModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SortDescendingModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("listModifier",)
		self.requires = (1, 0)
		self.active = False

	def modifyList(self, indexes, list):
		#always work on the indexes
		return sorted(indexes, reverse=True)

	def enable(self):
		self.type = "all"
		self.name = "Sort (descending)"
		self.active = True

	def disable(self):
		self.active = False
		del self.type
		del self.name

def init(moduleManager):
	return SortDescendingModule(moduleManager)
