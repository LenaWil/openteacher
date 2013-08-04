function (doc, req) {
	var lib = require("presentation_lib");

	provides("html", function () {
		return lib.generateListHtml(doc);
	});
}
