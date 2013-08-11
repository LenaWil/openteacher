var PouchDBext = (function () {
	function couchEval(requireContext, extraVars, program) {
		/*jshint evil:true*/
		var require;
		if (requireContext) {
			require = function (libPath) {
				var exports = {};

				var path = libPath.split("/");
				var lib = requireContext;
				for (var i = 0; i < path.length; i += 1) {
					lib = lib[path[i]];
				}
				eval(lib);
				return exports;
			}
		}

		var statements = "";
		for (name in extraVars) {
			statements += "var " + name + " = extraVars[" + name + "];\n";
		}

		return eval(statements + program);
	}

	var providesFuncs = {};
	function provides(type, func) {
		providesFuncs[type] = function () {
			return {
				code: 200,
				body: func()
			};
		};
	}

	function doValidation(db, newDoc, options, callback) {
		fillInValidationOptions(db, options, function (newOptions) {
			getValidationFunctions(db, function (err, validationFuncs) {
				if (err) {
					callback(err, null);
					return
				}
				if (!validationFuncs.length) {
					//no validation functions -> success
					callback(null, true);
					return
				}
				getOldDoc(db, newDoc._id, function (oldDoc) {
					try {
						validationFuncs.forEach(function (validationFunc) {
							validationFunc(newDoc, oldDoc, newOptions.userCtx, newOptions.secObj);
						});
					} catch (e) {
						if (e.unauthorized || e.forbidden) {
							callback(e, null);
						} else {
							callback({"exception_occurred": e}, null);
						}
						return;
					};
					//passed all validation functions -> success
					callback(null, true);
				});
			});
		})
	}
	function fillInValidationOptions(db, options, callback) {
		if (!options) {
			options = {};
		}
		if (!options.secObj) {
			//a default security object
			options.secObj = {
				admins: {
					names: [],
					roles: []
				},
				members: {
					names: [],
					roles: []
				}
			};
		}
		if (!options.userCtx) {
			db.info(function (err, resp) {
				//a default userCtx
				options.userCtx = {
					db: resp.db_name,
					name: null,
					roles: []
				}
				callback(options);
			});
		} else {
			callback(options);
		}
	}

	function getValidationFunctions(db, callback) {
		db.allDocs({
			startkey: "_design/",
			endkey: "_design0",
			include_docs: true
		}, function (err, resp) {
			if (err) {
				callback(err, null);
				return;
			}
			var validationFuncs = resp.rows.map(function (row) {
				return {
					doc: row.doc,
					func: row.doc.validate_doc_update
				}
			});
			validationFuncs = validationFuncs.filter(function (info) {
				return typeof info.func !== "undefined";
			});
			try {
				validationFuncs = validationFuncs.map(function (info) {
					//convert str -> function
					return couchEval(info.doc, {}, info.func);
				});
			} catch (e) {
				callback({"exception_occurred": e}, null);
				return;
			}
			callback(null, validationFuncs);
		});
	}

	function getOldDoc(db, id, callback) {
		if (!id) {
			//TODO: without this, the browser console gives a:
			//DataError: Data provided to an operation does not meet requirements.
			//but that one should actually be handled by PouchDB I think
			//-> report a bug.
			callback({"error": "Invalid id..."}, null);
		}
		db.get(id, function (err, resp) {
			if (err) {
				callback(err, null);
			} else {
				callback(null, resp);
			}
		});
	}

	return {
		withValidation: {
			put: function (db, doc, options, callback) {
				if (!callback) {
					callback = options;
					options = {};
				}
				doValidation(db, doc, options, function (err, success) {
					if (err) {
						callback(err, null);
						return;
					}
					db.put(doc, options, callback);
				});
			},
			post: function (db, doc, options, callback) {
				if (!callback) {
					callback = options;
					options = {};
				}
				doValidation(db, doc, options, function (err, success) {
					if (err) {
						callback(err, null);
						return;
					}
					db.post(doc, options, callback);
				});
			},
			delete: function (db, doc, options, callback) {
				if (!callback) {
					callback = options;
					options = {};
				}
				doc._deleted = true;
				doValidation(db, doc, options, function (err, success) {
					if (err) {
						callback(err, null);
						return;
					}
					db.delete(doc, options, callback);
				});
			},
			bulkDocs: function (db, bulkDocs, options, callback) {
				if (!callback) {
					callback = options;
					options = {};
				}
				var passes = [];
				var failes = [];
				bulkDocs.docs.forEach(function (doc) {
					doValidation(db, doc, options, function (err, success) {
						if (err) {
							failes.push(err);
						} else {
							passes.push(success);
						}
						if (passes.length + failes.length === bulkDocs.docs.length) {
							if (failes.length) {
								callback(failes, null);
								return;
							}
							db.bulkDocs(bulkDocs, options, callback);
						}
					});
				});
			},
			//also add this for attachments?
		},
		show: function (db, showPath, callback) {
			var designDocName = showPath.split("/")[0];
			var showName = showPath.split("/")[1];
			var docId = showPath.split("/")[2];
			db.get("_design/" + designDocName, function (err, designDoc) {
				if (err) {
					callback(err, null);
				}
				db.get(docId, function (err, doc) {
					if (err) {
						callback(err, null);
					}
					var result;
					try {
						var func = couchEval(designDoc, {
							provides: provides
						}, designDoc.shows[showName]);
						result = func(doc, null);
					} catch (e) {
						callback({"exception_occurred": e}, null);
					}

					if (!result) {
						result = providesFuncs.html();
					}
					callback(null, result);
				});
			});
		}
	}
}());
