/*jshint expr:true*/

(function (doc) {
	if(doc._id.indexOf("_design") !== 0) {
		var startTime;
		try {
			startTime = doc.results[0].active.start;
		} catch (e) {
			startTime = null;
		}
		emit([doc.listId, startTime], doc);
	}
});
