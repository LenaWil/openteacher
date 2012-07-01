#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
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


class Word(object):
    def __init__(self, word):
        self.mistakes = 0
        self.length = len(word)
        
        self._word = word
 
    def guessCharacter(self, guessedCharacter):
        results = []
        for index in xrange(len(self._word)):
            character = self._word[index]
            if character == guessedCharacter:
                results.append([index, character])
        
        if len(results) == 0:
            self.mistakes += 1
        return results
    
    def guessWord(self, guessedWord):
        if guessedWord == self._word:
            return True
        else:
            self.mistakes += 2
            
            return False
