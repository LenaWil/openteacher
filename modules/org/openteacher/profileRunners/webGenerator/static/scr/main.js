var translate, _;

//FIXME: remove the .destroy()'s when the db isn't completely
//repopulated each time anymore.
PouchDB.destroy("lists");
PouchDB.destroy("shared_lists");
PouchDB.destroy("tests");
PouchDB.destroy("settings");

var listsDb = new PouchDB("lists");
var sharedListsDb = new PouchDB("shared_lists");
var testsDb = new PouchDB("tests");
var settingsDb = new PouchDB("settings");

var listsChanged = new logic.Event();
var sharedListsChanged = new logic.Event();
var testsChanged = new logic.Event();
var settingsChanged = new logic.Event();

var languageChanged = new logic.Event();

$(function () {
	//translation
	languageChanged.handle(function () {
		var otWeb = _("OpenTeacher Web");

		document.title = otWeb;
		$("#header-title").text(otWeb);

		$("#license-and-source-link").text(_("License information and source code"));
	});

	function translate() {
		lang = navigator.language;
		logic.translator(translationIndex, lang, function (tr) {
			_ = tr;
			languageChanged.send();
		});
	}
	translate();

	//routing
	function parseHash(newHash, oldHash) {
		crossroads.parse(newHash);
	}
	hasher.initialized.add(parseHash);
	hasher.changed.add(parseHash);
	//start listening
	hasher.init();
	if (!hasher.getHash()) {
		//when there's no hash path to specify otherwise, go to the
		//login page.
		hasher.replaceHash("login")
	};
});
