var sharePage = (function () {
	var currentUsername, currentDb, currentShareName, cancelChanges;

	function queryOpts(shareName) {
		return {startkey: [currentShareName], endkey: [currentShareName, {}, {}]};
	}

	function retranslate() {
		$("#back-to-shares").text(_("Back to the shares page"));
		$("#share-lists .last-edited-label").text(_("Last edited:"));
		$("#share-lists .view-link").text(_("View"));
		$("#share-lists .take-over-link").text(_("Take over"));
		//TRANSLATORS: as in ATOM/RSS feeds.
		//TRANSLATORS: (https://en.wikipedia.org/wiki/Web_feed)
		$("#share-feed-link").attr("title", _("Feed"));
	}
	session.languageChanged.handle(retranslate);

	function onSharedListsChange() {
		currentDb.query("shares/by_name", queryOpts(), function (err, resp) {
			$("#share-lists").empty();
			$.each(resp.rows, function (i, row) {
				var list = tmpl("share-list-template", {
					doc: row.value,
					shareName: currentShareName,
					username: currentUsername,
					dbName: currentDbName(),
					classes: i % 2 ? "even" : "odd"
				});
				$("#share-lists").append(list);
			});
			//update ui translation
			retranslate();
		});
	}

	$(function () {
		$("#back-to-shares").click(function () {
			//calling directly doesn't work it seems.
			history.back();
		});
	});

	function currentDbName() {
		return "shared_lists_" + currentUsername;
	}

	function onSyncError() {
		if (err.status === 404) {
			//'bypassed' means 'not routed' -> gives the 404 page.
			crossroads.bypassed.dispatch("shares/" + username + "/" + shareName);
		}
	}

	var shareRoute = crossroads.addRoute("shares/{username}/{shareName}");
	shareRoute.matched.add(function (username, shareName) {
		currentUsername = username;
		currentShareName = shareName;
		currentDb = new PouchDB(currentDbName());

		sync.start(currentDbName());
		sync.errorsFor(currentDbName()).handle(onSyncError);
		cancelChanges = sync.onChangesFor(currentDbName(), onSharedListsChange);

		$("#share-page .subheader").text(shareName);

		$("#share-feed-link").attr(
			"href",
			COUCHDB_HOST + "/" + currentDbName() + "/_design/shares/_list/feed/by_name?startkey=" + JSON.stringify(queryOpts().startkey) + "&endkey=" + JSON.stringify(queryOpts().endkey)
		);

		show("#share-page");
	});
	shareRoute.switched.add(function () {
		sync.errorsFor(currentDbName()).unhandle(onSyncError);
		cancelChanges();
		sync.stop(currentDbName());
	});

	crossroads.addRoute("shares/{username}/{shareName}/{docId}/take-over", function (username, shareName, docId) {
		//first set up the base page
		crossroads.parse("shares/" + username + "/" + shareName);

		var url = "shares/" + username + "/" + shareName + "/" + docId + "/take-over";
		if (!session.loggedIn) {
			session.next = url;
			hasher.replaceHash("login");
			return;
		}
		var db = new PouchDB(currentDbName());
		db.get(docId, function (err, resp) {
			if (resp) {
				//make it act like a new doc. This way, we don't get
				//conflicts when user a shares a doc which user b takes
				//over and shares which user a takes over again.
				//(yeah, pretty unlikely. :P)
				delete resp._id;
				delete resp._rev;
				session.userDbs.private.post(resp);
			} else {
				//somehow the doc isn't found -> 404.
				crossroads.bypassed.dispatch(url);
			}
		});
	});
}());
