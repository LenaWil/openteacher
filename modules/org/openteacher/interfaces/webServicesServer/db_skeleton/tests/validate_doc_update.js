function (newDoc, oldDoc, userCtx) {
	if (newDoc._deleted) {
		//that's fine.
		return;
	}
	var lib = require("validation_lib");

	lib.requireAttr(newDoc, "listId");
	var results = newDoc.results || [];
	for (var i = 0; i < results.length; i += 1) {
		lib.assertSafeHtml(results[i].givenAnswer || "");
	}
}
