var username, password;

var loginPage = (function () {
	languageChanged.handle(function () {
		//login part
		$("#login-part .subheader").text(_("Log in"));

		$("#register-link").text(_("New? Click here to sign up."));
		$("#register-success").text(_("You registered succesfully. You can now log in."));
		$("#register-failure").text(_("You cancelled the registration."));

		$("#username-label").text(_("Username:"));
		$("#password-label").text(_("Password:"));
		$("#login-button").val(_("Log in!"));

		//session box
		$("#logout-link").text(_("Log out"));
		$("#deregister-link").text(_("Unsubscribe"));

		//share part
		$("#share-part .subheader").text(_("Or view a shared list"));
	});

	function onLoginRequested() {
		username = $("#username").val();
		password = $("#password").val();
		$("#login-form")[0].reset();

		loggedIn(username, password, function () {
			var xhr = new XMLHttpRequest();
			xhr.withCredentials = true;
			xhr.open("GET", COUCHDB_HOST + "/_session");
			xhr.send();
			hasher.setHash("lists");
			$("#session-box").fadeIn();

			var cancel1 = sync(listsDb, COUCHDB_HOST + "/lists_" + username, listsChanged.send);
			var cancel2 = sync(sharedListsDb, COUCHDB_HOST + "/shared_lists_" + username, sharedListsChanged.send);
			var cancel3 = sync(testsDb, COUCHDB_HOST + "tests_" + username, testsChanged.send);
			var cancel4 = sync(settingsDb, COUCHDB_HOST + "settings_" + username, settingsChanged.send);

			cancelSync = function () {
				cancel1();
				cancel2();
				cancel3();
				cancel4();
			};
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

	crossroads.addRoute("register", function () {
		//fixme: replace C with actual language
		var pn = document.location.pathname;
		var emptyFilePath = pn.slice(0, pn.lastIndexOf("/")) + "/empty.html";
		var redirect = document.location.origin + emptyFilePath;
		var registerUrl = SERVICES_HOST + "/register?language=C&redirect=" + redirect;
		$("#register-iframe")
			.attr("src", registerUrl)
			.slideDown("slow")
			.load(function () {
				try {
					if (this.contentDocument.location.pathname.indexOf("empty.html") === -1) {
						//not yet at the redirect path
						return;
					}
				} catch(e) {
					if (e.name === "TypeError") {
						//Single-origin violation means we're not yet
						//at the redirect path -> ignore.
						return;
					}
					throw(e);
				}
				var iframeQuery = this.contentDocument.location.search;
				//if here, the register page is 'done'.
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
				hasher.setHash("login");
		});
	});

	crossroads.addRoute("deregister", function () {
		var sure = window.confirm(_("Are you sure you want to unsubscribe? This will remove your account and all data associated with it. Keep in mind that there's no recovery procedure!"));
		if (sure) {
			servicesRequest({
				url: "/deregister",
				type: "POST",
				success: function () {
					crossroads.parse("logout");
				}
			});
		}
	});

	crossroads.addRoute("login", function () {
		show("#login-page");
		$("#username").focus();
	});

	crossroads.addRoute("logout", function () {
		$("#session-box").fadeOut();
		hasher.replaceHash("login");
		cancelSync();

		var xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.open("DELETE", COUCHDB_HOST + "/_session");
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send();
	});

	$(function () {
		$("#login-form").submit(onLoginRequested);
	});
}());
