session.languageChanged.handle(function () {
	$("#license-and-source-page .subheader").text(_("License information and source code"));
	$(".back-from-license-and-source").text(_("Back"));
});
$(function () {
	$(".back-from-license-and-source").click(function () {
		history.back();
	});
});
crossroads.addRoute("license-and-source", function () {
	$("#license-and-source-info").load("COPYING.txt");
	show("#license-and-source-page");
});
