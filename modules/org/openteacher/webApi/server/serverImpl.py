#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
#
#	This file is part of OpenTeacher.
#
#	OpenTeacher is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenTeacher is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.

import os
import sqlite3
import functools

import flask
import werkzeug.exceptions
import bcrypt

app = flask.Flask("__main__")

#database
def getConnection():
	dbPath = app.config["DATABASE"]
	dbExists = os.path.exists(dbPath)
	connection = sqlite3.connect(dbPath)

	if not dbExists:
		cursor = connection.cursor()
		cursor.executescript("""
			PRAGMA foreign_keys = ON;

			CREATE TABLE users (
				id INTEGER PRIMARY KEY,
				username TEXT,
				hash TEXT,
				UNIQUE (username)
			);

			CREATE TABLE apikeys (
				key TEXT,
				PRIMARY KEY(key)
			);

			CREATE TABLE lists (
				id INTEGER PRIMARY KEY,
				owner NUMERIC,
				questionLanguage TEXT,
				answerLanguage TEXT,
				title TEXT,
				items TEXT,
				tests TEXT,
				FOREIGN KEY (owner) references users (id) ON DELETE CASCADE
			);

			CREATE TABLE shares (
				id INTEGER PRIMARY KEY,
				owner NUMERIC,
				name TEXT,
				description TEXT,
				UNIQUE (name),
				FOREIGN KEY (owner) references users (id) ON DELETE CASCADE
			);

			CREATE TABLE lists_shares (
				list_id NUMERIC,
				share_id NUMERIC,
				PRIMARY KEY (list_id, share_id),
				FOREIGN KEY (list_id) references lists (id) ON DELETE CASCADE,
				FOREIGN KEY (share_id) references shares(id) ON DELETE CASCADE
			);
		""")
		connection.commit()
		cursor.close()
	return connection

@app.before_request
def before_request():
	flask.g.connection = getConnection()
	flask.g.cursor = flask.g.connection.cursor()

@app.teardown_request
def teardown_request(exception):
	if hasattr(flask.g, "cursor"):
		flask.g.cursor.close()
	if hasattr(flask.g, "connection"):
		flask.g.connection.commit()
		flask.g.connection.close()

def query_db(query, args=(), one=False):
	flask.g.cursor.execute(query, args)
	rv = [dict((flask.g.cursor.description[idx][0], value) for idx, value in enumerate(row)) for row in flask.g.cursor.fetchall()]
	return (rv[0] if rv else None) if one else rv

#authentication
def newHash(password):
	return bcrypt.hashpw(password, bcrypt.gensalt())

def check_auth(username, password):
	data = query_db("SELECT id, hash FROM users WHERE username=?", (username,), one=True)
	if data is not None and bcrypt.hashpw(password, data["hash"]) == data["hash"]:
		flask.g.user_id = data["id"]
		return True
	else:
		return False

def authenticate():
	resp = do401()
	resp.headers["WWW-Authenticate"] = 'Basic realm="OpenTeacher Web API"'
	return resp

def requires_auth(f):
	@functools.wraps(f)
	def decorated(*args, **kwargs):
		auth = flask.request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated

#error handling
def make_json_error(ex):
	response = flask.jsonify(error=str(ex))
	response.status_code = (ex.code	if isinstance(ex, werkzeug.exceptions.HTTPException) else 500)
	return response

for code in werkzeug.exceptions.default_exceptions.iterkeys():
	app.error_handler_spec[None][code] = make_json_error

#router method helpers
def doResponse(status, message, error=True):
	resp = flask.jsonify({"error" if error else "result": message})
	resp.status_code = status
	return resp

doSuccess = lambda: doResponse(200, "success", False)
do401 = lambda: doResponse(401, "unauthorized")
do403 = lambda: doResponse(403, "forbidden")
do404 = lambda: doResponse(404, "not_found")

