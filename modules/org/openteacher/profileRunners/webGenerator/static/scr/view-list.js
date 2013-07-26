var viewList = (function () {
	function onViewList(id) {
		listsDb.get(id, function (err, resp) {
			$("#title").val(resp.title);
			$("#shares").val(resp.shares.join(", "));
			$("#list-page").data("id", id);
			$("#list-page").data("rev", resp._rev);
			$("#list tbody").empty();
			for (var i = 0; i < resp.items.length; i += 1) {
				addRow(resp.items[i]);
			}
			newRow();

			$("#tests-part").hide();
			testsDb.query("tests/by_list_id", {
				startkey: [id],
				endkey: [id, {}],
				descending: true
			}, testsLoaded);
		});
	}

	function addRow(item) {
		var row = renderTemplate("#list-template", {
			item: item,
			compose: logic.compose
		});
		$("#list tbody").append(row);
	}

	function newRow() {
		var lastId = parseInt($("#list tbody tr:last").data("id"), 10);
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
				tbody.append(renderTemplate("#tests-template", {
					test: resp.rows[i].value,
					calculateNote: logic.calculateNote,
					classes: tbody.children().length % 2 ? "even" : "odd"
				}));
			}
			$("#tests-part").show();
		}
		show("#list-page", function () {
			$("#list tbody tr:last .question-input").focus();
		});
	}

	function onSaveList() {
		var page = $("#list-page");
		var id = page.data("id");
		var rev = page.data("rev");

		listsDb.get(id, function (err, doc) {
			//supplement the already existing doc with the saved values.
			doc._rev = rev;
			doc.title = $("#title").val();

			var sharesText = $("#shares").val();
			var splittedShares = sharesText.split(new RegExp("[;,]"));
			var unfilteredShares = splittedShares.map(function (s) {
				return s.trim();
			});
			doc.shares = unfilteredShares.filter(function (s) {return s !== "";});

			//make an object that maps id to items, so we can later
			//update items instead of replacing them.
			var oldItemsList = doc.items;
			var oldItems = {};
			$(oldItemsList).each(function () {
				oldItems[this.id] = this;
			});

			doc.items = [];
			//last row is always empty.
			$("#list tbody tr:not(:last)").each(function () {
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
			listsDb.put(doc, function (err, resp) {
				//set the new rev to the page, so it can be saved again
				//without conflicts.
				page.data("rev", resp.rev);
			});
		});
	}

	$(function () {
		$("#back-from-list-page").click(function () {
			show("#lists-page");
		});
		$("#save-list").click(onSaveList);

		$("#list tbody").on("keyup", "#list input:last", function (event) {
			//9 is 'tab'.
			if (event.which !== 9) {
				newRow();
			}
		});

		$("#tests").on("change", ".finished-checkbox", function () {
			//undo the user action, like if the checkbox is disabled.
			//(not using that because that looks greyed out)
			var checkbox = $(this);
			if (checkbox.attr("checked")) {
				checkbox.removeAttr("checked");
			} else {
				checkbox.attr("checked", "checked");
			}
		});

	});

	return onViewList;
}());
