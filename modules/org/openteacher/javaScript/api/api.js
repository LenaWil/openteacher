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

/*global localStorage */

var Api;

Api = (function() {
	"use strict";
	var doHttp, username, password;

	doHttp = function (options) {
		var request;

		request = new XMLHttpRequest();
		if (options.onLoad) {
			request.onLoad = function () {
				var resp = JSON.parse(this.responseText);
				options.onLoad(resp);
			};
		}
		if (options.onError) {
			request.onError = function () {
				var resp = JSON.parse(this.responseText);
				options.onError(this.status, resp);
			};
		}
		request.open(options.method, options.url, true, username, password);
		request.send();
	};

	localStorage.lists = localStorage.lists || {};

	return {
		getLists: function (callback) {
			doHttp({
				method: "get",
				url:"/api/lists/",
				onLoad: function (lists) {
					localStorage.lists = lists;
					callback(lists);
				},
				onError: function () {
					callback(localStorage.lists);
				}
			});
		},
		setCredentials: function (newUsername, newPassword) {
			username = newUsername;
			password = newPassword;
		}
	};
}());

