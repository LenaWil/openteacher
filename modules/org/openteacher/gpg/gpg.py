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

import os
import tempfile
import subprocess

class GPG(object):
	def __init__(self, gpgbinary="gpg", gpghome="~/.gpg", *args, **kwargs):
		super(GPG, self).__init__(*args, **kwargs)
		
		self.gpgbinary = gpgbinary
		self.gpghome = gpghome
	
	def verify_file(self, sig, filename):
		# Save sig to a temp file
		f = tempfile.NamedTemporaryFile(delete=False, prefix="otgpg")
		s = sig.read()
		f.write(s)
		f.close()
		
		args = []
		args.append(self.gpgbinary)
		args.append("--status-fd")
		args.append("1")
		args.append("--homedir")
		args.append(self.gpghome)
		args.append("--verify")
		args.append(f.name)
		args.append(filename)
		
		print args
		
		o = subprocess.call(args)
		
		os.unlink(f.name)
		
		return o

class GpgModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GpgModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "gpg"

	def enable(self):
		if os.name == "nt":
			self.gpg = GPG(
				gpgbinary=self._mm.resourcePath("gpgwin\\gpg.exe"),
				gpghome=self._mm.resourcePath("gpghome")
			)
		else:
			self.gpg = GPG(
				gpghome=self._mm.resourcePath("gpghome")
			)
		self.active = True

	def disable(self):
		self.active = False

		del self.gpg

def init(moduleManager):
	return GpgModule(moduleManager)
