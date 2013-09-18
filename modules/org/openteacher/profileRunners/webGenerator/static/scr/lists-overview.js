var overviewPage = (function () {
	var newListText, cancelChanges;

	function retranslate() {
		$("#lists-page .subheader").text(_("Lists overview"));
		$("#remove-selected").text(_("Remove selected lists"));
		$("#new-list").text(_("Create new list"));
		$("#load-list-from-computer").text(_("Upload list from computer"));
		$("#lists .view-link").text(_("View"));
		$(".learn-link").text(_("Teach me!"));
		$("#lists .last-edited-label").text(_("Last edited:"));

		$("#do-upload").val(_("Upload file"));
		$("#cancel-upload").text(_("Cancel"));
		$("#upload-explanation").text(_("Please select the file you want to upload below, and click 'upload' when you're done. Supported file extensions are:"));
		$("#load-failure").text(_("Couldn't load file. Is the file type supported and the file not corrupted?"));
	}
	session.languageChanged.handle(retranslate);

	function onRemoveSelected() {
		var deleteDocs = [];

		$("#lists input:checked").each(function () {
			var tr = $(this).parent().parent();

			deleteDocs.push({
				_id: tr.data("id"),
				_rev: tr.data("rev"),
				_deleted: true
			});
		});
		PouchDBext.withValidation.bulkDocs(session.userDbs.lists, {docs: deleteDocs});
	}

	function webifyList(list) {
		list.lastEdited = new Date();
		list.shares = [];

		return list;
	}

	function onNewList() {
		list = webifyList({
			items: [],
			title: _("New list")
		});
		PouchDBext.withValidation.post(session.userDbs.lists, list, function (err, resp) {
			hasher.setHash("lists/" + resp.id + "/view");
		});
	}

	function onLoadSuccess(doc) {
		doc.title = doc.title || _("Uploaded list");
		doc = webifyList(doc);

		tests = doc.tests || [];
		delete doc.tests;

		PouchDBext.withValidation.post(session.userDbs.lists, doc, function (err, resp) {
			$.each(tests, function (i, test) {
				test.listId = resp.id;
				PouchDBext.withValidation.post(session.userDbs.tests, test);
			});
		});
		hasher.setHash("lists");
	}

	function onLoadError() {
		$("#load-failure").slideDown(slideUpAfterTimeout(5000));
	}

	function onUploadSubmit() {
		$.each($("#file-box")[0].files, function (i, file) {
			var data = new FormData();
			data.append("file", file);
			servicesRequest({
				url: "/load",
				type: "POST",
				data: data,
				cache: false,
				processData: false,
				contentType: false,
				success: onLoadSuccess,
				error: onLoadError
			});
		});
		this.reset();
		return false;
	}

	function onListsChange(change) {
		session.userDbs.lists.query("lists/by_title", function(err, resp) {
			$("#loading-box").slideUp("fast");

			var tbody = $("#lists tbody");
			tbody.empty();
			for (var i = 0; i < resp.rows.length; i += 1) {
				var doc = resp.rows[i].value;

				var rows = tmpl("lists-template", {
					doc: doc,
					classes: tbody.children().length % 2 ? "even" : "odd"
				});
				tbody.append(rows);
			}
			//the lists table contains stuff that needs to be translated.
			retranslate();
		});
	}

	function onExtensionsLoaded(json) {
		var exts = json.result.map(function (ext) {
			return "." + ext;
		});
		exts = exts.sort().join(", ");
		$("#upload-exts").text(exts);
	}

	$(function () {
		$("#remove-selected").click(onRemoveSelected);
		$("#new-list").click(onNewList);
		$("#load-list-from-computer").click(function () {
			hasher.setHash("lists/upload-from-computer")
		});

		$("#upload-form").submit(onUploadSubmit);
		$("#cancel-upload").click(function () {
			hasher.setHash("lists");
		});
	});

	var listsRoute = crossroads.addRoute("lists")
	listsRoute.matched.add(function () {
		if (!session.loggedIn) {
			session.next = "lists";
			hasher.replaceHash("login");
			return;
		}
		if (session.username === "anonymous") {
			$("#load-list-from-computer").hide();
		} else {
			$("#load-list-from-computer").show();
		}
		cancelChanges = session.onUserDbChanges.lists(onListsChange);
		show("#lists-page");
	});
	listsRoute.switched.add(function () {
		if (session.loggedIn) {
			cancelChanges();
		}
	});

	var uploadRoute = crossroads.addRoute("lists/upload-from-computer")
	uploadRoute.matched.add(function () {
		if (!session.loggedIn) {
			session.next = "lists/upload-from-computer";
			hasher.replaceHash("login");
			return;
		}
		$("#upload-part").slideDown();
		servicesRequest({
			url: "/load/supported_extensions",
			success: onExtensionsLoaded,
		});
	});
	uploadRoute.switched.add(function () {
		$("#upload-part").slideUp();
	});
}());
