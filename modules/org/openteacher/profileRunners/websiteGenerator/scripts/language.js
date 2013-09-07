$(function () {
	var maxwidth = $("#languageBar").width();

	$("#languageBar").css({width: maxwidth});
	$("#otherLanguages").hide();

	$("#languageBar").mouseenter(function () {
		$("#otherLanguages").slideDown();
	});
	$("#languageBar").mouseleave(function () {
		$("#otherLanguages").slideUp();
	});

	function onResize () {
		var leftPos = $("#header").position().left + $("#header").width() - maxwidth - 15;
		$("#languageBar").css({left: leftPos});
	}

	$(window).resize(onResize);
	//place initially
	onResize();
});