#actually routed methods
#index
@app.route("/api/", methods=["GET"])
def api_get_index():
	return flask.jsonify({
		"welcome": "OpenTeacher Web API",
		"version": "0.1",
		"resources": [
			flask.url_for("api_post_users"),
			flask.url_for("api_get_lists"),
			flask.url_for("api_get_shares"),
		],
	})

#users
@app.route("/api/users/", methods=["POST"])
def api_post_users():
	#check key
	apiKey = flask.request.form["apiKey"]
	key = query_db("SELECT key FROM apikeys WHERE key=?", (apiKey,), one=True)
	if app.config.get("KEYCHECK", True) and key is None:
		return do403()

	#create user
	username = flask.request.form["username"]
	hash = newHash(flask.request.form["password"])

	try:
		query_db("INSERT INTO users(username, hash) VALUES (?, ?)", (username, hash))
	except sqlite3.IntegrityError:
		return do403()
	return doSuccess()

@app.route("/api/users/<username>", methods=["PUT"])
@requires_auth
def api_put_user(username):
	if flask.request.authorization.username == username:
		newUsername = flask.request.form["username"]
		hash = newHash(flask.request.form["password"])

		try:	
			query_db("UPDATE users SET username=?, hash=? WHERE username=?", (newUsername, hash, username))
		except sqlite3.IntegrityError:
			return do403()
		else:
			return doSuccess()
	else:
		return do404()

@app.route("/api/users/<username>", methods=["DELETE"])
@requires_auth
def api_delete_user(username):
	if flask.request.authorization.username == username:
		query_db("DELETE FROM users WHERE username=?", (username,))
		if flask.g.cursor.rowcount:
			return doSuccess()
	#or 403, who cares
	return do404()

#lists
@app.route("/api/lists/", methods=["GET"])
@requires_auth
def api_get_lists():
	lists = query_db("SELECT id, title, questionLanguage, answerLanguage FROM lists WHERE owner=? ORDER BY title", (flask.g.user_id,))
	for list in lists:
		list["url"] = flask.url_for("api_get_list", id=list["id"])
	return flask.jsonify({"result": lists})

@app.route("/api/lists/", methods=["POST"])
@requires_auth
def api_post_lists():
	query_db("INSERT INTO lists(title, items, questionLanguage, answerLanguage, tests, owner) VALUES (?, ?, ?, ?, ?, ?)", (
		flask.request.form["title"],
		flask.request.form["items"],
		flask.request.form.get("questionLanguage", u""),
		flask.request.form.get("answerLanguage", u""),
		flask.request.form.get("tests", "[]"),
		flask.g.user_id,
	))
	return doSuccess()

@app.route("/api/lists/<id>", methods=["GET"])
@requires_auth
def api_get_list(id):
	list = query_db("SELECT id, title, questionLanguage, answerLanguage, items, tests FROM lists WHERE id=? AND owner=?", (id, flask.g.user_id), one=True)
	if list is not None:
		return flask.jsonify({"result": list})
	else:
		#or 403
		return do404()

@app.route("/api/lists/<id>", methods=["PUT"])
@requires_auth
def api_put_list(id):
	query_db("UPDATE lists SET title=?, items=?, questionlanguage=?, answerLanguage=?, tests=? WHERE id=? AND owner=?", (
		flask.request.form["title"],
		flask.request.form["items"],
		flask.request.form.get("questionLanguage", u""),
		flask.request.form.get("answerLanguage", u""),
		flask.request.form.get("tests", "[]"),
		id,
		flask.g.user_id,
	))
	if flask.g.cursor.rowcount:
		return doSuccess()
	else:
		#or 403
		return do404()

@app.route("/api/lists/<id>", methods=["DELETE"])
@requires_auth
def api_delete_list(id):
	query_db("DELETE FROM lists WHERE id=? AND owner=?", (id, flask.g.user_id))
	if flask.g.cursor.rowcount:
		return doSuccess()
	else:
		#or 403
		return do404()

