#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

import HTMLParser

class HocrParser(HTMLParser.HTMLParser):
	def __init__(self, *args, **kwargs):
		HTMLParser.HTMLParser.__init__(self, *args, **kwargs)

		self.rects = []
		self.capturingData = False

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if tag == "span" and attrs.get("class") == "ocr_line":
			positions = attrs.get("title")
			parts = positions.split(" ")

			self.rects.append({
				"x": int(parts[1]),
				"y": int(parts[2]),
				"width": int(parts[3]) - int(parts[1]),
				"height": int(parts[4]) - int(parts[2]),
				"text": u"",
			})
			self.capturingData = True

	def handle_endtag(self, tag):
		if tag == "span":
			self.capturingData = False

	def handle_data(self, data):
		if self.capturingData:
			self.rects[-1]["text"] += data

class OcrWordListLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OcrWordListLoaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ocrWordListLoader"
		self.requires = (
			self._mm.mods(type="wordsStringParser"),
			self._mm.mods(type="ocrRecognizer"),
		)

	_parse = property(lambda self: self._modules.default("active", type="wordsStringParser").parse)
	_imageToHocr = property(lambda self: self._modules.default("active", type="ocrRecognizer").toHocr)

	def _sortAndDetectRows(self, rects, margin):
		rects = sorted(rects, key=lambda rect: rect["y"])

		lastElement = None
		rows = []
		for rect in rects:
			if lastElement and rect["y"] - lastElement["y"] < margin:
				currentRow.append(rect)
			else:
				currentRow = [rect]
				rows.append(currentRow)
			lastElement = rect
		return rows

	def _sortAndDetectColumns(self, rows, margin):
		#vertical margin can safely be a bit higher. 4 makes it tolerate
		#a tab.
		margin *= 4
		columnsTable = []
		for row in rows:
			row = sorted(row, key=lambda rect: rect["x"])

			lastElement = None
			columns = []
			columnsTable.append(columns)
			for rect in row:
				if lastElement and rect["x"] - lastElement["x"] < margin:
					currentColumn.append(rect)
				else:
					currentColumn = [rect]
					columns.append(currentColumn)
				lastElement = rect
		return columnsTable

	def _hocrToRects(self, hocr):
		parser = HocrParser()
		parser.feed(hocr)
		return parser.rects

	def _makeFilteredRowsFromColumnsTable(self, columnsTable):
		filteredRows = []
		for row in columnsTable:
			if len(row) == 1:
				if not filteredRows:
					continue
				filteredRows[-1].extend(row[0])
			else:
				filteredRows.append(row[0] + row[-1])
		return filteredRows

	def _columnsTableToLesson(self, columnsTable):
		lesson = {
			"list": {
				"items": [],
			},
			"resources": {},
		}
		for id, row in enumerate(columnsTable):
			if len(row) != 2:
				#could happen if the row filtering suddenly gave more
				#than two columns back. Not likely, but possible.
				continue
			questionColumn, answerColumn = row
			questions = " ".join([question["text"] for question in questionColumn])
			answers = " ".join([answer["text"] for answer in answerColumn])

			lesson["list"]["items"].append({
				"id": id,
				"questions": self._parse(questions),
				"answers": self._parse(answers),
			})
		return lesson

	def loadWordList(self, imagePath):
		#ocr image
		hocr = self._imageToHocr(imagePath)
		rects = self._hocrToRects(hocr)

		if not rects:
			return self._columnsTableToLesson([])
		margin = rects[0]["height"] * 0.5

		rows = self._sortAndDetectRows(rects, margin)
		columnsTable = self._sortAndDetectColumns(rows, margin)

		filteredRows = self._makeFilteredRowsFromColumnsTable(columnsTable)
		filteredColumnsTable = self._sortAndDetectColumns(filteredRows, margin)

		return self._columnsTableToLesson(filteredColumnsTable)

	def enable(self):
		self._modules = next(iter(self._mm.mods(type="modules")))

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return OcrWordListLoaderModule(moduleManager)
