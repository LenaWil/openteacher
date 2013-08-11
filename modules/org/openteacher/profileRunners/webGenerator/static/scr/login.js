var username;

var loginPage = (function () {
	function retranslate() {
		//login part
		$("#login-part .subheader").text(_("Log in"));

		$("#register-link").text(_("New? Click here to sign up."));
		$("#register-success").text(_("You registered succesfully. You can now log in."));
		$("#register-failure").text(_("You cancelled the registration."));

		$("#username-label").text(_("Username:"));
		$("#password-label").text(_("Password:"));
		$("#login-button").val(_("Log in!"));

		//share part
		$("#share-part .subheader").text(_("Or view a shared list"));
	}

	function onLogin() {
		username = $("#username").val();
		var password = $("#password").val();

		function sync(db, remoteDb, onChange) {
			var options = {continuous: true};
			if (onChange) {
				options.onChange = onChange;
			}
			db.replicate.to(remoteDb, options);
			db.replicate.from(remoteDb, options);
		}

		loggedIn(username, password, function () {
			var xhr = new XMLHttpRequest();
			xhr.withCredentials = true;
			xhr.open("GET", COUCHDB_HOST + "/_session");
			xhr.send();
			show("#lists-page");
			sync(listsDb, COUCHDB_HOST + "/lists_" + username, listsChanged.send);
			sync(sharedListsDb, COUCHDB_HOST + "/shared_lists_" + username, sharedListsChanged.send);
			sync(testsDb, COUCHDB_HOST + "tests_" + username, testsChanged.send);
			sync(settingsDb, COUCHDB_HOST + "settings_" + username, settingsChanged.send);
		});
		return false;
	}

	function loggedIn(username, password, done) {
		var xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				done();
			}
		};
		xhr.open("POST", COUCHDB_HOST + "/_session");
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send(JSON.stringify({"name": username, "password": password}));
	}

	function onRegister() {
		//fixme: replace C with actual language
		var pn = document.location.pathname;
		var emptyFilePath = pn.slice(0, pn.lastIndexOf("/")) + "/empty.html";
		var redirect = document.location.origin + emptyFilePath;
		var registerUrl = SERVICES_HOST + "/register?language=C&redirect=" + redirect;
		$("#register-iframe")
			.attr("src", registerUrl)
			.slideDown("slow")
			.load(function () {
				var iframeQuery;
				try {
					iframeQuery = this.contentDocument.location.search;
				} catch(e) {
					if (e.name === "TypeError") {
						return;
					}
					throw(e);
				}
				//if here, the register page is 'done'. We can't get the
				//query string of any other page than our own, and it
				//gets redirected to our own page when that happens.
				if (iframeQuery === "?status=ok") {
					$("#register-success").fadeIn();
					$("#register-failure").fadeOut();
				}
				if (iframeQuery === "?status=cancel") {
					$("#register-failure").show();
					$("#register-success").fadeOut();
				}
				//set the src back to the registerUrl, it makes the
				//slideUp animation look better.
				$(this)
					.attr("src", registerUrl + "&screenshotonly=true")
					.slideUp("slow");
		});
		return false;
	}

	$(function () {
		$("#register-link").click(onRegister);
		$("#login-form").submit(onLogin);

		show("#login-page");
		$("#username").focus();
	});

	return {retranslate: retranslate};
}());
