(function () {
	function onLogin() {
		var username = $("#username").val();
		var password = $("#password").val();

		function sync(db, remoteDb, onChange) {
			var options = {	continuous: true};
			if (onChange) {
				options.onChange = onChange;
			}
			db.replicate.to(remoteDb, options);
			db.replicate.from(remoteDb, options);
		}

		loggedIn(username, password, function () {
			show("#lists-page");
			sync(listsDb, COUCHDB_HOST + "/lists_" + username, onListsChange);
			sync(sharedListsDb, COUCHDB_HOST + "/shared_lists_" + username, onSharedListsChange);
			sync(testsDb, COUCHDB_HOST + "tests_" + username);
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

	function onListsChange(change) {
		listsDb.query("lists/by_title", function(err, resp) {
			var tbody = $("#lists tbody");
			tbody.empty();
			for (var i = 0; i < resp.rows.length; i += 1) {
				var doc = resp.rows[i].value;

				var rows = renderTemplate("#lists-template", {
					doc: doc,
					classes: tbody.children().length % 2 ? "even" : "odd"
				});
				tbody.append(rows);
			}
		});
	}

	function onSharedListsChange(change) {
		sharedListsDb.query("shares/share_names", {group: true}, function (err, resp) {
			var shareNames = [];
			for (var i = 0; i < resp.rows.length; i += 1) {
				shareNames.push(resp.rows[i].key);
			}
			$("#shares-info").text("Currently existing shares: " + shareNames.join(", "));
		});
	}

	function onRegister() {
		var registerUrl = SERVICES_HOST + "/register?redirect=" + document.location.origin + document.location.pathname;
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
					$("#register-status")
						.css("color", "green")
						.text("You registered succesfully. You can now log in.");
				}
				if (iframeQuery === "?status=cancel") {
					$("#register-status")
						.css("color", "red")
						.text("You cancelled the registration.");
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
}());
