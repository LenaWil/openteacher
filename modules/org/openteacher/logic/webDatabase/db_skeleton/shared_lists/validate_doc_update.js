/*jshint expr:true*/

(function (newDoc, oldDoc, userCtx) {
	if (userCtx.roles.indexOf("_admin") === -1) {
		throw({"unauthorized": "need to be admin to make changes."});
	}
	if (newDoc._deleted) {
		//that's fine.
		return;
	}
	if (oldDoc && oldDoc.shares.length) {
		//You can never get a shared list
		//de-published again, but at least it's
		//removed from the view this time, and from
		//next time on changes to the list will not
		//be visible anymore (until the list is
		//shared again.)
		return;
	}
	if (!newDoc.shares.length) {
		throw({"forbidden": "should be here only if having shares."});
	}
});
