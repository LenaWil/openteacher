var currentDbName;

var sharesPage = (function () {
	var cancel;
	var sharesDb;

	function retranslate() {
		$("#shares-page .subheader").text(_("Shares"));
		$("#share-owner-label").text(_("Share owner's username:"));
		$("#find-shares").val(_("Find available shares"));
		$("#share-error").text(_("An error occurred while getting shares. Please make sure that the user exists and that your internet connection works correctly."));
	}

	function whenComplete(err, resp) {
		if (err) {
			updateView();
			$("#share-error").slideDown(slideUpAfterTimeout(8000));
		}
	}

	function updateView() {
		$("#share-links").empty();
		sharesDb.query("shares/share_names", {reduce: true}, function (err, resp) {
			$.each(resp.rows, function (i, row) {
				var link = tmpl("share-template", row);
				$("#share-links").append(link);
			});
		});
	}

	function shareOwnerRequested() {
		if (cancel) {
			cancel();
		}
		var username = $("#share-owner").val();
		currentDbName = "shared_lists_" + username;
		//fixme: remove destroy when not using demo data all the time
		//anymore.
		PouchDB.destroy(currentDbName, function () {
			sharesDb = new PouchDB(currentDbName);
			cancel = sync(
				sharesDb,
				COUCHDB_HOST + "/" + currentDbName,
				updateView,
				whenComplete
			);
		});

		this.reset();
		return false;
	}

	function shareDetailRequested() {
		var name = $(this).text();
		sharePage.show(name);
		return false;
	}

	$(function () {
		$("#share-owner-form").submit(shareOwnerRequested);
		$("#share-links").on("click", "a", shareDetailRequested);
	});

	function onShow() {
		show("#shares-page", function () {
			$("#share-owner").focus();
		});
	}

	return {
		retranslate: retranslate,
		show: onShow
	};
}());
