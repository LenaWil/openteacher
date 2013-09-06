function servicesRequest(opts) {
	var authHeader = "Basic " + btoa(encodeURI(username) + ":" + encodeURI(password));

	opts.url = SERVICES_HOST + opts.url;
	opts.headers = {
		Authorization: authHeader
	};
	opts.dataType = "json";

	$.ajax(opts);
}

function show(page, whenDone) {
	function hidingDone (slow) {
		var speed = slow ? "slow": "fast";
		$(page).fadeIn(speed, whenDone);
	}

	var pagesToHide = $("#login-page:visible, #lists-page:visible, #view-page:visible, #learn-page:visible, #shares-page:visible, #share-page:visible");
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

function sync(db, remoteDb, onChange, complete) {
	var options = {continuous: true};
	if (onChange) {
		options.onChange = onChange;
	}
	var to = db.replicate.to(remoteDb, options, complete);
	var from = db.replicate.from(remoteDb, options, complete);
	return function cancel() {
		to.cancel();
		from.cancel();
	};
}
