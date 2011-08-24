#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2008-2011, Milan Boers
#	Copyright 2009-2011, Marten de Vries
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


class TopoTestTypeModule(object):
	PLACE_NAME, CORRECT = xrange(2)
	def __init__(self, moduleManager, *args, **kwargs):
		super(TopoTestTypeModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		
		self.type = "testType"
		self.dataType = "topo"

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False
	
	def updateList(self, list, test):
		self._list = list
		self._test = test
	
	@property
	def header(self):
		return [
			_("Place name"),#FIXME: own translator
			_("Correct")
		]
	
	def _itemForResult(self, result):
		for item in self._list["items"]:
			if result["itemId"] == item["id"]:
				return item
	
	def data(self, row, column):
		result = self._test["results"][row]
		
		item = self._itemForResult(result)
		if column == self.PLACE_NAME:
			return item["name"]
		elif column == self.CORRECT:
			return result["result"] == "right"

def init(moduleManager):
	return TopoTestTypeModule(moduleManager)
