var sharePage = (function () {
	function retranslate() {
		$("#back-to-shares").text(_("Back to the shares page"));
		$("#share-lists .last-edited-label").text(_("Last edited:"));
		$("#share-lists .view-link").text(_("View"));
		$("#share-lists .take-over-link").text(_("Take over"));
		//TRANSLATORS: as in ATOM/RSS feeds.
		//TRANSLATORS: (https://en.wikipedia.org/wiki/Web_feed)
		$("#share-feed-link").attr("title", _("Feed"));
	}
	languageChanged.handle(retranslate);

	$(function () {
		$("#back-to-shares").click(function () {
			//calling directly doesn't work it seems.
			history.back();
		});
	});

	crossroads.addRoute("shares/{username}/{shareName}", function (username, shareName) {
		var currentDbName = "shared_lists_" + username;
		var currentDb = new PouchDB(currentDbName);

		$("#share-page .subheader").text(shareName);
		var opts = {startkey: [shareName], endkey: [shareName, {}, {}]};

		currentDb.query("shares/by_name", opts, function (err, resp) {
			$("#share-lists").empty();
			$.each(resp.rows, function (i, row) {
				var list = tmpl("share-list-template", {
					doc: row.value,
					shareName: shareName,
					username: username,
					dbName: currentDbName,
					classes: i % 2 ? "even" : "odd"
				});
				$("#share-lists").append(list);
			});
			//update ui translation
			retranslate();
		});

		$("#share-feed-link").attr(
			"href",
			COUCHDB_HOST + "/" + currentDbName + "/_design/shares/_list/feed/by_name?startkey=" + JSON.stringify(opts.startkey) + "&endkey=" + JSON.stringify(opts.endkey)
		);

		show("#share-page");
	});

	crossroads.addRoute("shares/{username}/{shareName}/{docId}/take-over", function (username, shareName, docId) {
		//FIXME.
		console.log("takeover " + username + shareName + docId);
	});
}());
