#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

import shutil
import sys
import os

class WebGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "webGenerator"
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="webLogicGenerator"),
		)
		self.priorities = {
			"default": -1,
			"generate-web": 0,
		}

	def enable(self):
		global pyratemp
		try:
			import pyratemp
		except ImportError:
			return
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default(type="execute").startRunning.handle(self._run)

		self.active = True

	def _run(self):
		#get path to save to
		try:
			path = sys.argv[1]
			couchdbHost = sys.argv[2]
			servicesHost = sys.argv[3]
		except IndexError:
			print >> sys.stderr, "Please specify a path to save the site to, the couchdb hostname and the services server hostname as last command line arguments. (e.g. -p generate-web web-debug http://localhost:5984 http://localhost:5000)"
			return
		#ask if overwrite
		if os.path.isdir(path):
			confirm = raw_input("There is already a directory at '%s'. Do you want to remove it and continue (y/n). " % path)
			if confirm != "y":
				return
			shutil.rmtree(path)

		#copy all static stuff
		shutil.copytree(self._mm.resourcePath("static"), path)

		#create the config file
		template = pyratemp.Template(filename=self._mm.resourcePath("config.templ.js"))
		with open(os.path.join(path, "scr/config.js"), "w") as f:
			f.write(template(couchdbHost=couchdbHost, servicesHost=servicesHost).encode("UTF-8"))

		#create the logic file
		logicGenerator = self._modules.default("active", type="webLogicGenerator")
		logicPath = os.path.join(path, "scr", "logic.js")
		logicGenerator.writeLogicCode(logicPath)

	def disable(self):
		self.active = False

		self._modules.default(type="execute").startRunning.unhandle(self._run)
		del self._modules

def init(moduleManager):
	return WebGeneratorModule(moduleManager)
