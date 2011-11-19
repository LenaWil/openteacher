#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#
#	This file is part of OpenTeacher.
#
#	OpenTeacher is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenTeacher is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.

"""The tests server for OpenTeacher

Used HTTP status codes:
- 200 Ok
- 401 Unauthorized
- 500 Internal server error

Error responses:
{"error": "unauthorized"}
{"error": "username_unavailable"}
{"error": "short_name_unavailable"}
{"error": "invalid_id"}
{"error": "invalid_username"}
{"error": "invalid_role"}

Success responses:
{"success": "group_registered"}
{"success": "group_deregistered"}
{"success": "user_registered"}
{"success": "user_deregistered"}
{"success": "logged_in"}
{"success": "logged_out"}
{"success": "user_added"}
{"success": "user_removed"}
{"success": "group_added"}
{"success": "group_removed"}

"""
import cherrypy
import uuid
import sqlite3
import hashlib
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

def get_cursor():#FIXME?
	db_scheme = """
	PRAGMA foreign_keys = ON;
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY,
		username TEXT NOT NULL UNIQUE,
		role TEXT NOT NULL,
		hash TEXT NOT NULL,
		salt TEXT NOT NULL,
		real_name TEXT,
		mail TEXT
	);
	CREATE TABLE IF NOT EXISTS groups (
		id INTEGER PRIMARY KEY,
		short_name TEXT NOT NULL UNIQUE,
		long_name TEXT
	);
	CREATE TABLE IF NOT EXISTS groups_groups (
		parent_id INTEGER,
		child_id INTEGER,

		FOREIGN KEY(parent_id) REFERENCES groups ON DELETE CASCADE,
		FOREIGN KEY(child_id) REFERENCES groups ON DELETE CASCADE
	);
	CREATE TABLE IF NOT EXISTS groups_users (
		group_id INTEGER,
		user_id INTEGER,

		FOREIGN KEY(group_id) REFERENCES groups ON DELETE CASCADE,
		FOREIGN KEY(user_id) REFERENCES users ON DELETE CASCADE
	);

	CREATE TABLE IF NOT EXISTS tests (
		id INTEGER PRIMARY KEY,
		teacher_id INTEGER NOT NULL,
		title TEXT,
		question_language TEXT,
		answer_language TEXT,
		list TEXT NOT NULL,

		FOREIGN KEY(teacher_id) REFERENCES users(id)
	);
	CREATE TABLE IF NOT EXISTS tests_groups (
		test_id INTEGER,
		group_id INTEGER,

		FOREIGN KEY(test_id) REFERENCES tests ON DELETE CASCADE,
		FOREIGN KEY(group_id) REFERENCES groups ON DELETE CASCADE
	);
	CREATE TABLE IF NOT EXISTS test_users (
		test_id INTEGER,
		user_id INTEGER,

		FOREIGN KEY(test_id) REFERENCES tests ON DELETE CASCADE,
		FOREIGN KEY(user_id) REFERENCES users ON DELETE CASCADE
	);
	CREATE TABLE IF NOT EXISTS answers (
		test_id INTEGER,
		student_id INTEGER,
		list TEXT NOT NULL,

		FOREIGN KEY(test_id) REFERENCES tests ON DELETE CASCADE,
		FOREIGN KEY(student_id) REFERENCES users ON DELETE CASCADE
	);
	CREATE TABLE IF NOT EXISTS checked_answers (
		test_id INTEGER,
		student_id INTEGER,
		list TEXT NOT NULL,
		note TEXT,

		FOREIGN KEY(test_id) REFERENCES tests ON DELETE CASCADE,
		FOREIGN KEY(student_id) REFERENCES users ON DELETE CASCADE
	);

	"""
	db = sqlite3.connect("database.sqlite3")
	db.isolation_level = None
	cursor = db.cursor()
	for statement in db_scheme.split(";"):
		cursor.execute(statement)
	return cursor

class AuthorizationHelper(object):
	id = property(lambda: cherrypy.session.get("id"))

	@property
	def adminRegistered(self):
		cursor = get_cursor()
		cursor.execute(
			"SELECT count(role) FROM users WHERE role='admin'"
		)
		return bool(cursor.fetchone()[0])

	@property
	def role(self):
		if not self.id:
			return "guest"
		cursor = get_cursor()
		cursor.execute(
			"SELECT role FROM users WHERE id=?",
			(self.id,),
		)
		try:
			return cursor.fetchone()[0] #role
		except TypeError:
			#no username in database (anymore?)
			return "guest"

