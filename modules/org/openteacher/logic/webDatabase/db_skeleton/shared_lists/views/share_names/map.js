/*jshint expr:true*/

(function (doc) {
	if(doc._id.indexOf("_design") !== 0) {
		for (var i = 0; i < doc.shares.length; i += 1) {
			emit(doc.shares[i], null);
		}
	}
});