#shares
@app.route("/api/shares/", methods=["GET"])
@requires_auth
def api_get_shares():
	shares = query_db("SELECT name, description FROM shares WHERE owner=?", (flask.g.user_id,))
	for share in shares:
		share["url"] = flask.url_for("api_get_share", name=share["name"])
	return flask.jsonify({"result": shares})

@app.route("/api/shares/", methods=["POST"])
@requires_auth
def api_post_shares():
	name = flask.request.form["name"]
	description = flask.request.form.get("description", u"")
	try:
		shares = query_db("INSERT INTO shares(name, description, owner) VALUES (?, ?, ?)", (name, description, flask.g.user_id))
	except sqlite3.IntegrityError:
		return do403()
	return doSuccess()

@app.route("/api/shares/<name>/", methods=["PUT"])
@requires_auth
def api_put_share(name):
	newName = flask.request.form["name"]
	description = flask.request.form["description"]
	query_db("UPDATE shares SET name=?, description=? WHERE name=? AND owner=?", (newName, description, name, flask.g.user_id))
	if flask.g.cursor.rowcount:
		return doSuccess()
	else:
		#or 403
		return do404()

@app.route("/api/shares/<name>/", methods=["GET"])
def api_get_share(name):
	share = query_db("SELECT id, name, description FROM shares WHERE name=?", (name,), one=True)
	if share is None:
		return do404()
	lists = query_db("SELECT list_id FROM lists_shares WHERE share_id=?", (share["id"],))
	#no need to expose to the users
	del share["id"]

	return flask.jsonify({"result": {
		"share": share,
		"lists": [
			flask.url_for("api_get_share_list", share_name=name, list_id=list["list_id"]) for list in lists
		],
	}})

@app.route("/api/shares/<name>/", methods=["DELETE"])
@requires_auth
def api_delete_share(name):
	query_db("DELETE FROM shares WHERE name=? AND owner=?", (name, flask.g.user_id))
	if flask.g.cursor.rowcount:
		return doSuccess()
	else:
		#or 403. Who cares.
		return do404()

@app.route("/api/shares/<share_name>/", methods=["POST"])
@requires_auth
def api_post_share_list(share_name):
	unsafe_list_id = flask.request.form["listId"]

	list_id = query_db("SELECT id FROM lists WHERE id=? AND owner=?", (unsafe_list_id, flask.g.user_id), one=True)
	share_id = query_db("SELECT id FROM shares WHERE name=? AND owner=?", (share_name, flask.g.user_id), one=True)
	if list_id is None or share_id is None:
		#or 403
		return do404()
	try:
		query_db("INSERT INTO lists_shares (list_id, share_id) VALUES (?, ?)", (list_id["id"], share_id["id"],))
	except sqlite3.IntegrityError:
		return do403()
	return doSuccess()

@app.route("/api/shares/<share_name>/<list_id>", methods=["GET"])
def api_get_share_list(share_name, list_id):
	list = query_db("SELECT l.title, l.questionLanguage, l.answerLanguage, l.items FROM lists l, lists_shares ls, shares s WHERE s.name = ? AND ls.share_id = s.id AND ls.list_id=l.id AND l.id=?", (share_name, list_id), one=True)
	if list is None:
		return do404()
	return flask.jsonify({"result": list})

@app.route("/api/shares/<share_name>/<list_id>", methods=["DELETE"])
@requires_auth
def api_delete_share_list(share_name, list_id):
	share_id = query_db("SELECT id FROM shares WHERE name=? AND owner=?", (share_name, flask.g.user_id), one=True)
	if share_id is None:
		#or 403
		return do404()
	query_db("DELETE FROM lists_shares WHERE share_id=? AND list_id=?", (share_id["id"], list_id,))
	if flask.g.cursor.rowcount:
		return doSuccess()
	else:
		return do404()

if __name__ == "__main__":
	app.run(debug=True)
