function servicesRequest(opts) {
	var authHeader = "Basic " + btoa(encodeURI(username) + ":" + encodeURI(password));

	opts.url = SERVICES_HOST + opts.url;
	opts.headers = {
		Authorization: authHeader
	};
	opts.dataType = "json";

	$.ajax(opts);
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
