var doRetranslate, _;

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

$(function () {
	function retranslate() {
		var otWeb = _("OpenTeacher Web");

		document.title = otWeb;
		$("#header-title").text(otWeb);

		$("#license-and-source-link").text(_("License information and source code"));
	}

	function doRetranslate() {
		lang = navigator.language;
		logic.translator(translationIndex, lang, function (tr) {
			_ = tr;
			retranslate();
			loginPage.retranslate();
			sharesPage.retranslate();
			sharePage.retranslate();
			overviewPage.retranslate();
			learnPage.retranslate();
			viewPage.retranslate();
		});
	}

	doRetranslate();
});
