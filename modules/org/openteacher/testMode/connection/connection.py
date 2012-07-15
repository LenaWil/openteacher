#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
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

from PyQt4 import QtGui
from PyQt4 import QtCore
import os
import urllib
import urllib2
import cookielib
import hashlib
import socket
try:
	import json
except:
	import simplejson as json

MAXVERSION = 1.0

class ConnectWidget(QtGui.QWidget):
	"""We use HTTP so there's not actually a continuous connection, but
	   this class is basically here to check whether a server exists.

	"""
	def __init__(self, connection, *args, **kwargs):
		super(ConnectWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		
		self.connectLayout = QtGui.QFormLayout()
		self.setLayout(self.connectLayout)
		
		self.serverField = QtGui.QLineEdit()
		self.connectLayout.addRow(_("Server IP or hostname:"), self.serverField)
		
		connectButton = QtGui.QPushButton(_("Connect"))
		connectButton.clicked.connect(lambda: self.connection.connect(str(self.serverField.text())))
		self.connectLayout.addRow(connectButton)
		
		self.serverField.returnPressed.connect(connectButton.click)

class LoginWidget(QtGui.QWidget):
	def __init__(self, connection, loginid, *args, **kwargs):
		super(LoginWidget, self).__init__(*args, **kwargs)
		
		self.connection = connection
		
		self.loginLayout = QtGui.QFormLayout()
		self.setLayout(self.loginLayout)
		
		self.usernameField = QtGui.QLineEdit()
		self.loginLayout.addRow(_("Username:"), self.usernameField)
		
		self.passwordField = QtGui.QLineEdit()
		self.passwordField.setEchoMode(QtGui.QLineEdit.Password)
		self.loginLayout.addRow(_("Password:"), self.passwordField)
		
		self.checkButton = QtGui.QPushButton(_("Login"))
		self.checkButton.clicked.connect(lambda : connection.checkLogin(str(self.usernameField.text()), str(self.passwordField.text()), loginid))
		self.loginLayout.addRow(self.checkButton)
		
		self.passwordField.returnPressed.connect(self.checkButton.click)

class ConnectLoginWidget(QtGui.QWidget):
	def __init__(self, connection, loginid, *args, **kwargs):
		super(ConnectLoginWidget, self).__init__(*args, **kwargs)
		
		self.layout = QtGui.QStackedLayout()
		self.setLayout(self.layout)
		
		self.connectWidget = ConnectWidget(connection)
		connection.connected.handle(self.afterConnect)
		self.layout.addWidget(self.connectWidget)
		
		self.loginWidget = LoginWidget(connection, loginid)
		self.layout.addWidget(self.loginWidget)
	
	def afterConnect(self):
		self.layout.setCurrentWidget(self.loginWidget)

class Connection(object):
	def __init__(self, modules, *args, **kwargs):
		super(Connection, self).__init__(*args, **kwargs)
		
		self._modules = modules
		
		# Connected event
		self.connected = self._modules.default(type="event").createEvent()
		# LoggedIn event
		self.loggedIn = self._modules.default(type="event").createEvent()
		
		# Setup opener
		self.opener = urllib2.build_opener()
		self.server = None
		self.serverName = None
		self.auth = False
	
	# "Connected" to the server and logged in?
	@property
	def connectedLoggedIn(self):
		return self.server != None and self.auth == True
	
	# "Connect" to server
	def connect(self, hostname):
		try:
			# Replace hostname by IP (so DNS is not needed at every request. Will speed things up.)
			hostname = socket.gethostbyname(hostname)
		except socket.gaierror:
			# Could not connect
			dialogShower = self._modules.default(type="dialogShower")
			dialogShower.showError.send(self.loginTab, "Could not connect to the server. Possibly wrong hostname.")
		else:
			# Everything OK, Connected
			self.server = hostname
			# Try to fetch the index page
			index = self.get("https://%s:8080/" % (hostname))
			self.serverName = index["name"]
			
			self.connected.send()
	
	# Get path
	def get(self, path):
		try:
			req = json.load(self.opener.open("https://%s:8080/%s" % (self.server, path)))
			return req
		except urllib2.HTTPError, e:
			return e
	
	def post(self, path, data):
		data = urllib.urlencode(data)
		try:
			request = urllib2.Request("https://%s:8080/%s" % (self.server, path), data)
			return json.load(self.opener.open(request))
		except urllib2.HTTPError, e:
			return e
	
	def put(self, path, data):
		data = urllib.urlencode(data)
		try:
			request = urllib2.Request("https://%s:8080/%s" % (self.server, path), data)
			request.get_method = lambda: 'PUT'
			return json.load(self.opener.open(request))
		except urllib2.HTTPError, e:
			return e
	
	# Method to log in. You need to send a uuid along, so your loggedIn doesn't react to other requests.
	def login(self, loginid):
		if self.connectedLoggedIn:
			self._afterLogin(loginid)
		else:
			self.connectLoginWidget = ConnectLoginWidget(self, loginid)
			
			module = self._modules.default("active", type="ui")
			self.loginTab = module.addCustomTab(self.connectLoginWidget)
			self.loginTab.title = _("Login") #FIXME: retranslate etc.

			self.loginTab.closeRequested.handle(self.loginTab.close)
	
	# Checks if login is right (and implicitly fetches the token) (te be used only inside this module)
	def checkLogin(self, username, passwd, loginid):
		index = "https://%s:8080/" % self.server
		
		loginCreds = u"%s:%s" % (username, passwd)
		loginCreds = str(loginCreds.encode("utf-8"))
		loginCreds = loginCreds.encode("base64").strip()
		
		self.opener.addheaders = [("Authorization", "Basic %s" % loginCreds)]
		
		#fixme: check password
		me = self.get("users/me")
		
		if type(me) == urllib2.HTTPError:
			# User was not logged in
			dialogShower = self._modules.default("active", type="dialogShower")
			dialogShower.showError.send(self.loginTab, "Could not login. Wrong username or password.")
		else:
			self.userId = int(os.path.basename(me))
			self._afterLogin(loginid)
	
	def _afterLogin(self, loginid):
		# Logged in, set var to server
		self.auth = True
		self.loginTab.close()
		self.loggedIn.send(loginid)

class TestModeConnectionModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeConnectionModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "testModeConnection"
		self.priorities = {
			"student@home": -1,
			"student@school": 444,
			"teacher": 444,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": 444,
			"codedocumentation": 444,
			"all": 444,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="ui"),
		)
		self.filesWithTranslations = ("connection.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		#setup translation
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
		
		self.connection = Connection(self._modules)
		
		self.active = True

	def disable(self):
		self.active = False
	
	def getConnection(self):
		return self.connection

def init(moduleManager):
	return TestModeConnectionModule(moduleManager)
