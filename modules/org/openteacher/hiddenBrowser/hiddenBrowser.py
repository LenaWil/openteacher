#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Copyright 2011-2012, Cas Widdershoven
#	Copyright 2012, Marten de Vries
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
	def __init__(self, resourcePath, startPage, *args, **kwargs):
		super(WebBrowserWidget, self).__init__(*args, **kwargs)
		
		vbox = QtGui.QVBoxLayout()
		
		hidelo = QtGui.QHBoxLayout()
		self.hideSelfButton = QtGui.QPushButton()
		self.hideOthersButton = QtGui.QPushButton()
		hidelo.addWidget(self.hideSelfButton)
		hidelo.addWidget(self.hideOthersButton)
		
		urllo = QtGui.QHBoxLayout()
		
		previousButton = QtGui.QPushButton(QtGui.QIcon.fromTheme(
			"back",
			QtGui.QIcon(resourcePath("icons/back.png"))
		), "")
		nextButton = QtGui.QPushButton(QtGui.QIcon.fromTheme(
			"forward",
			QtGui.QIcon(resourcePath("icons/forward.png"))
		), "")
		reloadButton = QtGui.QPushButton(QtGui.QIcon.fromTheme(
			"reload",
			QtGui.QIcon(resourcePath("icons/reload.png"))
		), "")
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
		
		self.hideSelfButton.clicked.connect(self.hideSelf)
		self.hideOthersButton.clicked.connect(self.hideOthers)
		previousButton.clicked.connect(self.webview.back)
		nextButton.clicked.connect(self.webview.forward)
		reloadButton.clicked.connect(self.webview.reload)
		self.urlbar.returnPressed.connect(self.loadUrl)
		self.webview.urlChanged.connect(
			lambda url: self.urlbar.setText(url.toString())
		)

		self.webview.load(QtCore.QUrl(startPage))

		#finally
		self.retranslate()

	def retranslate(self):
		self.hideSelfButton.setText(_("Hide the browser!"))
		self.hideOthersButton.setText(_("Hide the others; make space for the browser"))
		
	def loadUrl(self, *args):
		if not unicode(self.urlbar.text()).startswith(u"http://"):
			self.url = QtCore.QUrl(u"http://" + self.urlbar.text(), QtCore.QUrl.TolerantMode)
		else:
			self.url = QtCore.QUrl(self.urlbar.text(), QtCore.QUrl.TolerantMode)
		self.webview.load(self.url)

	def hideSelf(self):
		#FIXME (3.1): Make sure this works via a nice module interface,
		#because this breaks as soon as a very small change is made. (It
		#already did once...)

		#show other side widgets
		sizes = self.parentWidget().sizes()
		sizes[self.parentWidget().indexOf(self)] = 0
		if sum(sizes):
			self.parentWidget().setSizes(sizes)
		else:
			for i in range(len(sizes)):
				sizes[i] = 1
			sizes[self.parentWidget().indexOf(self)] = 0
			self.parentWidget().setSizes(sizes)

		#show other widgets
		sizes = self.parentWidget().parentWidget().sizes()
		for i in range(len(sizes)):
			sizes[i] = 1
		self.parentWidget().parentWidget().setSizes(sizes)

	def hideOthers(self):
		#FIXME 3.1: see hideSelf.

		#hide other side widgets
		sizes = self.parentWidget().sizes()
		size = sizes[self.parentWidget().indexOf(self)]
		for i in range(len(sizes)):
			sizes[i] = 0
		sizes[self.parentWidget().indexOf(self)] = size
		self.parentWidget().setSizes(sizes)

		#hide other widgets
		sizes = self.parentWidget().parentWidget().sizes()
		size = sizes[self.parentWidget().parentWidget().indexOf(self.parentWidget())]
		for i in range(len(sizes)):
			sizes[i] = 0
		sizes[self.parentWidget().parentWidget().indexOf(self.parentWidget())] = size
		self.parentWidget().parentWidget().setSizes(sizes)

class HiddenBrowserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(HiddenBrowserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "webbrowser"
		
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="metadata"),
		)
		self.uses = (
			self._mm.mods(type="settings"),
			self._mm.mods(type="lesson"),
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("hiddenBrowser.py",)
		x = 940
		self.priorities = {
			"all": x,
			"selfstudy": -x,
			"student@home": x,
			"student@school": -x,
			"teacher": -x,
			"wordsonly": -x,
		}

	def _lessonAdded(self, lesson):
		self._lessons.add(lesson)
		if self._enabled["value"]:
			try:
				#FIXME (3.1?): don't access private properties (teachWidget & lessonWidget)
				lesson._teachWidget._lessonWidget.addSideWidget(self.browser)
			except AttributeError:
				#not every lesson teachWidget has an addSideWidget
				pass

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
		metadata = self._modules.default("active", type="metadata").metadata
		
		#Register for retranslating
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		#translate everything for the first time
		self._retranslate()

		#FIXME 3.1: This object is now built even if the webview is
		#never shown. Since building it is quite heavy (e.g. a Java
		#VM starts if installed), that should be delayed.
		self.browser = WebBrowserWidget(self._mm.resourcePath, metadata["website"])
		
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
		try:
			self.browser.retranslate()
		except AttributeError:
			#first time it's not there
			pass
	
	def updateActive(self, *args, **kwargs):
		if self._enabled["value"]:
			#Add the web browser to every lesson
			for lesson in self._lessons:
				try:
					lesson._teachWidget._lessonWidget.addSideWidget(self.browser)
				except AttributeError:
					#in case the lesson doesn't support sideWidgets
					pass
		else:
			#Remove the web browser from every lesson
			for lesson in self._lessons:
				try:
					lesson._teachWidget._lessonWidget.removeSideWidget(self.browser)
				except AttributeError:
					#in case the lesson doesn't support sideWidgets
					pass
	
	def disable(self):
		self.active = False
		
		del self._modules

def init(moduleManager):
	return HiddenBrowserModule(moduleManager)
