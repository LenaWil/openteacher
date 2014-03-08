var sharesPage = (function () {
	var sharesDb, currentUsername, cancelChanges;

	session.languageChanged.handle(function () {
		$("#shares-page .subheader").text(_("Shares"));
		$("#share-owner-label").text(_("Share owner's username:"));
		$("#find-shares").val(_("Find available shares"));
		$("#share-error").text(_("An error occurred while getting shares. Please make sure that the user exists and that your internet connection works correctly."));
		$("#back-from-shares").text(_("Back"));
	});

	function onSyncError() {
		updateView();
		$("#share-error").slideDown(slideUpAfterTimeout(8000));
	}

	function emptyView() {
		$("#share-links").empty();
	}

	function updateView() {
		sharesDb.query("shares/share_names", {group: true}, function (err, resp) {
			emptyView();
			$.each(resp.rows, function (i, row) {
				var link = tmpl("share-template", {
					row: row,
					username: currentUsername
				});
				$("#share-links").append(link);
			});
		});
	}

	function shareOwnerRequested() {
		var username = $("#share-owner").val();
		this.reset();

		hasher.setHash("shares/" + username);
		return false;
	}

	$(function () {
		$("#share-owner-form").submit(shareOwnerRequested);
		$("#back-from-shares").click(function () {
			history.back();
		});
	});

	crossroads.addRoute("shares", function () {
		emptyView();
		show("#shares-page", function () {
			$("#share-owner").focus();
		});
	});

	function currentDbName() {
		return "shared_lists_" + currentUsername;
	}

	var sharesRoute = crossroads.addRoute("shares/{username}");
	sharesRoute.matched.add(function (username) {
		//first set up the base page
		crossroads.parse("shares");

		currentUsername = username;

		//fixme: remove destroy when not using demo data all the time
		//anymore.
		PouchDB.destroy(currentDbName(), function () {
			sharesDb = new PouchDB(currentDbName());
			sync.start(currentDbName());
			sync.errorsFor(currentDbName()).handle(onSyncError);
			cancelChanges = sync.onChangesFor(currentDbName(), updateView);
		});
	});
	sharesRoute.switched.add(function () {
		if (currentUsername) {
			sync.stop(currentDbName());
			sync.errorsFor(currentDbName()).unhandle(onSyncError);
			cancelChanges();
		}
		currentUsername = undefined;
	});
}());
