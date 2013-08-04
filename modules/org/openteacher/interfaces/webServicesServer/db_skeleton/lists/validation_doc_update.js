function (newDoc, oldDoc, userCtx) {
	if (newDoc._deleted) {
		//that's fine.
		return;
	}
	var lib = require("validation_lib");

	lib.requireAttr(newDoc, "title");
	lib.assertSafeHtml(newDoc, "title");

	lib.requireAttr(newDoc, "shares");
	for (var i = 0; i < newDoc.shares.length; i += 1) {
		lib.assertSafeHtml(newDoc.shares[i]);
	}

	lib.requireAttr(newDoc, "lastEdited");
	lib.assertValidDate(newDoc.lastEdited);

	var items = newDoc.items || [];
	for (var i = 0; i < items.length; i += 1) {
		var item = items[i];
		lib.assertSafeHtml(item.comment || "");
		lib.assertSafeHtml(item.commentAfterAnswering || "");
		//close enough...
		lib.assertSafeHtml((item.questions || []).toString());
		lib.assertSafeHtml((item.answers || []).toString());
	}
}
