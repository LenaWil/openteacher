function (doc) {
	if(doc._id.indexOf("_design") !== 0) {
		emit([doc.title.toLowerCase(), doc.lastEdited], doc);
	}
}
