function (doc) {
	if(doc._id.indexOf("_design") !== 0) {
		try {
			var startTime = doc.results[0].active.start;
		} catch (e) {
			var startTime = null;
		}
		emit([doc.listId, startTime], doc);
	}
}
