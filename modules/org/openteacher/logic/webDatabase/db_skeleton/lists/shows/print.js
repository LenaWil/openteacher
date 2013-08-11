/*jshint expr:true*/

(function (doc, req) {
	if (!doc) {
		return {
			code: 404,
			body: "Nothing here. You might want to try adding a list id to the URL. Or, if there is already one, check if it's not removed in the meantime."
		};
	}

	var lib = require("presentation_lib");
	provides("html", function () {
		return lib.generateWordsHtml(doc);
	});
});
