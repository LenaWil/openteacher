#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Milan Boers
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

import sys
import os
import shutil

class WebsiteGeneratorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WebsiteGeneratorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "websiteGenerator"
		
		self.requires = (
			self._mm.mods(type="execute"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)
		
		self.priorities = {
			"generate-website": 0,
			"default": -1,
		}
		
		self.filesWithTranslations = [('templ/' + name) for name in os.listdir(self._mm.resourcePath('templ'))] + \
		                             [('docs/' + name) for name in os.listdir(self._mm.resourcePath('docs'))]
	
	def generateWebsite(self):
		#get path to save to
		try:
			path = sys.argv[1]
		except IndexError:
			print >> sys.stderr, "Please specify a path to save the website to. (e.g. -p generate-website website-debug)"
			return
		#ask if overwrite
		if os.path.exists(path):
			confirm = raw_input("There is already a directory at '%s'. Do you want to remove it and continue (y/n). " % path)
			if confirm != "y":
				return
			shutil.rmtree(path)

		os.mkdir(path)
		
		# Copy images, scripts etc.
		shutil.copytree(self._mm.resourcePath("images"), os.path.join(path, "images"))
		shutil.copytree(self._mm.resourcePath("scripts"), os.path.join(path, "scripts"))
		shutil.copy(self._mm.resourcePath("style.css"), os.path.join(path, "style.css"))
		shutil.copy(self._mm.resourcePath("index.php"), os.path.join(path, "index.php"))
		
		templates = ["index.shtml", "download.html", "contribute.html", "home.html", "about.html", "documentation.html"]
		docs = ["faq.html", "install-arch.html", "install-ubuntu.html", "the-openteacher-format.html", "translator-notes.html", "using-openteacher.html"]
		
		constants = {
			'siteroot': 'http://www.openteacher.org/',
			'downloadLink': 'http://sourceforge.net/projects/openteacher/files/openteacher/3.1/openteacher-3.1-windows-setup.msi/download',
		}
		
		# The default (US English) (unicode as translate function)
		os.mkdir(os.path.join(path, 'en'))
		
		# Make constants
		cconstants = constants.copy()
		cconstants['langroot'] = constants['siteroot'] + 'en/'
		
		# Generate
		self._generatePages(templates, docs, cconstants, unicode, os.path.join(path, 'en'))
		
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			# All the other languages
			for poname in os.listdir(self._mm.resourcePath('translations')):
				if not poname.endswith('.po'):
					continue
				langCode = os.path.splitext(poname)[0]
				
				langpath = os.path.join(path, langCode)
				os.mkdir(langpath)
				
				# Set translation function
				_, ngettext = translator.gettextFunctions(self._mm.resourcePath("translations"), language=langCode)
				
				# Make constants
				cconstants = constants.copy()
				cconstants['langroot'] = constants['siteroot'] + langCode + '/'
				
				# Generate
				self._generatePages(templates, docs, cconstants, _, langpath)
		
		print "Writing OpenTeacher website to '%s' is now done." % path
	
	def _generatePages(self, templates, docs, constants, tr, path):
		# Normal pages
		for templ in templates:
			self._writeTemplate(self._mm.resourcePath("templ/" + templ), os.path.join(path, templ), constants, tr)
		
		# Documentation pages
		os.mkdir(os.path.join(path, "documentation"))
		for doc in docs:
			docconsts = {
				'docPage': self._getTemplate(self._mm.resourcePath("docs/" + doc), constants, tr),
			}
			docconsts.update(constants)
			self._writeTemplate(self._mm.resourcePath("templ/docpage.html"), os.path.join(path, "documentation/" + doc), docconsts, tr)
	
	def _getTemplate(self, template, consts, tr):
		class EvalPseudoSandbox(pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)
				self2.register("tr", tr)
		
		t = pyratemp.Template(filename=template, eval_class=EvalPseudoSandbox)
		return t(**consts)
	
	def _writeTemplate(self, template, outfile, constants, tr):
		result = self._getTemplate(template, constants, tr)
		
		with open(outfile, 'w') as f:
			f.write(result)
	
	def enable(self):
		global pyratemp
		try:
			import pyratemp
		except ImportError:
			sys.stderr.write("For this developer module to work, you need to have pyratemp installed.\n")
		
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		self._modules.default(type="execute").startRunning.handle(self.generateWebsite)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return WebsiteGeneratorModule(moduleManager)
