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

/*global $: false, translationIndex: false, logic: false */
/*jslint nomen: true, browser: true */

(function () {
	"use strict";
	var gui, listManagementDialog, optionsDialog, enterTab, teachTab;

	listManagementDialog = (function () {
		var newList, askWhichListToLoad, loadList, askSaveName, saveList, getLists, saveLists;

		getLists = function () {
			return JSON.parse(localStorage.lists || "{}");
		};

		saveLists = function (lists) {
			localStorage.lists = JSON.stringify(lists);
		};

		newList = function () {
			$.mobile.changePage($("#enter-page"));
			enterTab.newList();
		};

		loadList = function (item) {
			var name, list;

			//get name out of clicked element
			name = $(item).text();
			//load the list associated list
			list = getLists()[name];
			//and load that list into the enter tab
			enterTab.fromList(list);
			//then, switch to the enter tab.
			$.mobile.changePage($("#enter-page"));
		};

		askWhichListToLoad = function () {
			var html, lists, name, listView;

			html = "";

			//fill the list view again with newly retrieved lists.
			lists = getLists();
			for (name in lists) {
				if (lists.hasOwnProperty(name)) {
					html += "<li><a href='#'>" + name + "</a></li>";
				}
			}

			listView = $("#load-listview")
			listView.html(html)
			try {
				listView.listview('refresh');
			} catch (e) {}
			$.mobile.changePage($("#load-dialog"));
		};

		askSaveName = function () {
			$.mobile.changePage($("#save-dialog"));
		};

		saveList = function (force) {
			var lists, nameBox, name, list;

			nameBox = $("#save-name-box");
			name = nameBox.val();

			lists = getLists();

			if (lists.hasOwnProperty(name) && !force) {
				//ask if the user wants to overwrite
				$("#overwrite-popup").popup("open");
				return;
			}
			//clean name box
			nameBox.val("");

			//do saving
			lists[name] = enterTab.toList();
			saveLists(lists);

			//update ui
			history.go(-2);
		}
		return {
			setupUi: function () {
				$("#new-list-button").click(newList);
				$("#load-list-button").click(askWhichListToLoad);
				$("#save-list-button").click(askSaveName);

				$("#save-done-button").click(function () {saveList(false); });
				$("#overwrite-yes-button").click(function () {saveList(true); });
				$("#overwrite-no-button").click(askSaveName);

				//for all 'a's in #load-listview, so also ones added
				//later on.
				$("#load-listview").on("click", "a", function () {loadList(this)});
			},
			retranslate: function (_) {
				//base dialog
				$("#list-management-header").text(_("List management"));
				$("#new-list-button").text(_("New list"));
				$("#load-list-button").text(_("Load list"));
				$("#save-list-button").text(_("Save list"));
//				$("#import-from-file-button").text(_("Import from file"));
//				$("#export-to-file-button").text(_("Export to file"));

				//save dialog (& overwrite popup)
				$("#save-header").text(_("Save list"));
				$("#save-explanation").text(_("Please choose a name for the current list, so it can be saved."));
				$("#save-name-box-label").text(_("Name:"));
				$("#save-done-button").text(_("Done"));

				$("#overwrite-header").text(_("Warning"));
				$("#overwrite-title").text(_("There is already a list named like that."));
				$("#overwrite-msg").text(_("If you continue, it will be overwritten. Continue?"));
				$("#overwrite-yes-button").text(_("Yes"));
				$("#overwrite-no-button").text(_("No"));

				//load dialog
				$("#load-header").text(_("Load list"));
				$("#load-explanation").text(_("Please choose the list you want to load."));
			}
		};
		
	}());

	optionsDialog = (function () {
		var getLanguage, languageChanged;

		getLanguage = function () {
			if (localStorage.language === undefined) {
				//first time running
				if (translationIndex.hasOwnProperty(navigator.language)) {
					//first try the exact browser locale
					localStorage.language = navigator.language;
				} else if (translationIndex.hasOwnProperty(navigator.language.split("-")[0])) {
					//then the generic one
					localStorage.language = navigator.language.split("-")[0];
				} else {
					//if all else fails...
					localStorage.language = "en";
				}
			}
			return translationIndex[localStorage.language];
		};

		languageChanged = function () {
			localStorage.language = $("option:selected", this).attr("name");
			gui.retranslate();
		};

		return {
			setupSettings: function () {
				var langCode, select;

				//language
				select = $("#language-select");

				//fill combobox
				for (langCode in translationIndex) {
					if (translationIndex.hasOwnProperty(langCode)) {
						select.append("<option name='" + langCode + "'>" + translationIndex[langCode].name + "</option>");
					}
				}

				//set current value
				select.val(getLanguage().name);

				//register handler
				select.change(languageChanged);
			},
			retranslate: function (_) {
				$("#options-header").text(_("Options"));
				$("#language-select-label").text(_("Language:"));
			},
			getLanguage: getLanguage
		};
	}());

	enterTab = (function () {
		var closePopup, newText;

		closePopup = function () {
			$("#missing-separator-popup").popup("close");
		};

		return {
			newList: function () {
				$("#list-textarea").val(newText).textinput();
			},
			setupUi: function () {
				$("#list-textarea").tabOverride();
				$("#missing-separator-ok-button").click(closePopup);
			},
			retranslate: function (_) {
				$("#enter-list-header").text(_("Enter list"));
				$("#word-list-label").text(_("Word list:"));
				newText = _("Welcome = Welkom\nto = bij\nOpenTeacher mobile = OpenTeacher mobile\n");

				$("#missing-separator-header").text(_("Error"));
				$("#missing-separator-title").text(_("Missing equals sign or tab"));
				$("#missing-separator-msg").text(_("Please make sure every line contains an '='-sign or tab between the questions and answers."));
				$("#missing-separator-ok-button").text(_("Ok"));
			},
			fromList: function (list) {
				var text;

				text = logic.composeList(list);
				$("#list-textarea").val(text);
			},
			toList: function () {
				var text, list;

				text = $("#list-textarea").val();

				try {
					list = logic.parseList(text);
				} catch (exc) {
					if (exc.name === "SeparatorError") {
						$("#missing-separator-popup").popup("open");
						return false;
					}
					throw exc;
				}
				return list;
			}
		};
	}());

	teachTab = (function () {
		var sliderToProgressBar;

		sliderToProgressBar = function () {
			//It's a hack. But it works.
			$("#progress-bar")
				.hide()

				.siblings(".ui-slider")
				.css("margin", 6)
				.width("99%")
				.off("vmousedown")

				.children(".ui-slider-handle")
				.hide()

				.siblings(".ui-slider-bg")
				.css("cursor", "auto");
		};

		return {
			setupUi: function () {
				sliderToProgressBar();
			},
			retranslate: function (_) {
				$("#teach-me-header").text(_("Teach me!"));
				$("#question-label-label").text(_("Question:"));
				$("#answer-box-label").text(_("Answer:"));
				$("#check-button").text(_("Check!"));
				$("#skip-button").text(_("Skip"));
				$("#correct-anyway-button").text(_("Correct anyway"));
			},
			doLesson: function (list) {
				//FIXME
			}
		};
	}());

	gui = (function () {
		var setupDone, main, doRetranslate, retranslate, tabChange,
			startLesson;

		//setup for a local environment
		$.ajaxSetup({
			beforeSend: function (xhr) {
				if (xhr.overrideMimeType) {
					xhr.overrideMimeType("application/json");
				}
			}
		});

		setupDone = false;

		doRetranslate = function (_) {
			//header menu
			//.ui-btn-text because it seems close to impossible to
			//refresh a button based on a <a>-tag...
			$(".options-dialog-link .ui-btn-text").text(_("Options"));

			//footer menu
			$("#enter-page-link .ui-btn-text").text(_("Enter list"));
			$("#teach-page-link .ui-btn-text").text(_("Teach me!"));
			$("#list-management-dialog-link .ui-btn-text").text(_("List management"));

			//retranslate all tabs & dialogs
			enterTab.retranslate(_);
			teachTab.retranslate(_);
			listManagementDialog.retranslate(_);
			optionsDialog.retranslate(_);

			try {
				$("button").button("refresh");
			} catch (e) {
				$("button").button();
			}
		};

		retranslate = function (callback) {
			if (optionsDialog.getLanguage().url === undefined) {
				//english, use a simple pass through function.
				doRetranslate(function (str) {
					return str;
				});
				if (callback) {
					callback();
				}
			} else {
				//download the translation file
				$.get(optionsDialog.getLanguage().url, function (translations) {
					//use it for translating the ui.
					doRetranslate(function (str) {
						return translations[str] || str;
					});
					if (callback) {
						callback();
					}
				});
			}
		};

		main = function () {
			//translate the GUI for the first time. Delay the other set
			//up things until that's done, because they might depend
			//on the translations.
			retranslate(function () {
				//setup UI
				enterTab.setupUi();
				teachTab.setupUi();
				listManagementDialog.setupUi();

				if (!setupDone) {
					//start with a new word list
					enterTab.newList();

					//make sure the options dialog is ready to be shown
					optionsDialog.setupSettings();

					//this part of main() is supposed to only run once.
					setupDone = true;
				}
			});
		};

		startLesson = function () {
			var list;

			list = enterTab.toList();
			if (!list) {
				return false;
			}
			teachTab.doLesson(list);
			return true;
		};

		tabChange = function (event, info) {
			var hash, success;

			if (typeof info.toPage !== "string") {
				return;
			}

			hash = $.mobile.path.parseUrl(info.toPage).hash;
			if (hash === "#teach-page") {
				success = startLesson();
				if (!success) {
					//set the enter tab as active again on the navbar
					//(jqm doesn't seem to do that on preventDefault())
					$("#teach-page-link").removeClass("ui-btn-active ui-state-persist");
					$("#enter-page-link").addClass("ui-btn-active ui-state-persist");

					//not going to that page
					event.preventDefault();
				}
			}
		};

		//initialization of pages (retranslating etc.)
		$(document).on("pageinit", main);

		//handle page change, so a lesson can be started etc.
		$(document).on("pagebeforechange", tabChange);

		return {
			retranslate: retranslate
		};
	}());
}());
