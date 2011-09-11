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

from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import weakref

class OpenTeacherWebPage(QtWebKit.QWebPage):
	def __init__(self, url, userAgent, language, *args, **kwargs):
		super(OpenTeacherWebPage, self).__init__(*args, **kwargs)

		self.url = url
		self.userAgent = userAgent

	def userAgentForUrl(self, url):
		return self.userAgent

	def updateStatus(self, ok):
		if not ok:
			text = _("Couldn't reach %s, are you sure you're online?") % self.url
			self.view().setHtml("<p>%s</p>" % text)

	def updateLanguage(self, language):
		request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.url))
		request.setRawHeader("Accept-Language", language)
		self.mainFrame().load(request)

		self.connect(self, QtCore.SIGNAL("loadFinished(bool)"), self.updateStatus)

class DocumentationDialog(QtWebKit.QWebView):
	def __init__(self, url, userAgent, *args, **kwargs):
		super(DocumentationDialog, self).__init__(*args, **kwargs)

		self.page = OpenTeacherWebPage(url, userAgent, self)
		self.setPage(self.page)

	def retranslate(self):
		self.setWindowTitle(_("Documentation"))
		#self.page is retranslated by the updateLanguage call done on a
		#higher level

	def updateLanguage(self, language):
		self.page.updateLanguage(language)

class DocumentationModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(DocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "documentation"
		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="ui"),
		)

	def show(self):
		metadataMod = self._modules.default("active", type="metadata")
		for module in self._mm.mods("active", type="ui"):#FIXME
			dialog = DocumentationDialog(
				metadataMod.documentationUrl,
				metadataMod.userAgent
			)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
			tab.closeRequested.handle(tab.close)
			
			self._activeDialogs.add(weakref.ref(dialog))

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._activeDialogs = set()

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		#load translator
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.name = _("Documentation module")
		for dialog in self._activeDialogs:
			r = dialog()
			if r is not None:
				r.retranslate()
				r.updateLanguage("en") #FIXME: update dynamically

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self._activeDialogs

def init(moduleManager):
	return DocumentationModule(moduleManager)
