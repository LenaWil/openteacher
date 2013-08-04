exports.xmlEscape = function (xml) {
	xml = xml.replace(/&/g, "&amp;");
	xml = xml.replace(/>/g, "&gt;");
	xml = xml.replace(/</g, "&lt;");

	return xml;
};
exports.generateListHtml = function (list) {
	//replace with a real function
	var html = "<h1>" + list.title + "</h1>";
	html += list.items.join(", ");
	return html;
};