class UserHandler(object):
	def __init__(self, authorizationHelper, *args, **kwargs):
		super(UserHandler, self).__init__(*args, **kwargs)

		self._authorizationHelper = authorizationHelper

	@cherrypy.expose
	def index(self):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor()
		cursor.execute("SELECT id, username, role, real_name, mail FROM users")
		results = []
		for user in cursor:
			results.append({
				"id": user[0],
				"username": user[1],
				"role": user[2],
				"real_name": user[3],
				"mail": user[4],
			})
		return json.dumps(results)

	@cherrypy.expose
	def me(self):
		id = self._authorizationHelper.id
		if not id:
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor()
		cursor.execute(
			"SELECT id, username, role, real_name, mail FROM users WHERE id=?",
			(id,),
		)
		user = cursor.fetchone()
		return json.dumps({
			"id": user[0],
			"username": user[1],
			"role": user[2],
			"real_name": user[3],
			"mail": user[4],
		})

	@cherrypy.expose
	def register(self, username, role, hashed_password, **kwargs):
		if self._authorizationHelper.adminRegistered and self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		if (
			role not in ("admin", "student", "teacher") or #valid role name
			not self._authorizationHelper.adminRegistered and role != "admin" #only register admin when there's none.
		):
			cherrypy.response.status = 500
			return json.dumps({"error": "invalid_role"})
		salt = str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4())

		hash = hashlib.sha512()
		hash.update(hashed_password)
		hash.update(salt)

		values = [username, role, hash.hexdigest(), salt]

		try:
			values.append(kwargs["real_name"])
		except KeyError:
			values.append(None)
		try:
			values.append(kwargs["mail"])
		except KeyError:
			values.append(None)

		cursor = get_cursor()
		try:
			cursor.execute(
				"INSERT INTO users VALUES (null, ?, ?, ?, ?, ?, ?)",
				values
			)
		except sqlite3.IntegrityError:
			#username in use
			cherrypy.response.status = 500
			return json.dumps({"error": "username_unavailable"})
		return json.dumps({
			"success": "user_registered",
			"id": cursor.lastrowid
		})

	@cherrypy.expose
	def deregister(self, id):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor();
		cursor.execute(
			"DELETE FROM users WHERE id=?",
			(username,)
		)
		if cursor.rowcount:
			return json.dumps({"success": "user_deregistered"})
		else:
			cherrypy.response.status = 500
			return json.dumps({"error": "invalid_username"})

	@cherrypy.expose
	def login(self, username, hashed_password):
		cursor = get_cursor()
		cursor.execute(
			"SELECT	id, hash, salt FROM users WHERE username=?",
			(username,)
		)
		user = cursor.fetchone()
		hash = hashlib.sha512()
		hash.update(hashed_password)
		hash.update(user[2]) #salt
		if user[1] == hash.hexdigest(): #user[0] = saved hash
			cherrypy.session["id"] = user[0]
			return json.dumps({"success": "logged_in"})
		else:
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

	@cherrypy.expose
	def logout(self):
		try:
			del cherrypy.session["id"]
			return json.dumps({"success": "logged_out"})
		except KeyError:
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

