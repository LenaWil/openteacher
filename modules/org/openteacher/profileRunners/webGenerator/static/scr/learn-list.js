var learnPage = (function () {
	var lessonType, currentList;

	session.languageChanged.handle(function () {
		$("#question-label-label").text(_("Question:"));
		$("#check-button").val(_("Check!"));
		$("#skip-button").val(_("Skip"));
		$("#correct-anyway-button").val(_("Correct anyway"));
		$("#back-from-learn-page").text(_("Back"));
	});

	var controller = new logic.InputTypingController();

	function newItem(item) {
		$("#question-label").html(logic.compose(item.questions || []));
	}

	function lessonDone(callback) {
		if (typeof callback === "undefined") {
			callback = function () {
				hasher.setHash("lists/" + currentList._id + "/view");
			};
		}
		if (typeof currentList.tests === "undefined") {
			//no answer had been given yet the moment the test was
			//aborted.
			callback();
		} else {
			var doc = currentList.tests[0];
			doc.listId = currentList._id;
			PouchDBext.withValidation.post(session.userDbs.tests, doc, callback);
		}
	}

	function showCorrection(correction) {
		$("#correction-label")
			.text(correction)
			.show()
			.fadeOut(4000, controller.correctionShowingDone);
	}

	function hideCorrection() {
		$("#correction-label").stop().hide();
	}

	$(function () {
		$("#back-from-learn-page").click(function () {
			lessonDone(function () {
				history.back();
			});
		});

		//bind to controller events
		controller.clearInput.handle(function () {
			$("#learn-answer-input").val("");
		});
		controller.enableInput.handle(function () {
			$("#learn-answer-input").removeAttr("disabled");
		});
		controller.disableInput.handle(function () {
			$("#learn-answer-input").attr("disabled", "disabled");
		});
		controller.focusInput.handle(function () {
			//the timeout is needed because jQuery might still be busy
			//finishing the 'wrong answer' fade animation which ruins
			//the focus.
			setTimeout(function () {
				//apparantly you can't delay calling jquery object
				//methods, so wrapping this call.
				$("#learn-answer-input").focus();
			}, 0);
		});

		controller.showCorrection.handle(showCorrection);
		controller.hideCorrection.handle(hideCorrection);

		controller.enableCheck.handle(function () {
			$("#check-button").removeAttr("disabled");
		});
		controller.disableCheck.handle(function () {
			$("#check-button").attr("disabled", "disabled");
		});
		controller.enableSkip.handle(function () {
			$("#skip-button").removeAttr("disabled");
		});
		controller.disableSkip.handle(function () {
			$("#skip-button").attr("disabled", "disabled");
		});
		controller.enableCorrectAnyway.handle(function () {
			$("#correct-anyway-button").removeAttr("disabled");
		});
		controller.disableCorrectAnyway.handle(function () {
			$("#correct-anyway-button").attr("disabled", "disabled");
		});

		$("#learn-form").submit(function () {
			controller.checkTriggered($("#learn-answer-input").val());
			return false;
		});
		$("#skip-button").click(controller.skipTriggered);
		$("#correct-anyway-button").click(controller.correctAnywayTriggered);
		$("#learn-answer-input").keyup(controller.userIsTyping);
	});

	crossroads.addRoute("lists/{id}/learn", function (id) {
		if (!session.loggedIn) {
			session.next = "lists/" + id + "/learn";
			hasher.replaceHash("login");
			return;
		}
		session.userDbs.lists.get(id, function (err, list) {
			currentList = list;
			indexes = [];
			for (i = 0; i < list.items.length; i += 1) {
				indexes.push(i);
			}

			lessonType = new logic.LessonType(list, indexes);
			lessonType.newItem.handle(newItem);
			lessonType.lessonDone.handle(lessonDone);

			controller.lessonType = lessonType;

			show("#learn-page", function () {
				lessonType.start();
			});
		});
	});
}());
