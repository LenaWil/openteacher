#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   This file is part of QHangMan.
#
#   QHangman is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 3 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class HangmanWidget(QtGui.QWidget):
	def __init__(self, mm, parent = None):
		super(HangmanWidget, self).__init__()
		self.wrongCharacters = []
		self.guesses = []
		self.parent = parent
		
		graphics = mm.import_("graphics")
		word = mm.import_("word")
		
		self.vbox = QtGui.QVBoxLayout()
		self.hgraph = graphics.HangmanGraphics()
		self.hgraph.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding))
		self.wordLabel = QtGui.QLabel()
		self.uiInsert = QtGui.QHBoxLayout()
		self.guessEdit = QtGui.QLineEdit()
		self.guessEdit.returnPressed.connect(self.checkGuess)
		self.insertButton = QtGui.QPushButton("Guess letter / word")
		self.insertButton.clicked.connect(self.checkGuess)
		self.uiInsert.addWidget(self.guessEdit)
		self.uiInsert.addWidget(self.insertButton)
		self.wrongCharactersLabel = QtGui.QLabel("  ")
		self.wordLessonWordLabel = QtGui.QLabel()
		self.questionLabel = QtGui.QLabel()
		self.questionLabel.setWordWrap(True)
		self.vbox.addWidget(self.hgraph)
		self.vbox.addWidget(self.wordLessonWordLabel)
		self.vbox.addWidget(self.questionLabel)
		self.vbox.addWidget(self.wordLabel)
		self.vbox.addLayout(self.uiInsert)
		self.vbox.addWidget(self.wrongCharactersLabel)
		self.setLayout(self.vbox)
		self.setWindowTitle('Hangman v0.1')
		self.word = None
		self.onlineGame = False
	
	def checkGuess(self):
		guess = self.guessEdit.text()
		if guess in self.guesses:
			alreadyGuessedDialog = QtGui.QMessageBox(self)
			alreadyGuessedDialog.setText('You have already tried this character / word')
			alreadyGuessedDialog.addButton('OK', alreadyGuessedDialog.AcceptRole).setFocus()
			alreadyGuessedDialog.exec_()
			self.guessEdit.clear()
			return
		self.guesses.append(guess)
		wordLabelList = list(self.wordLabel.text())
		if len(guess) == 1:
			results = self.word.guessCharacter(guess) #A list with [index, character]
			if results:
				for i in results:
					wordLabelList[i[0]] = i[1]
				resultingString = ""
				for i in wordLabelList:
					resultingString += i
				self.wordLabel.setText(resultingString)
				if self.wordLabel.text() == self.word._word:
					self.showEndOfGame(True)
			else:
				self.wrongCharacters.append(str(guess))
				self.wrongCharactersLabel.setText('Mistakes:  ' + '  |  '.join(self.wrongCharacters))
				self.hgraph.mistakes = self.word.mistakes
				self.hgraph.update()
				if self.word.mistakes >= 6:
					self.showEndOfGame(False)
		elif len(guess) > 1:
			if self.word.guessWord(guess):
				self.showEndOfGame(True)
			else:
				self.hgraph.mistakes = self.word.mistakes
				self.hgraph.update()
				if self.word.mistakes >= 6:
					self.showEndOfGame(False)
		self.guessEdit.clear()
	
	def showEndOfGame(self, win):
		self.guesses = []
		self.wrongCharacters = []
		self.wrongCharactersLabel.setText('')
		self.word = None
		self.wordLabel.setText("")
		self.hgraph.mistakes = 0
		self.hgraph.update()
		self.parent.setResult(win)
				

class Hangman(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.resize(300, 300)
		self.setWindowTitle('Hangman v0.1')

		self.hwidget = HangmanWidget(self)
		self.setCentralWidget(self.hwidget)
		
		self.new = QtGui.QAction(QtGui.QIcon('../icons/new.gif'), 'New game', self)
		self.new.setShortcut('Ctrl+N')
		self.new.triggered.connect(self.newGame)
		
		self.exit = QtGui.QAction(QtGui.QIcon('../icons/exit.gif'), 'Exit', self)
		self.exit.setShortcut('Ctrl+Q')
		self.exit.triggered.connect(self.close)
		
		self.toolbar = self.addToolBar('New')
		self.toolbar.addAction(self.new)
		self.toolbar.addAction(self.exit)
		
		self.hwidget.setEnabled(False)
		
	def newGame(self):
		newGameDialog = NewGameDialog(self.hwidget)
		newGameDialog.exec_()
		try:
			labelString = ""
			for i in xrange(self.hwidget.word.length):
				labelString += '-'
			self.hwidget.wordLabel.setText(labelString)
			self.hwidget.setEnabled(True)
		except AttributeError:
			pass
			
def main():
  
	app = QtGui.QApplication([])
	hmn = Hangman()
	hmn.show()
	app.exec_()  


if __name__ == '__main__':
	main()
