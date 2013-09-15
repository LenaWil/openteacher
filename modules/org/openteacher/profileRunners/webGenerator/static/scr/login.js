var username, password;

var loginPage = (function () {
	session.languageChanged.handle(function () {
		//login part
		$("#login-part .subheader").text(_("Log in"));

		$("#register-link").text(_("New? Click here to sign up."));
		$("#register-success").text(_("You registered succesfully. You can now log in."));
		$("#register-failure").text(_("You cancelled the registration."));

		$("#username-label").text(_("Username:"));
		$("#password-label").text(_("Password:"));
		$("#login-button").val(_("Log in!"));

		$("#login-anonymously-link").text(_("Login anonymously"));
		$("#login-anonymously-link").attr("title", _("All data will only be available locally, and will be gone when your browser's local storage is cleared."));

		//session box
		$("#logout-link").text(_("Log out"));
		$("#deregister-link").text(_("Unsubscribe"));

		//share part
		$("#share-part .subheader").text(_("Or view a shared list"));
	});

	function onLoginRequested() {
		auth = {
			username: $("#username").val(),
			password: $("#password").val()
		}
		$("#login-form")[0].reset();

		sync.start("lists_" + auth.username, auth);
		sync.start("shared_lists_" + auth.username, auth);
		sync.start("tests_" + auth.username, auth);
		sync.start("settings_" + auth.username, auth);

		session.userDbs = {}
		session.onUserDbChanges = {}
		$(["lists", "shared_lists", "tests", "settings"]).each(function (i, dbName) {
			var fullName = dbName + "_" + auth.username;
			session.userDbs[dbName] = new PouchDB(fullName);
			session.onUserDbChanges[dbName] = function (callback) {
				return sync.onChangesFor(fullName, callback);
			};
		});

		session.username = auth.username;
		session.password = auth.password
		session.loggedIn = true;

		hasher.setHash(session.next || "lists");
		delete session.next;

		$("#session-box").fadeIn();

		return false;
	}

	crossroads.addRoute("register", function () {
		var pn = document.location.pathname;
		var emptyFilePath = pn.slice(0, pn.lastIndexOf("/")) + "/empty.html";
		var registerUrl = SERVICES_HOST + "/register?" + $.param({
			redirect: document.location.origin + emptyFilePath,
			language: (navigator.language || "").replace("_", "-") || "C"
		});
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
		if (!session.loggedIn) {
			session.next = "deregister";
			hasher.replaceHash("login");
			return;
		}
		var sure = window.confirm(_("Are you sure you want to unsubscribe? This will remove your account and all data associated with it. Keep in mind that there's no recovery procedure!"));
		if (sure) {
			servicesRequest({
				url: "/deregister",
				type: "POST",
				success: function () {
					crossroads.parse("logout");
				}
			});
		} else {
			history.back();
		}
	});

	crossroads.addRoute("login", function () {
		show("#login-page");
		$("#username").focus();
	});

	crossroads.addRoute("login-anonymously", function () {
		$("#username").val("anonymous"),
		$("#password").val("anonymous");
		onLoginRequested();
	});

	crossroads.addRoute("logout", function () {
		$("#session-box").fadeOut();

		sync.stop("lists_" + session.username);
		sync.stop("shared_lists_" + session.username);
		sync.stop("tests_" + session.username);
		sync.stop("settings_" + session.username);

		delete session.username;
		delete session.password;
		delete session.userDbs;
		delete session.onUserDbChanges;
		session.loggedIn = false;

		hasher.replaceHash("login");
	});

	$(function () {
		$("#login-form").submit(onLoginRequested);
	});
}());
