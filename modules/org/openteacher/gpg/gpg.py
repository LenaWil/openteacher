#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2012, Milan Boers
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

import gpgme

class GPG(object):
	"""This class is an abstract layer above a GPG implementation. This
	   class uses the gpgme library, but it can easily be replaced with
	   another implementation, or be extended."""

	def __init__(self, gpghome="~/.gpg", *args, **kwargs):
		super(GPG, self).__init__(*args, **kwargs)

		#Create the GPG environment; set the included gpg home directory
		#with keys of the OpenTeacher maintainers.
		self._c = gpgme.Context()
		self._c.set_engine_info(self._c.protocol, None, gpghome)
	
	def verify_file(self, sigio, fileio):
		"""This method verifies file fileio with separated signature
		   sigio. Both should be Python file-like objects."""

		#call the lib to do all the work :).
		return self._c.verify(sigio, fileio, None)[0].summary

class GpgModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GpgModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "gpg"

	def enable(self):
		self.gpg = GPG(self._mm.resourcePath("gpghome"))

		self.active = True

	def disable(self):
		self.active = False

		del self.gpg

def init(moduleManager):
	return GpgModule(moduleManager)
