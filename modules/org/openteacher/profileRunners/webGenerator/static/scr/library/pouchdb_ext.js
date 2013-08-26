var PouchDBext = (function () {
	function couchEval(requireContext, extraVars, program) {
		/*jshint evil:true*/
		var require;
		if (requireContext) {
			require = function (libPath) {
				var module = {
					id: libPath,
					//no way to fill in current and parent as far as I
					//know
					current: undefined,
					parent: undefined,
					exports: {}
				};
				var exports = module.exports;

				var path = libPath.split("/");
				var lib = requireContext;
				for (var i = 0; i < path.length; i += 1) {
					lib = lib[path[i]];
				}
				eval(lib);
				return module.exports;
			};
		}
		var isArray = Array.isArray;
		var toJSON = JSON.stringify;
		var log = console.log;
		var sum = function (array) {
			return array.reduce(function (a, b) {
				return a + b;
			});
		};

		var statements = "";
		for (var name in extraVars) {
			if (extraVars.hasOwnProperty(name)) {
				statements += "var " + name + " = extraVars['" + name + "'];\n";
			}
		}

		return eval(statements + program);
	}

	function buildProvidesCtx() {
		var providesFuncs = {};
		return {
			provides: function provides(type, func) {
				providesFuncs[type] = function () {
					return {
						code: 200,
						body: func()
					};
				};
			},
			funcs: providesFuncs
		};
	}

	function doValidation(db, newDoc, options, callback) {
		fillInValidationOptions(db, options, function (newOptions) {
			getValidationFunctions(db, function (err, validationFuncs) {
				if (err) {
					callback(err, null);
					return;
				}
				if (!validationFuncs.length) {
					//no validation functions -> success
					callback(null, true);
					return;
				}
				getOldDoc(db, newDoc._id, function (err, oldDoc) {
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
					}
					//passed all validation functions -> success
					callback(null, true);
				});
			});
		});
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
				};
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
				};
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
			//TODO: also add this for attachments?
		},
		show: function (db, showPath, callback) {
			var designDocName = showPath.split("/")[0];
			var showName = showPath.split("/")[1];
			var docId = showPath.split("/")[2];
			db.get("_design/" + designDocName, function (err, designDoc) {
				if (err) {
					callback(err, null);
					return;
				}
				db.get(docId, function (err, doc) {
					if (err) {
						callback(err, null);
					}
					var result;
					var providesCtx = buildProvidesCtx();
					try {
						var func = couchEval(designDoc, {
							provides: providesCtx.provides,
							registerTypes: function () {}
						}, designDoc.shows[showName]);
						result = func(doc, null);
					} catch (e) {
						callback({"exception_occurred": e}, null);
					}

					if (!result) {
						result = providesCtx.funcs.html();
					}
					callback(null, result);
				});
			});
		},
		list: function (db, listPath, opts, callback) {
			if (typeof opts === "function") {
				callback = opts;
				opts = {};
			}
			var designDocName = listPath.split("/")[0];
			var listName = listPath.split("/")[1];
			var viewName = listPath.split("/")[2];

			db.get("_design/" + designDocName, function (err, designDoc) {
				if (err) {
					callback(err, null);
					return;
				}
				db.query(designDocName + "/" + viewName, opts, function (err, view) {
					if (err) {
						callback(err, null);
						return;
					}
					var result;
					var sent = "";
					var providesCtx = buildProvidesCtx();
					var i = -1;
					try {
						var func = couchEval(designDoc, {
							provides: providesCtx.provides,
							registerTypes: function () {},
							getRow: function () {
								i += 1;
								return view.rows[i];
							},
							start: function () {},
							send: function (data) {
								sent += data;
							},
						}, designDoc.lists[listName]);
						//TODO: (head, req) arguments should make more sense.
						result = func(null, {
							info: {
								db_name: "shared_lists_test"
							},
							headers: {
								Host: COUCHDB_HOST.split("/")[2]
							},
							raw_path: "/shared_lists_test/_design/" + designDocName + "/_list/" + listName + "/" + viewName
						}) || "";
					} catch (e) {
						callback({"exception_occurred": e}, null);
					}

					result = sent + (result || "");
					if (!result) {
						//FIXME. Same for show()
						result = providesCtx.funcs.atom();
						result.body = sent + result.body;
					}
					callback(null, result);
				});
			});
		}
	};
}());
