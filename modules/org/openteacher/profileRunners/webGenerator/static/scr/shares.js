var sharesPage = (function () {
	var cancel;

	languageChanged.handle(function () {
		$("#shares-page .subheader").text(_("Shares"));
		$("#share-owner-label").text(_("Share owner's username:"));
		$("#find-shares").val(_("Find available shares"));
		$("#share-error").text(_("An error occurred while getting shares. Please make sure that the user exists and that your internet connection works correctly."));
	});

	function whenComplete(err, resp) {
		if (err) {
			updateView();
			$("#share-error").slideDown(slideUpAfterTimeout(8000));
		}
	}

	function emptyView() {
		$("#share-links").empty();
	}

	function updateView(username) {
		emptyView();
		sharesDb.query("shares/share_names", {group: true}, function (err, resp) {
			$.each(resp.rows, function (i, row) {
				var link = tmpl("share-template", {
					row: row,
					username: username
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
	});

	crossroads.addRoute("shares", function () {
		emptyView();
		show("#shares-page", function () {
			$("#share-owner").focus();
		});
	});

	crossroads.addRoute("shares/{username}", function (username) {
		//first set up the base page
		crossroads.parse("shares");

		//then handel the data on the page
		if (cancel) {
			cancel();
		}
		var currentDbName = "shared_lists_" + username;
		//fixme: remove destroy when not using demo data all the time
		//anymore.
		//fixme: handle sync at a more global place so share.js can set
		//it into motion too?
		PouchDB.destroy(currentDbName, function () {
			sharesDb = new PouchDB(currentDbName);
			cancel = sync(
				sharesDb,
				COUCHDB_HOST + "/" + currentDbName,
				function () {
					updateView(username);
				},
				whenComplete
			);
		});
	});
}());
