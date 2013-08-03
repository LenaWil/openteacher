var overviewPage = (function () {
	var newListText;

	function retranslate() {
		$("#lists-page .subheader").text(_("Lists overview"));
		$("#remove-selected").text(_("Remove selected lists"));
		$("#new-list").text(_("Create new list"));
		$(".view-link").text(_("View"));
		$(".learn-link").text(_("Teach me!"));
		$(".last-edited-label").text(_("Last edited:"));
	}

	function onRemoveSelected() {
		var deleteDocs = [];

		$("#lists input:checked").each(function () {
			var tr = $(this).parent().parent();

			deleteDocs.push({
				_id: tr.data("id"),
				_rev: tr.data("rev"),
				_deleted: true
			});
		});
		listsDb.bulkDocs({docs: deleteDocs});
	}

	function onNewList() {
		listsDb.post({
			"title": _("New list"),
			"items": [],
			"shares": [],
			"lastEdited": new Date()
		}, function (err, resp) {
			viewPage.viewList(resp.id);
		});
	}

	function onListLinkClicked() {
		var tr = $(this).parents("tr")[0];
		var id = $(tr).data("id");
		({
			"#view-list": viewPage.viewList,
			"#learn-list": learnPage.learnList
		})[$(this).attr("href")](id);
		return false;
	}

	function onListsChange(change) {
		listsDb.query("lists/by_title", function(err, resp) {
			$("#loading-box").slideUp("fast");

			var tbody = $("#lists tbody");
			tbody.empty();
			for (var i = 0; i < resp.rows.length; i += 1) {
				var doc = resp.rows[i].value;

				var rows = renderTemplate("#lists-template", {
					doc: doc,
					classes: tbody.children().length % 2 ? "even" : "odd"
				});
				tbody.append(rows);
			}
			//the lists table contains stuff that needs to be translated.
			retranslate();
		});
	}

	$(function () {
		$("#remove-selected").click(onRemoveSelected);
		$("#new-list").click(onNewList);
		$("#lists").on("click", "a", onListLinkClicked);

		listsChanged.handle(onListsChange);
	});

	return {retranslate: retranslate};
}());
