var sharePage = (function () {
	var currentDb;

	function retranslate() {
		$("#back-to-shares").text(_("Back to the shares page"));
		$("#share-lists .last-edited-label").text(_("Last edited:"));
		$("#share-lists .view-link").text(_("View"));
		$("#share-lists .take-over-link").text(_("Take over"));
		//TRANSLATORS: as in ATOM/RSS feeds.
		//TRANSLATORS: (https://en.wikipedia.org/wiki/Web_feed)
		$("#share-feed-link").attr("title", _("Feed"));
	}

	function onShow(name) {
		currentDb = new PouchDB(currentDbName);

		$("#share-page .subheader").text(name);
		var opts = {startkey: [name], endkey: [name, {}, {}]};

		currentDb.query("shares/by_name", opts, function (err, resp) {
			$("#share-lists").empty();
			$.each(resp.rows, function (i, row) {
				var list = tmpl("share-list-template", {
					doc: row.value,
					dbName: currentDbName,
					classes: i % 2 ? "even" : "odd"
				});
				$("#share-lists").append(list);
			});
			retranslate();
		});

		$("#share-feed-link").attr(
			"href",
			COUCHDB_HOST + "/" + currentDbName + "/_design/shares/_list/feed/by_name?startkey=" + JSON.stringify(opts.startkey) + "&endkey=" + JSON.stringify(opts.endkey)
		);

		show("#share-page");
	}

	function backToShares() {
		sharesPage.show();
	}

	function onTakeOver() {
		//FIXME.
		return false;
	}

	$(function () {
		$("#share-lists").on("click", ".take-over-link", onTakeOver);
		$("#back-to-shares").click(backToShares);
	});

	return {
		show: onShow,
		retranslate: retranslate
	};
}());
