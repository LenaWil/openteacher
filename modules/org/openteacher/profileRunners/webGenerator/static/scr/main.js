var listsDb, sharedListsDb, testsDb;

function _(str) {
	//FIXME
	return str;
}

function show(page, whenDone) {
	function hidingDone (slow) {
		var speed = slow ? "slow": "fast";
		$(page).fadeIn(speed, whenDone);
	}

	var pagesToHide = $("#login-page:visible, #lists-page:visible, #list-page:visible, #learn-page:visible");
	if (pagesToHide.length) {
		pagesToHide.fadeOut("fast", hidingDone);
	} else {
		hidingDone(true);
	}
}

$(function () {
	//FIXME: remove this when the db isn't completely
	//repopulated each time anymore.
	PouchDB.destroy("lists");
	PouchDB.destroy("shared_lists");
	PouchDB.destroy("tests");
	listsDb = new PouchDB("lists");
	sharedListsDb = new PouchDB("shared_lists");
	testsDb = new PouchDB("tests");
});
