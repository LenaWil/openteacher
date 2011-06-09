#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
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

import urllib2
try:
	from elementTree import ElementTree
except ImportError:
	from xml.etree import ElementTree

class WrtsConnection(object):
	"""This class is used to keep a connection with WRTS. It stores authenticationdata and offers some
	   methods which make it easy to get some data without the need of remembering the URL.

	   Methods:
		   login(email, password)
		   exportWordList(wordList)
		   importWordLIst(url)

		Properties:
			lists - gets all lists from the open account
			loggedIn - tells if the connection keeps valid (working) credentials of the user"""

	class HeadRequest(urllib2.Request):
		"""This class is used to let urllib2 perform a HEAD-request."""
		def get_method(self):
			return "HEAD"

	def __init__(self, moduleManager, *args, **kwargs):
		super(WrtsConnection, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.loggedIn = False

	def logIn(self, email, password):
		"""Creates a connection to WRTS, with the authenticationdata inside it. Raises possibly a WrtsConnectionError/WrtsLoginError"""

		#Create connection
		unencoded = u"%s:%s" % (email, password)
		#to UTF-8, because we need binary
		unencoded = str(unencoded.encode("utf-8"))
		encoded = unencoded.encode("base64").strip()

		self._opener = urllib2.build_opener()
		self._opener.addheaders = [("Authorization", "Basic %s" % encoded),
								   ("User-Agent", "OpenTeacher")]

		#Try loading the api; if not logged in it won't work, and raises a WrtsLoginError
		self._openUrl("http://www.wrts.nl/api", "HEAD")

	@property
	def listsParser(self):
		"""Get all wrts-lists; returns a WrtsListParser instance."""
		xml = self._openUrl("http://www.wrts.nl/api/lists")
		return ListsParser(xml)

	def exportWordList(self, wordList):
		"""Exports a wordList to WRTS, fully automatic after your login. Throws WrtsConnectionError"""
		#Create the xml-document and set the wordlist
		requestXml = RequestXml(wordList)

		#Send a POST request, with as body the xml
		self._openUrl("http://www.wrts.nl/api/lists", "POST", requestXml.createXml(), {"Content-Type": "application/xml"})

	def importWordList(self, url):
		"""Downloads a WRTS wordlist from URL and parses it into a WordList object. Throws WrtsConnectionError/WrtsLoginError"""
		xmlStream = self._openUrl(url)
		wordListParser = WordListParser(self._mm, xmlStream)

		#return the wordList
		return wordListParser.list

	def _openUrl(self, url, method="GET", body=None, additionalHeaders=None):
		"""Open an url, and return the response as a xml.dom.minidom.Document. Can raise a WrtsConnectionError/WrtsConnectionError"""
		#If additionalHeaders not defined, they're set empty
		if not additionalHeaders:
			additionalHeaders = {}
		#Create a request object
		if method == "HEAD":
			request = self.HeadRequest(url, headers=additionalHeaders)
		elif method == "GET":
			request = urllib2.Request(url, headers=additionalHeaders)
		elif method == "POST":
			request = urllib2.Request(url, body, additionalHeaders)
		#Send it
		try:
			response = self._opener.open(request)
		except urllib2.HTTPError, e:
			if e.code == 401:
				#Not logged in
				self.loggedIn = False
				#Tell the user he/she isn't authorized.
				raise errors.WrtsLoginError()
			else:
				#Unknown status (most likely an error): not logged in
				self.loggedIn = False

				#Show for debugging:
				try:
					print e.code, e.reason
				except AttributeError:
					print e.code

				#But because it doesn't make sense to break the program for a WRTS error, show a nice error:
				raise errors.WrtsConnectionError()
		except urllib2.URLError, e:
			#Something wrong with the connection
			self.loggedIn = False
			#show for debugging
			print e
			#Show a nice error to the user.
			raise errors.WrtsConnectionError()

		#If no errors during request
		self.loggedIn = True

		if method == "HEAD":
			#HEAD never sends a body, so xml processing doesn't make sense.
			return

		return response

class ListsParser(object):
	"""This class parses a WRTS-API page: the lists-page. It can return the titles
	   of the lists as a python list with unicode strings, and it an get the url of the
	   corresponding wordList if you give the index of that title"""
	def __init__(self, xmlStream, *args, **kwargs):
		super(ListsParser, self).__init__(*args, **kwargs)

		self.root = ElementTree.parse(xmlStream).getroot()
		self.listsTree = self.root.findall(".//list")

	@property
	def lists(self):
		#Create a list to store the titles in.
		lists = []
		#Add titles to the earlier created list
		for listTree in self.listsTree:
			#Get the title (which can - too bad - be empty at WRTS)
			lists.append(listTree.findtext("title", u""))
		#Return the titles
		return lists

	def getWordListUrl(self, index):
		"""Gets the right node from the titleDom (selected by index),
		   gets the parentNode of it, which has an attribute 'href',
		   which is the needed url."""
		return self.listsTree[index].attrib["href"]

class WordList(object):
	def __init__(self, *args, **kwargs):
		super(WordList, self).__init__(*args, **kwargs)

		self.words = []
		self.tests = []

class Word(object):
	pass

class WordListParser(object):
	"""This class parses a wordlist from the WRTS-API into a WordList-instance."""
	def __init__(self, moduleManager,xmlStream, *args, **kwargs):
		super(WordListParser, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.root = ElementTree.parse(xmlStream).getroot()

	@property
	def list(self):
		#Create a new WordList instance
		wordList = WordList()

		#Read title, question subject and answer subject; sometimes the
		#element is empty, so the fallback u"" is needed.
		wordList.title = self.root.findtext("title", u"")
		wordList.questionLanguage = self.root.findtext("lang-a", u"")
		wordList.answerLanguage = self.root.findtext("lang-b", u"")

		#This counter is used to give each word a unique id
		counter = 0

		#Loop through the words in the xml
		for wordTree in self.root.findall("words/word"):
			#Create a Word-instance
			word = Word()
			word.id = counter

			#Read the question, again keep in mind that null values are
			#possible, so again the u"" fallback. The question is parsed
			#by a wordsStringParser module.

			#FIXME: only one
			for module in self._mm.activeMods.supporting("wordsStringParser"):
				text = wordTree.findtext("word-a", u"")
				word.questions = module.parse(text)

			#Read the answer, again keep in mind that null values are
			#possible, so again the u"" fallback. The answer is parsed
			#by a wordsStringParser module.

			#FIXME: only one
			for module in self._mm.activeMods.supporting("wordsStringParser"):
				text = wordTree.findtext("word-b", u"")
				word.answers = module.parse(text)

			# Add the current edited word to the wordList instance
			wordList.words.append(word)

			counter += 1

		#And finally, return the wordList
		return wordList
