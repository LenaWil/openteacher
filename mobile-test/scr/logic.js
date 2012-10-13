/*
	Copyright 2012, Marten de Vries

	This file is part of OpenTeacher.

	OpenTeacher is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	OpenTeacher is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
*/

var logic;

logic = (function () {
/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	var parse = (function () {
		"use strict";
		var obligatoryRe, wordRe, reverseAndTrim, isEmpty;
	
		obligatoryRe = new RegExp("\\.[0-9]+(?!\\\\)");
		wordRe = new RegExp("[,;](?!\\\\)");
	
		reverseAndTrim = function (i) {
			//reverse all words (the characters) back and trim them
			return i.split("").reverse().join("").trim();
		};
	
		isEmpty = function (i) {
			//remove empty words
			return i;
		};
	
		return function (text) {
			var obligatoryElements, result, i, obligatoryElement, words;
	
			//so we don't need negative lookback assertions :).
			text = text.split("").reverse().join("");
	
			obligatoryElements = text.split(obligatoryRe);
			//reverse order, reversing the text itself happens later on.
			obligatoryElements.reverse();
	
			result = [];
			for (i = 0; i < obligatoryElements.length; i += 1) {
				obligatoryElement = obligatoryElements[i];
	
				//split words
				words = obligatoryElement.split(wordRe);
	
				words = words.map(reverseAndTrim);
				words = words.filter(isEmpty);
				//revert the last unreversed thing: the order of the words
				words = words.reverse();
	
				if (words.length !== 0) {
					//add if non-empty
					result.push(words);
				}
			}
	
			return result;
		};
	}());


	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	var compose = function (word) {
		"use strict";
		var text, i, obligatorySet;
	
		if (word.length === 0) {
			return "";
		}
		if (word.length === 1) {
			return word[0].join(", ");
		}
		text = "";
		for (i = 0; i < word.length; i += 1) {
			obligatorySet = word[i];
			text += [
				i + 1,
				". ",
				obligatorySet.join(", "),
				" "
			].join("");
		}
		return text.trim();
	};


	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	var parse = (function () {
		"use strict";
		var obligatoryRe, wordRe, reverseAndTrim, isEmpty;
	
		obligatoryRe = new RegExp("\\.[0-9]+(?!\\\\)");
		wordRe = new RegExp("[,;](?!\\\\)");
	
		reverseAndTrim = function (i) {
			//reverse all words (the characters) back and trim them
			return i.split("").reverse().join("").trim();
		};
	
		isEmpty = function (i) {
			//remove empty words
			return i;
		};
	
		return function (text) {
			var obligatoryElements, result, i, obligatoryElement, words;
	
			//so we don't need negative lookback assertions :).
			text = text.split("").reverse().join("");
	
			obligatoryElements = text.split(obligatoryRe);
			//reverse order, reversing the text itself happens later on.
			obligatoryElements.reverse();
	
			result = [];
			for (i = 0; i < obligatoryElements.length; i += 1) {
				obligatoryElement = obligatoryElements[i];
	
				//split words
				words = obligatoryElement.split(wordRe);
	
				words = words.map(reverseAndTrim);
				words = words.filter(isEmpty);
				//revert the last unreversed thing: the order of the words
				words = words.reverse();
	
				if (words.length !== 0) {
					//add if non-empty
					result.push(words);
				}
			}
	
			return result;
		};
	}());
	
	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	var check = (function () {
		"use strict";
		var calculateDifference, arrayValuesEqual;
	
		calculateDifference = function (a1, a2) {
			var item;
	
			return a1.filter(function (item) {
				return a2.indexOf(item) === -1;
			});
		};
	
		arrayValuesEqual = function (a1, a2) {
			var i, index;
	
			//copy, it's going to be modified
			a1 = a1.slice();
	
			for (i = 0; i < a2.length; i += 1) {
				index = a1.indexOf(a2[i]);
				if (index === -1) {
					return false;
				}
				a1.splice(index, 1);
			}
			return a1.length === 0;
		};
	
		return function (givenAnswerString, word) {
			var givenAnswer, result, compulsoryAnswerCount, difference, i, compulsoryAnswer, oldDifference, compulsoryGivenAnswer, j;
	
			givenAnswer = parse(givenAnswerString);
	
			result = {"result": "wrong"};
			compulsoryAnswerCount = 0;
	
			if (givenAnswer.length === 1) {
				result = {"result": "right"};
				difference = givenAnswer[0];
				for (i = 0; i < word.answers.length; i += 1) {
					compulsoryAnswer = word.answers[i];
	
					oldDifference = difference;
					difference = calculateDifference(difference, compulsoryAnswer);
					if (arrayValuesEqual(oldDifference, difference)) {
						result = {"result": "wrong"};
						break;
					}
				}
				if (result.result === "right" && difference.length !== 0) {
					result = {"result": "wrong"};
				}
			} else if (givenAnswer.length > 1) {
				for (i = 0; i < givenAnswer.length; i += 1) {
					compulsoryGivenAnswer = givenAnswer[i];
	
					for (j = 0; j < word.answers.length; j += 1) {
						compulsoryAnswer = word.answers[j];
	
						difference = calculateDifference(compulsoryGivenAnswer, compulsoryAnswer);
						if (difference.length === 0) {
							compulsoryAnswerCount += 1;
						}
					}
				}
				if (compulsoryAnswerCount === word.answers.length) {
					result = {"result": "right"};
				}
			}
	
			return result;
		};
	}());


	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	var parse = (function () {
		"use strict";
		var obligatoryRe, wordRe, reverseAndTrim, isEmpty;
	
		obligatoryRe = new RegExp("\\.[0-9]+(?!\\\\)");
		wordRe = new RegExp("[,;](?!\\\\)");
	
		reverseAndTrim = function (i) {
			//reverse all words (the characters) back and trim them
			return i.split("").reverse().join("").trim();
		};
	
		isEmpty = function (i) {
			//remove empty words
			return i;
		};
	
		return function (text) {
			var obligatoryElements, result, i, obligatoryElement, words;
	
			//so we don't need negative lookback assertions :).
			text = text.split("").reverse().join("");
	
			obligatoryElements = text.split(obligatoryRe);
			//reverse order, reversing the text itself happens later on.
			obligatoryElements.reverse();
	
			result = [];
			for (i = 0; i < obligatoryElements.length; i += 1) {
				obligatoryElement = obligatoryElements[i];
	
				//split words
				words = obligatoryElement.split(wordRe);
	
				words = words.map(reverseAndTrim);
				words = words.filter(isEmpty);
				//revert the last unreversed thing: the order of the words
				words = words.reverse();
	
				if (words.length !== 0) {
					//add if non-empty
					result.push(words);
				}
			}
	
			return result;
		};
	}());
	
	
	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	/*global parse: false */
	
	var parseList = function (string) {
		"use strict";
	
		//assumed global: parse(wordsString);
		var SeparatorError, re, parseLine, counter, list, lines, i, word;
	
		SeparatorError = function (message) {
			this.name = "SeparatorError";
			this.message = message;
		};
		SeparatorError.prototype = new Error();
		SeparatorError.prototype.constructor = SeparatorError;
	
		//the '\\\\' part matches exactly 1 '\' due to both JS and regex
		//escaping...
		re = new RegExp("[^\\\\][=\t]");
	
		parseLine = function (line, id) {
			var questionText, answerText, firstOccurenceIndex;
	
			if (line.trim() === "") {
				return;
			}
	
			if (["\t", "="].indexOf(line[0]) !== -1) {
				//if first character is \t or =, run special logic because
				//the regex handler down here can't cope with that.
				questionText = "";
				answerText = line.slice(1);
			} else {
				firstOccurenceIndex = line.search(re);
				if (firstOccurenceIndex === -1) {
					throw new SeparatorError("Missing equals sign or tab");
				}
				questionText = line.slice(0, firstOccurenceIndex + 1);
				answerText = line.slice(firstOccurenceIndex + 2);
			}
	
			return {
				"id": id,
				"questions": parse(questionText),
				"answers": parse(answerText)
			};
		};
	
		list = {
			"items": [],
			"tests": []
		};
		counter = 0;
		lines = string.split("\n");
		for (i = 0; i < lines.length; i += 1) {
			word = parseLine(lines[i], counter);
			if (word) {
				counter += 1;
				list.items.push(word);
			}
		}
		return {
			"resources": {},
			"list": list
		};
	};


	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	var compose = function (word) {
		"use strict";
		var text, i, obligatorySet;
	
		if (word.length === 0) {
			return "";
		}
		if (word.length === 1) {
			return word[0].join(", ");
		}
		text = "";
		for (i = 0; i < word.length; i += 1) {
			obligatorySet = word[i];
			text += [
				i + 1,
				". ",
				obligatorySet.join(", "),
				" "
			].join("");
		}
		return text.trim();
	};
	
	
	/*
		Copyright 2012, Marten de Vries
	
		This file is part of OpenTeacher.
	
		OpenTeacher is free software: you can redistribute it and/or modify
		it under the terms of the GNU General Public License as published by
		the Free Software Foundation, either version 3 of the License, or
		(at your option) any later version.
	
		OpenTeacher is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
		GNU General Public License for more details.
	
		You should have received a copy of the GNU General Public License
		along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.
	*/
	
	/*global compose: false */
	var composeList;
	
	composeList = (function () {
		"use strict";
		var escape, equalsRe, tabRe;
	
		equalsRe = new RegExp("[^\\\\](=)");
		tabRe = new RegExp("[^\\\\](\t)");
	
		escape = function (data) {
			var i;
	
			//(+ 1 because we want the '=', not the thing that isn't a
			//slash)
			i = data.search(equalsRe) + 1;
			if (i) {
				//+ 1 here to make sure the '=' isn't double included.
				data = data.slice(0, i) + "\\=" + data.slice(i + 1);
			}
			//same for tab
			i = data.search(tabRe) + 1;
			if (i) {
				data = data.slice(0, i) + "\\\t" + data.slice(i + 1);
			}
			return data;
		};
	
		return function (container) {
			var items, result, i, questions, answers;
	
			items = container.list.items;
			result = "";
			for (i = 0; i < items.length; i += 1) {
				questions = compose(items[i].questions);
				answers = compose(items[i].answers);
				result += escape(questions) + " = " + escape(answers) + "\n";
			}
			if (!result) {
				return "\n";
			}
			return result;
		};
	}());

	return {
		//words string functions
		parse: parse,
		compose: compose,
		check: check,

		//list string functions
		parseList: parseList,
		composeList: composeList
	}
}())
