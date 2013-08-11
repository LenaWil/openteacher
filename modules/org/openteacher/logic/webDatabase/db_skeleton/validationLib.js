exports.assertSafeHtml = function (text) {
	if (!isSafeHtml(text)) {
		throw({forbidden: "'" + text + "' isn't safe HTML."});
	}
};

exports.requireAttr = function (obj, attr) {
	if (typeof obj[attr] === "undefined") {
		throw({forbidden: "'" + attr + "' should not be undefined."});
	}
	if (!obj[attr]) {
		throw({forbidden: "'" + attr + "' should not evaluate to false."});
	}
};

exports.assertValidDate = function (data) {
	if (isNaN(new Date(data).valueOf())) {
		//if not a valid date
		throw({forbidden: "'" + data + "' should be a valid JSON representation of a JS Date object (as serialized in JS)."});
	}
};

exports.assertNumeric = function (number) {
	if (typeof number !== "number") {
		throw({forbidden: "'" + number + "' should be a number."});
	}
};
