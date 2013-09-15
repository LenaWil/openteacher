var sync = (function () {
	var syncs = {};

	function createSyncInfoIfNotThere(dbName) {
		if (!syncs.hasOwnProperty(dbName)) {
			syncs[dbName] = {
				//amount of times this sync is requested. Makes sure
				//that the sync isn't cancelled until no one is using it
				//anymore.
				count: 0,
				changes: new logic.Event(),
				errors: new logic.Event()
			}
		}
	}

	var api = {
		start: function (dbName, auth) {
			createSyncInfoIfNotThere(dbName);

			syncs[dbName].count += 1;

			if (syncs[dbName].count === 1) {
				//start sync
				opts = {
					continuous: true,
					complete: function (err, resp) {
						//on error, stop the other replication too directly.
						syncs[dbName].cancel();
						syncs[dbName].errors.send(err);
					}
				};
				var db = new PouchDB(dbName);
				var remoteName = COUCHDB_HOST + "/" + dbName;
				var remoteDb = new PouchDB(remoteName, {auth: auth})
				var to = db.replicate.to(remoteDb, opts);
				var from = db.replicate.from(remoteDb, opts);

				syncs[dbName].cancel = function () {
					//both ways
					to.cancel();
					from.cancel();
				}
			}
		},
		stop: function (dbName) {
			syncs[dbName].count -= 1;
			if (syncs[dbName].count === 0) {
				syncs[dbName].cancel();
			}
		},
		onChangesFor: function (dbName, callback) {
			var db = new PouchDB(dbName);
			var changes = db.changes({continuous: true, onChange: callback});
			return function () {} || changes.cancel;
		},
		errorsFor: function (dbName) {
			createSyncInfoIfNotThere();

			return syncs[dbName].errors;
		}
	}
	return api;
}());

function servicesRequest(opts) {
	var authHeader = "Basic " + btoa(encodeURI(session.username) + ":" + encodeURI(session.password));

	opts.url = SERVICES_HOST + opts.url;
	opts.headers = {
		Authorization: authHeader
	};
	opts.dataType = "json";

	$.ajax(opts);
}

function show(page, whenDone) {
	if ($(page + ":visible").length) {
		//page already shown.
		return;
	}
	function hidingDone (slow) {
		var speed = slow ? "slow": "fast";
		$(page).fadeIn(speed, whenDone);
	}

	var pagesToHide = $(".page:visible");
	if (pagesToHide.length) {
		pagesToHide.fadeOut("fast", hidingDone);
	} else {
		hidingDone(true);
	}
}

function slideUpAfterTimeout(timeout) {
	return function () {
		var elem = this;
		setTimeout(function () {
			if ($(elem).is(":visible")) {
				$(elem).slideUp();
			}
		}, timeout);
	};
}
