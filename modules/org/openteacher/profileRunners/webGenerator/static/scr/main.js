var translate, _;
(function () {
	//fixme
	$(["test", "test2", "anonymous"]).each(function (i, username) {
		PouchDB.destroy("private_" + username);
		PouchDB.destroy("shared_lists_" + username);
	});
}());

var session = {
	//other properties set when logged in are:
	//- username = "...";
	//- password = "...";
	//- userDbs = {
	//    private: new PouchDB('...'),
	//    shared_lists: new PouchDB('...'),
	//  }
	// - onUserDbChanges = {
	//    private: function (callback) {...; return function cancel() {...};},
	//    shared_lists: function (callback) {...; return function cancel() {...};},
	//  }
	//
	//when redirecting to the login page, you can set:
	//- next (with a url as accepted by hasher.setHash)
	languageChanged: new logic.Event(),
	languageChangeDone: new logic.Event(),
	loggedIn: false
};

$(function () {
	//translation
	session.languageChanged.handle(function () {
		var otWeb = _("OpenTeacher Web");

		document.title = otWeb;
		$("#header-title").text(otWeb);

		$("#license-and-source-link").text(_("License information and source code"));
	});

	function translate() {
		//browserLanguage for IE
		lang = navigator.language || navigator.browserLanguage;
		logic.translator(translationIndex, lang, function (tr) {
			_ = tr;
			session.languageChanged.send();
			session.languageChangeDone.send();
		});
	}
	translate();

	session.languageChangeDone.handle(function () {
		//routing
		crossroads.ignoreState = true;
		function parseHash(newHash, oldHash) {
			crossroads.parse(newHash);
		}
		hasher.initialized.add(parseHash);
		hasher.changed.add(parseHash);

		//start listening
		if (!location.hash) {
			//when there's no hash path to specify otherwise, go to the
			//login page.
			hasher.replaceHash("login");
		}
		hasher.init();
	});
});