class GroupHandler(object):
	def __init__(self, authorizationHelper, *args, **kwargs):
		super(GroupHandler, self).__init__(*args, **kwargs)

		self._authorizationHelper = authorizationHelper

	@cherrypy.expose
	def index(self, short_name):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor()
		cursor.execute("""
		SELECT
			short_name, long_name
		FROM
			groups
		WHERE
			short_name=?""", (short_name,))
		result = cursor.fetchone()
		return json.dumps({
			"short_name": result[0],
			"long_name": result[1],
		})

	@cherrypy.expose
	def groups(self, short_name):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor()
		cursor.execute("""
		SELECT
			child.id, child.short_name, child.long_name
		FROM
			groups parent,
			groups child,
			groups_groups gg
		WHERE
			parent.short_name = ?
		AND
			gg.parent_id = parent.id
		AND
			gg.child_id = child.id
		""", (short_name,))

		results = []
		for result in cursor:
			results.append({
				"id": result[0],
				"short_name": result[1],
				"long_name": result[2],
			})
		return json.dumps(results)

	@cherrypy.expose
	def users(self, short_name):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor()
		cursor.execute("""
		SELECT
			users.id, users.username, users.role, users.real_name, users.mail
		FROM
			groups,
			users,
			groups_users
		WHERE
			groups.short_name = ?
		AND
			groups_users.group_id = groups.id
		AND
			groups_users.user_id = users.id
		""", (short_name,))

		results = []
		for result in cursor:
			results.append({
				"id": result[0],
				"username": result[1],
				"role": result[2],
				"real_name": result[3],
				"mail": result[4],
			})
		return json.dumps(results)

	@cherrypy.expose
	def register(self, short_name, **kwargs):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		values = [short_name]
		try:
			values.append(kwargs["long_name"])
		except KeyError:
			values.append(None)

		cursor = get_cursor()
		try:
			cursor.execute(
				"INSERT INTO groups VALUES (null, ?, ?)",
				values
			)
		except sqlite3.IntegrityError:
			cherrypy.response.status = 500
			return json.dumps({
				"error": "short_name_unavailable",
			})
		return json.dumps({
			"success": "group_registered",
			"id": cursor.lastrowid,
		})

	@cherrypy.expose
	def deregister(self, id):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		cursor = get_cursor()
		cursor.execute("DELETE FROM groups WHERE id=?", (id,))
		if cursor.rowcount:
			return json.dumps({"success": "group_deregistered"})
		else:
			return json.dumps({"error": "invalid_id"})

	@cherrypy.expose
	def add_user(self, group_id, user_id):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		cursor = get_cursor()
		try:
			cursor.execute(
				"INSERT INTO groups_users VALUES (?, ?)",
				(group_id, user_id)
			)
		except sqlite3.IntegrityError:
			cherrypy.response.status = 500
			return json.dumps({
				"error": "invalid_id",
			})
		return json.dumps({
			"success": "user_added",
		})

	@cherrypy.expose
	def remove_user(self, group_id, user_id):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		cursor = get_cursor()
		cursor.execute(
			"DELETE FROM groups_users WHERE group_id=? AND user_id=?",
			(group_id, user_id)
		)
		if cursor.rowcount:
			return json.dumps({"success": "user_removed"})
		else:
			cherrypy.response.status = 500
			return json.dumps({"error": "invalid_id"})

	@cherrypy.expose
	def add_group(self, parent_id, child_id):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		cursor = get_cursor()
		try:
			cursor.execute(
				"INSERT INTO groups_groups VALUES (?, ?)",
				(parent_id, child_id)
			)
		except sqlite3.IntegrityError:
			cherrypy.response.status = 500
			return json.dumps({
				"error": "unauthorized"
			})
		return json.dumps({
			"succes": "group_added"
		})

	@cherrypy.expose
	def remove_group(self, parent_id, child_id):
		if self._authorizationHelper.role != "admin":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		cursor = get_cursor()
		cursor.execute(
			"DELETE FROM groups_groups WHERE parent_id=? AND child_id=?",
			(parent_id, child_id)
		)
		if cursor.rowcount:
			return json.dumps({"success": "group_removed"})
		else:
			cherrypy.response.status = 500
			return json.dumps({"error": "invalid_id"})

class TestsHandler(object):
	def __init__(self, authorizationHelper, *args, **kwargs):
		super(TestsHandler, self).__init__(*args, **kwargs)

		self._authorizationHelper = authorizationHelper

	@cherrypy.expose
	def register(self, list):
		if self._authorizationHandler.role != "teacher":
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		teacher_id = self._authorizationHandler.id
		title = list.get("title")
		question_language = list.get("questionLanguage")
		answer_language = list.get("answerLanguage")

		cursor.execute(
			"INSERT INTO tests VALUES (NULL, ?, ?, ?, ?, ?)",
			(teacher_id, title, question_language, answer_language, list)
		)

	@cherrypy.expose
	def users(self):
		pass

	@cherrypy.expose
	def groups(self):
		pass

	@cherrypy.expose
	def add_user(self, user_id):
		pass

	@cherrypy.expose
	def remove_user(self, user_id):
		pass

	@cherrypy.expose
	def add_group(self, group_id):
		pass

	@cherrypy.expose
	def remove_group(self, group_id):
		pass

	@cherrypy.expose
	def index(self, **kwargs):
		test_id = kwargs.get("test_id")
		return

