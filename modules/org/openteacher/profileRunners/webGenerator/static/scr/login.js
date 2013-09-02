var username, password;

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

		//session box
		$("#logout-link").text(_("Log out"));
		$("#deregister-link").text(_("Deregister"));

		//share part
		$("#share-part .subheader").text(_("Or view a shared list"));
	}

	function onLogin() {
		username = $("#username").val();
		password = $("#password").val();
		$("#login-form")[0].reset();

		function sync(db, remoteDb, onChange) {
			var options = {continuous: true};
			if (onChange) {
				options.onChange = onChange;
			}
			var to = db.replicate.to(remoteDb, options);
			var from = db.replicate.from(remoteDb, options);
			return function cancel() {
				to.cancel();
				from.cancel();
			}
		}

		loggedIn(username, password, function () {
			var xhr = new XMLHttpRequest();
			xhr.withCredentials = true;
			xhr.open("GET", COUCHDB_HOST + "/_session");
			xhr.send();
			show("#lists-page");
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
			}
		});
		return false;
	}

	function onLogout() {
		$("#session-box").fadeOut();
		show("#login-page");
		cancelSync();

		var xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.open("DELETE", COUCHDB_HOST + "/_session");
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send();

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
		});
		return false;
	}

	function onDeregister() {
		var sure = window.confirm(_("Are you sure you want to deregister? This will remove your account and all data associated with it, without a possibility to recover!"));
		if (sure) {
			servicesRequest({
				url: "/deregister",
				type: "POST",
				success: onLogout
			})
		}

		//FIXME. Ask for confirmation & then send the POST request to
		//the services API that kills the account.
		return false;
	}

	$(function () {
		$("#logout-link").click(onLogout);
		$("#deregister-link").click(onDeregister);

		$("#register-link").click(onRegister);
		$("#login-form").submit(onLogin);

		show("#login-page");
		$("#username").focus();
	});

	return {retranslate: retranslate};
}());
