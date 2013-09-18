var viewPage = (function () {
	var cancelChanges;

	function retranslate() {
		$("#list-part .subheader").text(_("List"));
		$("#title-label").text(_("Title:"));
		$("#shares-label").text(_("Shares:"));
		$("#shares-info-label").text(_("Currently existing shares:"));
		$("#question-lang").attr("placeholder", _("Question language"));
		$("#answer-lang").attr("placeholder", _("Answer language"));
		$("#list-questions-header").text(_("Questions"));
		$("#list-answers-header").text(_("Answers"));
		$(".remove-item").attr("title", _("Remove this item"));

		$("#tests-part .subheader").text(_("Test results"));
		$("#tests-date-header").text(_("Date"));
		$("#tests-note-header").text(_("Note"));
		$("#tests-completed-header").text(_("Completed"));

		$("#back-from-list-page").text(_("Back to the lists page"));
		$("#save-list").text(_("Save"));
		$("#print-list").text(_("Print"));
		$("#download-list").text(_("Download"));
		$("#teach-list").text(_("Teach me!"));

		$("#save-success").text(_("Saved the list succesfully."));
		$("#save-forbidden").text(_("Can't save the document because it contains invalid content. Maybe you used unsafe HTML, or left fields empty that should not be empty?"));
		$("#save-conflict").text(_("Couldn't save the list, because it has been edited elsewhere in the meantime. You can either discard your changes, or save again (overwriting the changes made elsewhere)."));

		$("#download-explanation").text(_("Please choose the file you want to download from the options below. Not sure? Then download the file ending in '.otwd'."));
		$("#close-download").text(_("Close"));

		//TRANSLATORS: used to indicate that a table
		//TRANSLATORS: value is unknown.
		$(".unknown").text(_("-"));
	}
	session.languageChanged.handle(retranslate);

	function loadTests(id, opts, callback) {
		if (typeof opts === "function") {
			callback = opts;
			opts = {};
		}
		opts.startkey = [id];
		opts.endkey = [id, {}];
		session.userDbs.tests.query("tests/by_list_id", opts, callback);
	}

	function addRow(item) {
		$(".last-remove-item").removeClass("last-remove-item");
		var row = tmpl("list-template", {
			item: item,
			compose: logic.compose
		});
		$("#list-items").append(row);
	}

	function newRow() {
		var lastId = parseInt($("#list-items tr:last").data("id"), 10);
		if (isNaN(lastId)) {
			lastId = -1;
		}
		addRow({
			id: lastId + 1
		});
	}

	function testsLoaded(err, resp) {
		if (resp.rows.length !== 0) {
			var tbody = $("#tests tbody");
			tbody.empty();

			for (var i = 0; i < resp.rows.length; i += 1) {
				tbody.append(tmpl("tests-template", {
					test: resp.rows[i].value,
					calculateNote: logic.calculateNote,
					classes: tbody.children().length % 2 ? "even" : "odd"
				}));
			}
			//the tests part contains stuff that needs to be translated.
			retranslate();
			$("#tests-part").show();
		}
		show("#view-page", function () {
			$("#list-items tr:last .question-input").focus();
		});
	}

	function onBackFromListPage() {
		ifNextPageAllowed(function () {
			show("#lists-page");
		});
	}

	function ifNextPageAllowed(callback) {
		var page = $("#view-page");
		var id = page.data("id");
		var rev = page.data("rev");
		session.userDbs.lists.get(id, {rev: rev}, function (err, resp) {
			toList(function (list) {
				//JSON.stringify isn't meant for this, but it seems to
				//work.
				if (
					JSON.stringify(list) === JSON.stringify(resp) ||
					window.confirm(_("There are unsaved changes. Are you sure you want to leave this page?"))
				) {
					callback();
				}
			});
		});
	}

	function toList(callback) {
		var page = $("#view-page");
		var id = page.data("id");
		var rev = page.data("rev");

		session.userDbs.lists.get(id, function (err, doc) {
			//supplement the already existing doc with the saved values.
			doc._rev = rev;
			doc.title = $("#title").val();

			var sharesText = $("#shares").val();
			var splittedShares = sharesText.split(new RegExp("[;,]"));
			var unfilteredShares = splittedShares.map(function (s) {
				return s.trim();
			});
			doc.shares = unfilteredShares.filter(function (s) {return s !== "";});

			doc.questionLanguage = $("#question-lang").val();
			if (!doc.questionLanguage) {
				delete doc.questionLanguage;
			}
			doc.answerLanguage = $("#answer-lang").val();
			if (!doc.answerLanguage) {
				delete doc.answerLanguage;
			}

			//make an object that maps id to items, so we can later
			//update items instead of replacing them.
			var oldItemsList = doc.items;
			var oldItems = {};
			$(oldItemsList).each(function () {
				oldItems[this.id] = this;
			});

			doc.items = [];
			//last row is always empty.
			$("#list-items tr:not(:last)").each(function () {
				var tr = $(this);

				var id = parseInt(tr.data("id"), 10);
				item = oldItems[id];
				if (typeof item === "undefined") {
					item = {id: id};
				}
				item.questions = logic.parse($(".question-input", tr).val());
				item.answers = logic.parse($(".answer-input", tr).val());
				doc.items.push(item);
			});
			if (!doc.items.length) {
				delete doc.items;
			}
			callback(doc);
		});
	}

	function onSaveList() {
		toList(function (list) {
			PouchDBext.withValidation.put(session.userDbs.lists, list, function (err, resp) {
				if (err === null) {
					$("#save-conflict").slideUp();
					$("#save-forbidden").slideUp();
					$("#save-success").slideDown(slideUpAfterTimeout(5000));
				} else {
					$("#save-success").slideUp();
					if (err.forbidden) {
						$("#save-conflict").slideUp();
						$("#save-forbidden").slideDown(slideUpAfterTimeout(8000));
					} else {
						$("#save-forbidden").slideUp();
						$("#save-conflict").slideDown(slideUpAfterTimeout(8000));
					}
				}

				//query the db to get the latest rev (on success it's in
				//the resp too, but not on err.)
				session.userDbs.lists.get(list._id, function (err, resp) {
					//set the new rev to the page, so it can be saved again
					//without conflicts.
					$("#view-page").data("rev", resp._rev);
				});
			});
		});
	}

	function onTeachList () {
		ifNextPageAllowed(function () {
			learnPage.learnList($("#view-page").data("id"));
		});
	}

	function onPrintList() {
		var id = $("#view-page").data("id");
		PouchDBext.show(session.userDbs.lists, "lists/print/" + id, function (err, resp) {
			var frame = $("#print-frame")[0];
			var doc = frame.contentDocument;
			doc.open();
			doc.write(resp.body);
			doc.close();
			frame.contentWindow.print();
		});
	}

	function onLastListInputKeyUp(event) {
		//9 is 'tab'.
		if (event.which !== 9) {
			newRow();
		}
	}

	function onRemoveItem() {
		//remove the current row
		var currentRow = $($(this).parents("tr")[0]);
		var nextRow = currentRow.next();
		currentRow.remove();
		nextRow.find(".question-input").focus();
		return false;
	}

	function onRemoveItemKeyUp(event) {
		if (event.which === 9 && !event.shiftKey) {
			//if tabbing but not backtabbing, go to the next
			//question input.
			var nextRow = $($(this).parents("tr")[0]).next();
			$(nextRow).find(".question-input")[0].focus();
		}
	}

	function onFinishedCheckboxChange() {
		//undo the user action, like if the checkbox is disabled.
		//(not using that because that looks greyed out)
		var checkbox = $(this);
		if (checkbox.attr("checked")) {
			checkbox.removeAttr("checked");
		} else {
			checkbox.attr("checked", "checked");
		}
		//no focus too.
		checkbox.blur();
	}

	function onFinishedCheckboxFocus() {
		//pass the focus to the first button instead
		$("#back-from-list-page").focus();
		return false;
	}

	function onSharedListsChange(change) {
		session.userDbs.shared_lists.query("shares/share_names", {group: true}, function (err, resp) {
			var shareNames = [];
			for (var i = 0; i < resp.rows.length; i += 1) {
				shareNames.push(resp.rows[i].key);
			}
			$("#shares-info").text(shareNames.join(", "));
		});
	}

	$(function () {
		$("#back-from-list-page").click(function () {
			hasher.setHash("lists");
		});
		$("#save-list").click(onSaveList);
		$("#teach-list").click(function () {
			hasher.setHash("lists/" + $("#view-page").data("id") + "/learn");
		});
		$("#print-list").click(onPrintList);
		$("#download-list").click(function () {
			hasher.setHash("lists/" + $("#view-page").data("id") + "/download");
		});

		$("#close-download").click(function () {
			hasher.setHash("lists/" + $("#view-page").data("id") + "/view");
		});

		$("#list-items").on("keyup", "#list input:last", onLastListInputKeyUp);

		$("#list-items").on("click", ".remove-item", onRemoveItem);
		$("#list-items").on("keyup", ".remove-item", onRemoveItemKeyUp);

		$("#tests").on("change", ".finished-checkbox", onFinishedCheckboxChange);
		$("#tests").on("focus", ".finished-checkbox", onFinishedCheckboxFocus);
	});

	var downloadRoute = crossroads.addRoute("lists/{id}/download");
	var firstTimeDownloadRoute = true;
	downloadRoute.matched.add(function (id) {
		var url = "lists/" + id + "/download";
		if (notFoundIfNotLoggedIn(url) === 404) {
			return;
		}
		if (firstTimeDownloadRoute) {
			crossroads.parse("lists/" + id + "/view");
			firstTimeDownloadRoute = false;
			crossroads.parse(url);
		}
		$("#download-part").slideDown();

		servicesRequest({
			url: "/save/supported_extensions",
			success: function (json) {
				var exts = json.result.sort();
				exts = exts.map(function (ext) {
					return "." + ext;
				});

				$("#download-links").empty();
				$.each(exts, function (i, ext) {
					var link = tmpl("link-template", {
						id: id,
						title: $("#title").val(),
						ext: ext
					});
					$("#download-links").append(link);
				});
			},
		});
	});
	downloadRoute.switched.add(function () {
		if (!firstTimeDownloadRoute) {
			$("#download-part").slideUp();
			firstTimeDownloadRoute = true;
		}
	});

	crossroads.addRoute("lists/{id}/download/{extension}", 	function (id, ext) {
		if (notFoundIfNotLoggedIn("lists/" + id + "/download/" + ext) === 404) {
			return;
		}
		crossroads.parse("lists/" + id + "/view");
		session.userDbs.lists.get($("#view-page").data("id"), function (err, list) {
			loadTests(id, function (err, tests) {
				list.tests = tests.rows.map(function (row) {
					return row.value;
				});
				$("<form class='invisible'></form>")
					.attr("action", SERVICES_HOST + "/save")
					.attr("method", "POST")
					.attr("target", "download-frame")
					.append("<input name='username' value='" + session.username + "' />")
					.append("<input name='password' value='" + session.password + "' />")
					.append("<input name='list' value='" + JSON.stringify(list) + "' />")
					.append("<input name='filename' value='" + list.title + ext + "' />")
					.appendTo("body")
					.submit()
					.remove();
			});
		});
	});

	function notFoundIfNotLoggedIn(nextUrl) {
		if (!session.loggedIn) {
			session.next = nextUrl;
			hasher.replaceHash("login");
			return 404;
		}
	}

	viewRoute = crossroads.addRoute("lists/{id}/view")
	viewRoute.matched.add(function (id) {
		if (notFoundIfNotLoggedIn("lists/" + id + "/view") === 404) {
			return;
		}
		if (session.username === "anonymous") {
			$("#download-list").hide();
		} else {
			$("#download-list").show();
		}
		cancelChanges = session.onUserDbChanges.shared_lists(onSharedListsChange);

		session.userDbs.lists.get(id, function (err, resp) {
			if (err) {
				//trigger 404 page.
				viewRoute.switched.dispatch();
				crossroads.bypassed.dispatch();
			}
			$("#title").val(resp.title);
			$("#shares").val(resp.shares.join(", "));
			$("#question-lang").val(resp.questionLanguage || "");
			$("#answer-lang").val(resp.answerLanguage || "");
			$("#view-page").data("id", id);
			$("#view-page").data("rev", resp._rev);
			$("#list-items").empty();
			var items = resp.items || [];
			for (var i = 0; i < items.length; i += 1) {
				addRow(items[i]);
			}
			newRow();

			$("#tests-part").hide();
			loadTests(id, {descending: true}, testsLoaded);
		});
	});
	viewRoute.switched.add(function () {
		if (session.loggedIn) {
			cancelChanges();
		}
	});
}());
