function (doc) {
	if(doc._id.indexOf("_design") !== 0) {
		for (var i = 0; i < doc.shares.length; i += 1) {
			//sort order: by share, by title
			emit([doc.shares[i], doc.title.toLowerCase(), doc.lastEdited], doc);
		}
	}
}
