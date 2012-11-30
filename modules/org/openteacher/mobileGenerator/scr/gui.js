/*
	Copyright 2012, Marten de Vries
	Copyright 2012, Milan Boers

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

/*global $: false, translationIndex: false, logic: false, JsDiff: false */
/*jslint nomen: true, browser: true */

(function () {
	"use strict";
	var gui, menuDialog, optionsDialog, enterTab, teachTab;

	menuDialog = (function () {
		var newList, askWhichListToLoad, loadList, askSaveName,
			saveList, getLessons, saveLessons, askWhichListToRemove,
			removeList;

		getLessons = function () {
			return JSON.parse(localStorage.lessons || "{}");
		};

		saveLessons = function (lessons) {
			localStorage.lessons = JSON.stringify(lessons);
		};

		newList = function () {
			$.mobile.changePage($("#enter-page"));
			enterTab.newList();
		};

		removeList = function (name) {
			var lessons;

			lessons = getLessons();
			delete lessons[name];
			saveLessons(lessons);

			history.go(-2);
		};

		askWhichListToRemove = function () {
			var html, lists, name, listView;

			html = "";

			//fill the list view again with newly retrieved lists.
			lists = getLessons();
			for (name in lists) {
				if (lists.hasOwnProperty(name)) {
					html += "<li><a href='#'>" + name + "</a></li>";
				}
			}

			listView = $("#remove-listview");
			listView.html(html);
			try {
				listView.listview("refresh");
			} catch (e) {}
			$.mobile.changePage($("#remove-dialog"));
		};

		loadList = function (name) {
			var lesson;

			//load the associated lesson
			lesson = getLessons()[name];
			//and load that lesson into the enter tab
			enterTab.fromLesson(lesson);
			//then, switch to the enter tab.
			$.mobile.changePage($("#enter-page"));
		};

		askWhichListToLoad = function () {
			var html, lists, name, listView;

			html = "";

			//fill the list view again with newly retrieved lists.
			lists = getLessons();
			for (name in lists) {
				if (lists.hasOwnProperty(name)) {
					html += "<li><a href='#'>" + name + "</a></li>";
				}
			}

			listView = $("#load-listview");
			listView.html(html);
			try {
				listView.listview("refresh");
			} catch (e) {}
			$.mobile.changePage($("#load-dialog"));
		};

		askSaveName = function () {
			$.mobile.changePage($("#save-dialog"));
		};

		saveList = function (force) {
			var lessons, nameBox, name, lesson;

			nameBox = $("#save-name-box");
			name = nameBox.val();

			lessons = getLessons();

			if (lessons.hasOwnProperty(name) && !force) {
				//ask if the user wants to overwrite
				$("#overwrite-popup").popup("open");
				return;
			}
			//clean name box
			nameBox.val("");

			//do saving
			lesson = enterTab.toLesson();
			if (lesson) {
				lessons[name] = lesson;
				saveLessons(lessons);
			}

			//update ui
			history.go(-2);
		};
		return {
			setupUi: function () {
				$("#new-list-button").click(newList);
				$("#load-list-button").click(askWhichListToLoad);
				$("#save-list-button").click(askSaveName);
				$("#remove-list-button").click(askWhichListToRemove);

				$("#save-done-button").click(function () {
					saveList(false);
				});
				$("#overwrite-yes-button").click(function () {
					saveList(true);
				});
				$("#overwrite-no-button").click(askSaveName);

				//for all 'a's in #load-listview, so also ones added
				//later on.
				$("#load-listview").on("click", "a", function () {
					loadList($(this).text());
				});
				//same for remove
				$("#remove-listview").on("click", "a", function () {
					removeList($(this).text());
				});
			},
			retranslate: function (_) {
				//base dialog
				$("#menu-header").text(_("Menu"));
				$("#new-list-button").text(_("New list"));
				$("#load-list-button").text(_("Load list"));
				$("#save-list-button").text(_("Save list"));
				$("#remove-list-button").text(_("Remove list"));
				$("#options-button .ui-btn-text").text(_("Options"));

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
				$("#load-listview").attr("data-filter-placeholder", _("Filter lists..."));

				//remove dialog
				$("#remove-header").text(_("Remove list"));
				$("#remove-explanation").text(_('Please choose the list you want to remove.'));
				$("#remove-listview").attr("data-filter-placeholder", _("Filter lists..."));
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
				$("#copyright-info-link").text(_("Copyright info"));
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
				//keyup so jqm adjusts the textarea size.
				$("#list-textarea").val(newText).keyup();
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
			fromLesson: function (lesson) {
				var text;

				text = logic.composeList(lesson);
				$("#list-textarea").val(text);
			},
			toLesson: function () {
				var text, lesson;

				text = $("#list-textarea").val();

				try {
					lesson = logic.parseList(text);
				} catch (exc) {
					if (exc.name === "SeparatorError") {
						$("#missing-separator-popup").popup("open");
						return false;
					}
					throw exc;
				}
				return lesson;
			}
		};
	}());

	teachTab = (function () {
		var onCheck, onSkip, onCorrectAnyway, lessonDone, newItem,
			sliderToProgressBar, lessonType, currentItem, calculateNote,
			noteMessage, backToEnterTab, animationEnd;

		onCheck = function () {
			var answerBox, text, givenAnswer, result, correctionLabel,
				goodAnswer, diff, diffText, i;

			answerBox = $("#answer-box");
			text = answerBox.val();
			givenAnswer = logic.parse(text);
			result = logic.check(givenAnswer, currentItem);

			//disable the button for now, it stays that way or it's
			//re-enabled *after* the animation
			$("#correct-anyway-button").button("disable");
			if (result.result === "right") {
				lessonType.setResult(result);
			} else {
				correctionLabel = $("#correction-label");

				goodAnswer = logic.compose(currentItem.answers);
				diff = JsDiff.diffChars(text, goodAnswer);
				if (diff.length > 4) {
					//differs too much
					correctionLabel.html(goodAnswer);
				} else {
					//diff is close enough, show it.
					diffText = "";
					for (i = 0; i < diff.length; i += 1) {
						if (diff[i].added) {
							diffText += "<span style='color: green; text-decoration: underline;'>" + diff[i].value + "</span>";
						} else if (diff[i].removed) {
							diffText += "<span style='color: red; text-decoration: underline;'>" + diff[i].value + "</span>";
						} else {
							diffText += diff[i].value;
						}
					}
					correctionLabel.html(diffText);
				}
				answerBox.hide();
				correctionLabel.show().fadeOut(4000, function () {
					animationEnd(answerBox, result);
				});
			}
		};

		animationEnd = function (answerBox, result) {
			answerBox.show();
			$("#correct-anyway-button").button("enable");

			lessonType.setResult(result);
		};

		onSkip = function () {
			lessonType.skip();
		};

		onCorrectAnyway = function () {
			lessonType.correctLastAnswer({"result": "right"});
			$("#correct-anyway-button").button("disable");
		};

		calculateNote = function (test) {
			var good, total, i, result;

			good = 0;
			total = test.results.length;
			for (i = 0; i < test.results.length; i += 1) {
				result = test.results[i];
				if (result.result === "right") {
					good += 1;
				}
			}
			return Math.round(good / total * 100).toString() + "%";
		};

		lessonDone = function () {
			var test, note;

			test = lessonType.list.tests[lessonType.list.tests.length - 1];
			note = calculateNote(test);

			//free lesson objects
			lessonType = undefined;
			currentItem = undefined;

			//show results
			$("#result-msg").text(noteMessage.replace("%s", note));
			$.mobile.changePage($("#result-dialog"));
		};

		newItem = function (item) {
			var slider;

			currentItem = item;

			//set question
			$("#question-label").text(logic.compose(item.questions));

			//empty answer box
			$("#answer-box").val("");

			//update progress bar
			slider = $("#progress-bar");
			slider.attr("max", lessonType.totalItems);
			slider.val(lessonType.askedItems);
			try {
				slider.slider("refresh");
			} catch (e) {}

			//focus to input box when jqm is fully set up.
			setTimeout(function () {
				$("#answer-box").focus();
			}, 0);
		};

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

		backToEnterTab = function () {
			$.mobile.changePage($("#enter-page"));
		};
		$(document).on("pageinit", sliderToProgressBar);

		return {
			setupUi: function () {
				$("#check-button").click(onCheck);
				$("#skip-button").click(onSkip);
				$("#correct-anyway-button").click(onCorrectAnyway);

				$("#result-ok-button").click(backToEnterTab);
				$("#teach-page").keydown(function (event) {
					if (event.which === 13) {
						//enter key
						$("#check-button").click();
					}
				});
			},

			retranslate: function (_) {
				//ui itself
				$("#teach-me-header").text(_("Teach me!"));
				$("#question-label-label").text(_("Question:"));
				$("#answer-box-label").text(_("Answer:"));
				$("#check-button").text(_("Check!"));
				$("#skip-button").text(_("Skip"));
				$("#correct-anyway-button").text(_("Correct anyway"));

				//result popup
				$("#result-header").text(_("Test completed!"));
				$("#result-title").text(_("Test completed!"));
				$("#result-ok-button").text(_("Ok"));
				noteMessage = _("Your note: %s");
			},

			doLesson: function (lesson) {
				var i, indexes;

				indexes = [];
				for (i = 0; i < lesson.list.items.length; i += 1) {
					indexes.push(i);
				}
				lessonType = new logic.LessonType(lesson.list, indexes);
				lessonType.newItem.handle(newItem);
				lessonType.lessonDone.handle(lessonDone);
				lessonType.start();

				try {
					$("#correct-anyway-button").button("disable");
				} catch (e) {}
			}
		};
	}());

	gui = (function () {
		var setupDone, main, doRetranslate, retranslate, tabChange,
			startLesson, onDeviceReady, onMenuKeyDown;

		setupDone = false;

		doRetranslate = function (_) {
			//header menu
			//.ui-btn-text because it seems close to impossible to
			//refresh a button based on a <a>-tag...
			$(".menu-dialog-link .ui-btn-text").text(_("Menu"));

			//tabs
			$(".enter-page-link .ui-btn-text").text(_("Enter list"));
			$(".teach-page-link .ui-btn-text").text(_("Teach me!"));
			//$("#list-management-dialog-link .ui-btn-text").text(_("List management"));

			//retranslate all tabs & dialogs
			enterTab.retranslate(_);
			teachTab.retranslate(_);
			menuDialog.retranslate(_);
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

		onDeviceReady = function () {
			//Connect buttons to functions
			$(document).on("menubutton", onMenuKeyDown);
		};

		onMenuKeyDown = function () {
			//Make the menu button on Android work
			$.mobile.changePage("#menu-dialog", "pop", false, true);
		};

		main = function () {
			//translate the GUI for the first time. Delay the other set
			//up things until that's done, because they might depend
			//on the translations.
			retranslate(function () {
				if (!setupDone) {
					//setup UI
					enterTab.setupUi();
					teachTab.setupUi();
					menuDialog.setupUi();

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
			var lesson;

			lesson = enterTab.toLesson();
			if (!lesson) {
				return false;
			}
			teachTab.doLesson(lesson);
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
					$(".teach-page-link").removeClass("ui-btn-active ui-state-persist");
					$(".enter-page-link").addClass("ui-btn-active ui-state-persist");

					//not going to that page
					event.preventDefault();
				}
			}
		};

		//setup for a local environment
		$.ajaxSetup({
			beforeSend: function (xhr) {
				if (xhr.overrideMimeType) {
					xhr.overrideMimeType("application/json");
				}
			}
		});

		/* OS matching themes */
		(function () {
			var ua, isIos, isAndroid;

			ua = navigator.userAgent.toLowerCase();
			isIos = !(ua.indexOf("ipod") === -1 && ua.indexOf("iphone") === -1 && ua.indexOf("ipad") === -1);
			isAndroid = ua.indexOf("android") !== -1;

			if (isIos) {
				//page transition
				$(document).on("mobileinit", function () {
					$.mobile.defaultPageTransition = "slide";
				});
				//add css
				$(function () {
					$("head").append("<link type='text/css' rel='stylesheet' href='css/themes/ios/styles.css' />");
				});
			}
			if (isAndroid) {
				//change default swatch to something looking good
				//in android
				$.mobile.page.prototype.options.contentTheme = "d";

				$(function () {
					//add css
					$("head").append("<link type='text/css' rel='stylesheet' href='css/themes/android/android-theme.css' />");

					//set theme class
					$("body").addClass("android");
				});
			}
		}());

		//initialization of pages (retranslating etc.)
		$(document).on("pageinit", main);

		//handle page change, so a lesson can be started etc.
		$(document).on("pagebeforechange", tabChange);

		//do what needs to be done after the device is ready
		$(document).on("deviceready", onDeviceReady);

		return {
			retranslate: retranslate
		};
	}());
}());
