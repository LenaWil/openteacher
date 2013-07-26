(function () {
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
			"title": "New list",
			"items": [],
			"shares": [],
			"lastEdited": new Date()
		}, function (err, resp) {
			viewList(resp.id);
		});
	}

	function onListLinkClicked() {
		var tr = $(this).parents("tr")[0];
		var id = $(tr).data("id");
		({
			"#view-list": viewList,
			"#learn-list": learnList
		})[$(this).attr("href")](id);
		return false;
	}

	$(function () {
		$("#remove-selected").click(onRemoveSelected);
		$("#new-list").click(onNewList);
		$("#lists").on("click", "a", onListLinkClicked);
	});
}());
