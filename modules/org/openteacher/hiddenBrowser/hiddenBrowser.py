#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Copyright 2011-2012, Cas Widdershoven
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

from PyQt4 import QtCore, QtGui, QtWebKit
import os

class WebBrowserWidget(QtGui.QWidget):
	def __init__(self, mm, *args, **kwargs):
		super(WebBrowserWidget, self).__init__(*args, **kwargs)
		
		vbox = QtGui.QVBoxLayout()
		
		hidelo = QtGui.QHBoxLayout()
		hideSelfButton = QtGui.QPushButton("Hide the browser!")
		hideOthersButton = QtGui.QPushButton("Hide the others; make space for the browser")
		hidelo.addWidget(hideSelfButton)
		hidelo.addWidget(hideOthersButton)
		
		urllo = QtGui.QHBoxLayout()
		
		previousButton = QtGui.QPushButton(QtGui.QIcon(mm.resourcePath("back.png")), "")
		nextButton = QtGui.QPushButton(QtGui.QIcon(mm.resourcePath("forward.png")), "")
		reloadButton = QtGui.QPushButton(QtGui.QIcon(mm.resourcePath("reload.png")), "")
		self.urlbar = QtGui.QLineEdit()
		
		urllo.addWidget(previousButton)
		urllo.addWidget(nextButton)
		urllo.addWidget(reloadButton)
		urllo.addWidget(self.urlbar)
		
		self.webview = QtWebKit.QWebView()
		self.webview.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True);
		
		vbox.addLayout(hidelo)
		vbox.addLayout(urllo)
		vbox.addWidget(self.webview)
		
		self.setLayout(vbox)
		
		hideSelfButton.clicked.connect(self.hideSelf)
		hideOthersButton.clicked.connect(self.hideOthers)
		previousButton.clicked.connect(self.webview.back)
		nextButton.clicked.connect(self.webview.forward)
		reloadButton.clicked.connect(self.webview.reload)
		self.urlbar.returnPressed.connect(self.loadUrl)
		self.webview.load(QtCore.QUrl("http://google.com"))
		
	def loadUrl(self, *args):
		if not unicode(self.urlbar.text()).startswith(u"http://"):
			self.url = QtCore.QUrl(u"http://" + self.urlbar.text())
		else:
			self.url = QtCore.QUrl(self.urlbar.text())
		self.webview.load(self.url)
		
	def hideSelf(self):
		sizes = self.parentWidget().sizes()
		sizes[self.parentWidget().indexOf(self)] = 0
		if sum(sizes):
			self.parentWidget().setSizes(sizes)
		else:
			for i in range(len(sizes)):
				sizes[i] = 1
			sizes[self.parentWidget().indexOf(self)] = 0
			self.parentWidget().setSizes(sizes)
		
	def hideOthers(self):
		sizes = self.parentWidget().sizes()
		size = sizes[self.parentWidget().indexOf(self)]
		for i in range(len(sizes)):
			sizes[i] = 0
		sizes[self.parentWidget().indexOf(self)] = size
		self.parentWidget().setSizes(sizes)

class HiddenBrowserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(HiddenBrowserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "webbrowser"
		
		self.uses = (
			self._mm.mods(type="wordsTeacher"),
			self._mm.mods(type="settings"),
			self._mm.mods(type="lesson"),
			)
		self.filesWithTranslations = ("hiddenBrowser.py",)
		
	def _lessonAdded(self, lesson):
		self._lessons.add(lesson)
		if self._enabled["value"]:
			lesson._teachWidget._lessonWidget.addSideWidget(self.browser)
		
	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		try:
			#Keeps track of all created lessons
			for module in self._mm.mods("active", type="lesson"):
				module.lessonCreated.handle(self._lessonAdded)
		except IndexError:
			pass
		
		try:
			self._enabled = self._modules.default(type="settings").registerSetting(**{
				"internal_name": "org.openteacher.hiddenBrowser.enabled",
				"type": "boolean",
				"defaultValue": False,
				"callback": {
					"args": ("active",),
					"kwargs": {
						"type": "webbrowser"
					},
					"method": "updateActive"
				},
			})
		except IndexError:
			self._enabled = {
				"value": False,
			}
			
		self.browser = WebBrowserWidget(self._mm)
		
		#Register for retranslating
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		#translate everything for the first time
		self._retranslate()
		
		self._lessons = set()
		
		self.active = True
		
	def _retranslate(self):
		#Install translator for this file
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
			
		self._enabled.update({
			"name": _("Enable hidden browser (hide it by moving the slider)"),
		})
	
	def updateActive(self, *args, **kwargs):
		if self._enabled["value"]:
			#Add the web browser to every lesson
			for lesson in self._lessons:
				lesson._teachWidget._lessonWidget.addSideWidget(self.browser)
		else:
			#Remove the web browser from every lesson
			for lesson in self._lessons:
				lesson._teachWidget._lessonWidget.removeSideWidget(self.browser)
		
	def disable(self):
		self.active = False
		
		del self._modules

def init(moduleManager):
	return HiddenBrowserModule(moduleManager)
