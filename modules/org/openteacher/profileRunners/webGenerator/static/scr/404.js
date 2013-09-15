session.languageChanged.handle(function () {
	$("#notfound-page .subheader").text(_("Page not found"));
	$("#notfound-explanation").text(_("The page you requested doesn't exist. You could try going back to the start page."));
	$("#back-to-start").text(_("Back to the start page"));
});

$(function () {
	$("#back-to-start").click(function () {
		hasher.setHash("login");
	});
});

crossroads.bypassed.add(function () {
	show("#notfound-page");
});
