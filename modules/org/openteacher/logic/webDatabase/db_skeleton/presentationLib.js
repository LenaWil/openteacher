exports.xmlEscape = function (xml) {
	xml = xml.replace(/&/g, "&amp;");
	xml = xml.replace(/>/g, "&gt;");
	xml = xml.replace(/</g, "&lt;");

	return xml;
};

exports.generateWordsHtml = function (list) {
	return generateWordsHtml(list, {margin: "1em"});
};
