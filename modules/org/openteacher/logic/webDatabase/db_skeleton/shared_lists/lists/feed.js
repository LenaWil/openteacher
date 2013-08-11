/*jshint expr:true*/

(function (head, req) {
	var lib = require("presentation_lib");

	provides("atom", function () {
		var share_owner = req.info.db_name.substring("shared_lists_".length);
		var host = "http://" + req.headers.Host;
		var url = host + req.raw_path;
		var row = getRow();
		var share_name = row.key[0];

		send("<?xml version='1.0' encoding='UTF-8' ?>");
		send("<feed xmlns='http://www.w3.org/2005/Atom'>");
			send("<id>");
				send(lib.xmlEscape(url));
			send("</id>");
			send("<title>");
				send(lib.xmlEscape("Share '" + share_name + "' by '" + share_owner + "'"));
			send("</title>");
		
		do {
			send("<entry>");
				send("<content type='html'>");
					send(lib.xmlEscape(lib.generateWordsHtml(row.value)));
				send("</content>");
				send("<id>");
					send(row.id);
				send("</id>");
				send("<title>");
					send(lib.xmlEscape(row.value.title));
				send("</title>");
				send("<link href='");
					send(host + "/shared_lists_" + share_owner + "/_design/lists/_show/print/" + row.id);
				send("' />");
				send("<updated>");
					send(row.value.lastEdited);
				send("</updated>");
			send("</entry>");
			row = getRow();
		} while (row);
		send("</feed>");
	});
});
