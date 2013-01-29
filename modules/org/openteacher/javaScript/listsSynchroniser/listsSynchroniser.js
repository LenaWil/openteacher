/*
	Copyright 2013, Marten de Vries

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

/*global $, localStorage */

var ListsSynchroniser;

ListsSynchroniser = (function() {
	"use strict";

	var lastUpdate, getOnlineIndex, getOnlineList;

	//the moment this feature was first developed. It's guaranteed to be
	//in the past at use time.
	lastUpdate = "2013-01-28T20:45:17.642173";

	localStorage.lists = localStorage.lists || {};

	getOnlineIndex = function () {
		//handle authentication
		return $.getJSON("/lists/");
	};

	getOnlineList = function (url) {
		//handle authentication
		return $.getJSON(url);
	};

	return {
		synchronize: function () {
			var onlineIndex, title, list;

			onlineIndex = getOnlineIndex();
			for (title in onlineIndex) {
				if (onlineIndex.hasOwnProperty(title)) {
					list = onlineIndex[title];

					if (list.modified > lastUpdate) {
						localStorage.lists[title] = getOnlineList(list.url);
					}
				}
			}
		},
		getLists: function () {
			return localStorage.lists;
		}
	};
});
