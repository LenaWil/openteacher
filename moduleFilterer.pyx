#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2013, Marten de Vries
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

class ModuleFilterer(object):
	"""This class is used to filter a list of objects ('modules'). By
	   calling an instance you can add filter requirements. There are
	   two types of filter requirements:
	   - an attribute equals a value
	   - an attribute evaluates to true
	   
	   You can run through the results by a for loop, or get them in
	   a python set/list/tuple/whatever by calling the appropriate
	   conversion function (e.g. set(ModuleFilterer(modules)) )

	"""
	def __init__(self, modules, *args, **kwargs):
		super(ModuleFilterer, self).__init__(*args, **kwargs)
		self._modules = modules

		self._where = {}
		self._whereTrue = set()

	def __call__(self, *args, **kwargs):
		self._whereTrue = self._whereTrue.union(args)
		self._where.update(kwargs)
		return self

	def __iter__(self):
		result = set()
		for module in self._modules:
			append = True
			for attribute, value in self._where.iteritems():
				if not hasattr(module, attribute):
					append = False
					break
				if getattr(module, attribute) != value:
					append = False
					break
			if not append:
				continue
			for attribute in self._whereTrue:
				#hasattr() and getattr() require strings, but we don't
				#want to force the user into that, so we convert it
				#ourselves
				attribute = str(attribute)
				if not hasattr(module, attribute):
					append = False
					break
				if not bool(getattr(module, attribute)):
					append = False
					break
			if append:
				result.add(module)
		return iter(result)

	#the elegant implementation. Maybe generator expressions will once
	#be optimized enough to use it. (In CPython or Cython)
	#
	#~ def __iter__(self):
		#~ return (
			#~ module
			#~ for module in self._modules
			#~ if (
				#~ #matches where
				#~ all(
					#~ getattr(module, attribute, not value) == value
					#~ for attribute, value in self._where.iteritems()
				#~ )
				#~ and
				#~ #matches where true
				#~ all(
					#~ getattr(module, attribute, False)
					#~ for attribute in self._whereTrue
				#~ )
			#~ )
		#~ )