class AnswersHandler(object):
	def __init__(self, authorizationHelper, *args, **kwargs):
		super(AnswersHandler, self).__init__(*args, **kwargs)

		self._authorizationHelper = authorizationHelper

	def _isTestTeacher(self):
		cursor = get_cursor()
		cursor.execute(
			"SELECT teacher_id FROM tests WHERE test_id=?",
			(test_id,)
		)
		return cursor.fetchone()[0] == self._authorizationHandler.id:

	def _isTestCandidate(self):
		"""Tells if the current user is allowed to make the test"""
		cursor = get_cursor()
		

	def _isTestStudent(self):
		"""Tells if the current user made the test"""
		cursor = get_cursor()
		cursor.execute("SELECT student_id FROM answers WHERE test_id=?")
		return cursor.fetchone()[0] == self._authorizationHandler.id

	@cherrypy.expose
	def answers(self, test_id, **kwargs):
		cursor = get_cursor()
		if self._isTestStudent():
			student_id = self._authorizationHandler.id
		elif self._isTestTeacher():
			#teacher
			student_id = kwargs.get(test_id)
			if not student_id:
				cursor.execute(
					"SELECT list FROM answers WHERE test_id=?",
					(test_id,)
				)
				#result[0] == list
				return json.dumps(map(lambda result: result[0], cursor))
		else:
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		cursor.execute(
			"SELECT list FROM answers WHERE test_id=? AND student_id=?",
			(test_id, student_id)
		)
		return json.dumps(cursor.fetchone()[0]) #list

	@cherrypy.expose
	def checked_answers(self, test_id, **kwargs):
		cursor = get_cursor()
		if self._isTestStudent():
			student_id = self._authorizationHandler.id
		elif self._isTestTeacher():
			#teacher
			student_id = kwargs.get(test_id)
			if not student_id:
				cursor.execute(
					"SELECT list, note FROM checked_answers WHERE test_id=?",
					(test_id,)
				)
				return json.dumps(map(
					lambda result: {"list": result[0], "note": result[1]},
					cursor
				))
		else:
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})

		cursor.execute(
			"SELECT list, note FROM checked_answers WHERE test_id=? AND student_id=?",
			(test_id, student_id)
		)
		result = cursor.fetchone()
		return json.dumps({
			"list": result[0],
			"note": result[1],
		})

	@cherrypy.expose
	def upload_answers(self, test_id, list):
		if not self._isTestCandidate():
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		student_id = self._authorizationHelper.id
		cursor = get_cursor()
		cursor.execute(
			"INSERT INTO answers VALUES (NULL, ?, ?, ?)",
			(test_id, student_id, answers)
		)

	@cherrypy.expose
	def upload_checked_answers(self, test_id, student_id, checked_list, note):
		if not self._isTestTeacher():
			cherrypy.response.status = 401
			return json.dumps({"error": "unauthorized"})
		student_id = self._authorizationHelper.id
		cursor = get_cursor()
		cursor.execute(
			"INSERT INTO checked_answers VALUES (NULL, ?, ?, ?, ?)",
			(test_id, student_id, checked_list, note)
		)

class Server(object):
	@cherrypy.expose
	def index(self):
		return json.dumps({
			"name": "OpenTeacher test server",
			"version": "1.0"
		})

class TestsServerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestsServerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testServer"

	def run(self):
		authorizationHelper = AuthorizationHelper()

		root = Server()
		root.user = UserHandler(authorizationHelper)
		root.group = GroupHandler(authorizationHelper)
		root.tests = TestsHandler(authorizationHelper)
		root.answers = AnswersHandler(authorizationHelper)
		cherrypy.quickstart(root, "", "config.ini")

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return TestsServerModule(moduleManager)

if __name__ == "__main__":
	init(None).run()

#TODO: some return values have to be added, fix fixme's and fill the functions that are now just passing.
