#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl

from launchpadlib import launchpad
import re
import urllib2
import urllib

class OpenTeacherBot(irc.IRCClient):
	factoids = {
		".downloads": "http://openteacher.org/download.html",
		".sf": "http://sourceforge.net/projects/openteacher",
		".stats": "http://sourceforge.net/projects/openteacher/files/stats",
		".lp": "https://launchpad.net/openteacher",
		".blueprints": "https://blueprints.launchpad.net/openteacher",
		".code": "https://code.launchpad.net/openteacher",
		".bugs": "https://bugs.launchpad.net/openteacher",
		".answers": "https://answers.launchpad.net/openteacher",
		".translations": "https://translations.launchpad.net/openteacher",
		".website": "http://openteacher.org/",
		".about": "http://openteacher.org/about.html",
		".documentation": "http://openteacher.org/documentation.html",
		".codedocs": "http://people.ubuntu.com/~marten-de-vries/openteacher-code-documentation",
		".contribute": "http://openteacher.org/contribute.html",
		".forum": "http://forum.ubuntu-nl.org/etalage/openteacher-overhoorprogramma-voor-linux/new/#new",
		".wiki": "http://sourceforge.net/apps/mediawiki/openteacher/index.php",
		".ogd": "http://opengamedesigner.org/",
		".twitter": "http://twitter.com/#!/openteacher",
		".facebook": "http://www.facebook.com/OpenTeacher",
		".hyves": "http://openteacher.hyves.nl/",
		".ohloh": "http://www.ohloh.net/p/openteacher",
		".mailarchive": "https://lists.launchpad.net/openteachermaintainers/",
		".paste": "http://paste.ubuntu.com/",
		".etherpad": "http://openetherpad.org/",
	}
	factoids[".download"] = factoids[".downloads"]
	factoids[".homepage"] = factoids[".website"]
	factoids[".codedocumentation"] = factoids[".codedocs"]
	factoids[".forumtopic"] = factoids[".forum"]
	factoids[".mailinglist"] = factoids[".mailarchive"]
	factoids[".pastebin"] = factoids[".paste"]

	@property
	def nickname(self):
		return self.factory.nickname

	@property
	def password(self):
		return self.factory.password

	@property
	def realname(self):
		return self.factory.realname

	def signedOn(self):
		print "Signed on. Now joining channels."
		for channel in self.factory.channels:
			self.join(channel)

	def joined(self, channel):
		print "Joined %s." % (channel,)

	def privmsg(self, user, channel, msg):
		print "%s: %s: %s" % (user.split("!")[0], channel, msg)
		target = channel if channel in self.factory.channels else user.split("!")[0]
		#factoids
		if msg in self.factoids:
			self.msg(target, self.factoids[msg])
		#bugs
		match = re.search("(?:bugs? ?/?|#)([0-9]+)", msg)
		if match:
			number = match.group(1)
			bug = self.factory.launchpad.bugs[number]
			if bug:
				try:
					task = bug.bug_tasks[0] #should not crash, but to be sure
				except IndexError:
					pass
				else:
					text = "bug #%s: %s (status: %s, importance: %s) - %s" % (
						bug.id,
						bug.title,
						task.status,
						task.importance,
						bug.web_link
					)
					self.msg(target, text.encode("UTF-8"))

		#branches
		match = re.search("lp:[^ ]*(?=[^,.?!])[^ ]", msg)
		if match:
			branch = self.factory.launchpad.branches.getByUrl(url=match.group(0))
			if branch:
				text = "branch %s (status: %s, %s revisions) - %s" % (
					branch.bzr_identity,
					branch.lifecycle_status,
					branch.revision_count,
					branch.web_link,
				)
				self.msg(target, text.encode("UTF-8"))
		
		if msg.startswith(".py "):
			statement = msg[4:]

			data = urllib.urlencode({
				"statement": statement,
				"session": "agVzaGVsbHITCxIHU2Vzc2lvbhiJzovInooGDA",
			})
			data = urllib2.urlopen("http://shell.appspot.com/shell.do?" + data).read()
			result = data.strip().split("\n")[-1]
			if len(result) > 350:
				result = result[len(result) - 350:]
			self.msg(target, result)

		if msg == ".quit" and user in self.factory.admins:
			self.factory.timeToQuit = True
			self.quit()

#		#blueprints
#		match = re.search("(?:specs?[ /]+|blueprints? )([^ ,.?!/]+)", msg)
#		if match:
#			spec = self.factory.launchpad.projects["openteacher"].getSpecification(name=match.group(1))
#			if spec:
#				text = "blueprint %s: %s (definition status: %s, implementation status: %s, priority: %s) - %s" % (
#					spec.name,
#					spec.title,
#					spec.definition_status,
#					spec.implementation_status,
#					spec.priority,
#					spec.web_link,
#				)

class OpenTeacherBotFactory(protocol.ClientFactory):
	protocol = OpenTeacherBot

	def __init__(self, channels, nickname, realname, password, admins):
		self.channels = channels
		self.nickname = nickname
		self.realname = realname
		self.password = password
		self.admins = admins

		self.timeToQuit = False

		self.launchpad = launchpad.Launchpad.login_anonymously("OpenTeacher bot", "production", "~/.config/launchpadlib")

	def clientConnectionLost(self, connector, reason):
		if not self.timeToQuit:
			print "Lost connection: %s. Trying to reconnect" % (reason,)
			connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print "Connection impossible: %s" % (reason,)


def run():
	print """For a nice quit, first tell the bot to .quit
on irc. Then press ctrl+c here.\n"""

	config = {
		"channels": [
			"##PyTest",
		],
		"nickname": "OTbot-dev",
		"realname": "http://openteacher.org/",
		"password": None,
		"admins": [
			"CasW!~cas@unaffiliated/casw",
			"commandoline!~commandol@ubuntu/member/commandoline",
			"lordnoid!~lordnoid@53537359.cm-6-4b.dynamic.ziggo.nl",
		]
	}
	reactor.connectSSL('irc.freenode.net', 7000, OpenTeacherBotFactory(**config), ssl.ClientContextFactory())
	reactor.run()
