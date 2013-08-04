exports.assertSafeHtml = function (data) {
	if (!isSafeHtml(data)) {
		throw({forbidden: "'" + data + "' isn't valid HTML."});
	}
};
exports.requireAttr = function (obj, attr) {
	if (typeof obj[attr] === "undefined") {
		throw({"forbidden": name + " should not be undefined."});
	}
};
exports.assertValidDate = function (data) {
	if (isNaN(new Date(data).valueOf())) {
		//if not a valid date
		throw({"forbidden": "'" + data + "' should be a valid JSON representation of a JS Date object (as serialized in JS)."});
	}
};
