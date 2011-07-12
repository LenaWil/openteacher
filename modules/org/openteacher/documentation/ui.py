#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2010-2011, Marten de Vries
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

class OpenTeacherWebPage(QtWebKit.QWebPage):
	def __init__(self, url, userAgent, language, *args, **kwargs):
		super(OpenTeacherWebPage, self).__init__(*args, **kwargs)

		self.url = url
		self.userAgent = userAgent

		request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.url))
		request.setRawHeader("Accept-Language", language)
		self.mainFrame().load(request)

		self.connect(self, QtCore.SIGNAL("loadFinished(bool)"), self.updateStatus)

	def userAgentForUrl(self, url):
		return self.userAgent

	def updateStatus(self, ok):
		if not ok:
			text = _("Couldn't reach %s, are you sure you're online?") % self.url
			self.view().setHtml("<p>%s</p>" % text)

class DocumentationDialog(QtWebKit.QWebView):
	def __init__(self, url, userAgent, language, *args, **kwargs):
		super(DocumentationDialog, self).__init__(*args, **kwargs)

		self.setPage(OpenTeacherWebPage(url, userAgent, language, self))
		self.setWindowTitle(_("Documentation"))
