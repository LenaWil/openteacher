import requests
import json
import uuid
import logging
import os

logger = logging.getLogger(__name__)

def _only_access_for(username):
	return {
		"admins": {
			"names": [],
			"roles": [],
		},
		"members": {
			"names": [username],
			"roles": [],
		}
	}

class OTWebCouch(object):
	def __init__(self, host, username, password, dbSkeletonDir, isSafeHtmlCode, *args, **kwargs):
		super(OTWebCouch, self).__init__(*args, **kwargs)

		self._host = host
		self._username = username
		self._password = password

		self._codeDir = dbSkeletonDir
		self._validationLib = isSafeHtmlCode + "\n" + self._getJs("validationLib.js")
		self._presentationLib = self._getJs("presentationLib.js")

	def _getJs(self, endpoint):
		with open(os.path.join(self._codeDir, endpoint)) as f:
			return f.read()

	def _design_from(self, endpoint, additionalData):
		join = os.path.join

		base = join(self._codeDir, endpoint)
		parts = os.listdir(base)
		design_doc = {}

		if "validate_doc_update.js" in parts:
			design_doc["validate_doc_update"] = self._getJs(join(endpoint, "validate_doc_update.js"))

		for type in ["updates", "lists", "shows"]:
			if type in parts:
				design_doc[type] = {}

				allOfType = os.listdir(join(base, type))
				for oneOfTypeJs in allOfType:
					oneOfType = oneOfTypeJs[:-len(".js")]
					design_doc[type][oneOfType] = self._getJs(join(endpoint, type, oneOfTypeJs))

		if "views" in parts:
			design_doc["views"] = {}

			views = os.listdir(join(base, "views"))
			for view in views:
				viewObj = {
					"map": self._getJs(join(endpoint, "views", view, "map.js")),
				}
				reducePath = join(endpoint, "views", view, "reduce.js")
				if os.path.exists(join(self._codeDir, reducePath)):
					viewObj["reduce"] = self._getJs(reducePath)
				design_doc["views"][view] = viewObj

		design_doc.update(additionalData)
		return design_doc

	def _req(self, method, endpoint, data=None, auth=None):
		if data:
			data = json.dumps(data)
		if not auth:
			auth = requests.auth.HTTPBasicAuth(self._username, self._password)
		headers = {"Content-Type": "application/json"}
		func = getattr(requests, method)
		return func(self._host + endpoint, auth=auth, headers=headers, data=data)

	def new_user(self, username, password):
		if len(password) < 8 or password.isalnum():
			raise ValueError("unsafe_password")

		try:
			#user
			assert self._req("post", "/_users", ({
				"_id": "org.couchdb.user:" + username,
				"type": "user",
				"name": username,
				"password": password,
				"roles": [],
			})).status_code == 201

			#tests
			assert self._req("put", "/tests_" + username).status_code == 201
			assert self._req(
				"put",
				"/tests_" + username + "/_security",
				_only_access_for(username)
			).status_code == 200
			assert self._req("put", "/tests_" + username + "/_design/tests", self._design_from("tests", {
				"validation_lib": self._validationLib,
			})).status_code == 201

			#settings
			assert self._req("put", "/settings_" + username).status_code == 201
			assert self._req(
				"put",
				"/settings_" + username + "/_security",
				_only_access_for(username)
			).status_code == 200

			#lists
			assert self._req("put", "/lists_" + username).status_code == 201
			assert self._req(
				"put",
				"/lists_" + username + "/_security",
				_only_access_for(username)
			).status_code == 200

			assert self._req("put", "/lists_" + username + "/_design/lists", self._design_from("lists", {
				"validation_lib": self._validationLib,
				"presentation_lib": self._presentationLib,
			})).status_code == 201

			#shared_lists
			assert self._req("put", "/shared_lists_" + username).status_code == 201
			assert self._req("put", "/shared_lists_" + username + "/_security", {
				"admins": {
					"names": [],
					"roles": [],
				},
				"members": {
					"names": [],
					"roles": [],
				}
			}).status_code == 200
			assert self._req("put", "/shared_lists_" + username + "/_design/shares", self._design_from("shared_lists", {
				"presentation_lib": self._presentationLib,
			})).status_code == 201

			#replicator
			assert self._req("put", "/_replicator/lists_to_shared_lists_" + username, {
				"source": "lists_" + username,
				"target": "shared_lists_" + username,
				"continuous": True,
				"user_ctx": {
					"roles": ["_admin"],
				},
				#Workaround for https://issues.apache.org/jira/browse/COUCHDB-1415
				"random_value": str(uuid.uuid4()),
			}).status_code == 201
		except AssertionError, e:
			logger.debug(e, exc_info=True)
			try:
				self.delete_user(username, password)
			except ValueError:
				#delete as far as possible, but it'll probably crash since
				#create_user didn't succeed.
				pass
			raise ValueError("username_taken")

	def check_auth(self, username, password):
		session = self._req("get", "/_session", auth=requests.auth.HTTPBasicAuth(username, password)).json()
		return username == session["userCtx"]["name"]

	def delete_user(self, username, password):
		try:
			#no assertion, because this could actually fail, because the
			#order is different than in new_user. And it has to be this way
			#because the DB's that are replicated shouldn't be deleted
			#already when the replication is done.
			rev = json.loads(self._req("head", "/_replicator/lists_to_shared_lists_" + username).headers["Etag"])
			self._req("delete", "/_replicator/lists_to_shared_lists_" + username + "?rev=" + rev)

			rev = json.loads(self._req("head", "/_users/org.couchdb.user:" + username).headers["Etag"])
			assert self._req("delete", "/_users/org.couchdb.user:" + username + "?rev=" + rev).status_code == 200

			assert self._req("delete", "/tests_" + username).status_code == 200
			assert self._req("delete", "/settings_" + username).status_code == 200
			assert self._req("delete", "/lists_" + username).status_code == 200
			assert self._req("delete", "/shared_lists_" + username).status_code == 200
		except (AssertionError, KeyError), e:
			logger.debug(e, exc_info=True)
			raise ValueError("Error deleting user, aborted.")

	def test(self):
		#kind of the test suite... Pauses halfway to allow experimenting a
		#bit with a filled database before everything's deleted again.

		assert self._req("get", "/").json()["version"] >= "1.2.0"

		TEST_USER = "test"
		TEST_PASSW = "hsdfjkh3$4"

		TEST2_USER = "test2"
		TEST2_PASSW = "s2Sjgjk*92"

		self.new_user(TEST_USER, TEST_PASSW)
		testAuth = requests.auth.HTTPBasicAuth(TEST_USER, TEST_PASSW)

		listId = self._req("post", "/lists_test/_design/lists/_update/set_last_edited_to_now", {
			"shares": ["testShare", "testShareB"],
			"items": [
				{
					"id": 0,
					"questions": [["een"]],
					"answers": [["a single", "one"], ["a"]],
					"comment": u"Silly example...",
				},
				{
					"id": 1,
					"questions": [["twee"]],
					"answers": [["two"]],
				}
			],
			"title": "something"
		}, auth=testAuth).json()["_id"]
		self._req("post", "/tests_test", {
			"listId": listId,

            "finished": True, 
            "results": [
                {
                    "itemId": 0, 
                    "result": "right", 
                    "givenAnswer": "one, a",
                    "active": {
						"start":"2013-07-22T18:14:15.015Z",
						"end":"2013-07-22T18:14:23.637Z",
					},
				}, 
                {
                    "itemId": 1, 
                    "result": "wrong", 
                    "givenAnswer": "ttwo"
                },
            ], 
            "pauses": [],
		})

		self._req("post", "/lists_test/_design/lists/_update/set_last_edited_to_now", {
			"shares": ["testShare"],
			"title": "a"
		}, auth=testAuth)
		self._req("post", "/lists_test/_design/lists/_update/set_last_edited_to_now", {
			"shares": ["testShare"],
			"title": "b"
		}, auth=testAuth)
		self._req("post", "/lists_test/_design/lists/_update/set_last_edited_to_now", {
			"shares": ["testShareB"],
			"title": "c"
		}, auth=testAuth)
		self._req("post", "/lists_test/_design/lists/_update/set_last_edited_to_now", {
			"shares": [],
			"title": "d"
		}, auth=testAuth)
		self._req("post", "/settings_test", {
			"_id": "org.openteacher.test",
			"value": 123,
		}, auth=testAuth)

		#see: https://wiki.apache.org/couchdb/View_collation#Complex_keys
		try:
			assert len(self._req("get", '/lists_test/_design/lists/_view/by_title?startkey=["a"]&endkey=["b", {}]').json()["rows"]) == 2
			assert self._req("get", "/lists_test/_design/lists/_show/print/" + listId).status_code == 200
			assert len(self._req("get", "/shared_lists_test/_design/shares/_view/share_names?group=true").json()["rows"]) == 2
			assert len(self._req("get", '/shared_lists_test/_design/shares/_view/by_name?startkey=["testShareB"]&endkey=["testShareB", {}, {}]').json()["rows"]) == 2
			assert len(self._req("get", '/tests_test/_design/tests/_view/by_list_id?startkey=["%s"]&endkey=["%s", {}]&descending=true' % (listId, listId)).json()["rows"]) == 1
		except AssertionError, e:
			print e

		self.new_user(TEST2_USER, TEST2_PASSW)
		test2Auth = requests.auth.HTTPBasicAuth(TEST2_USER, TEST2_PASSW)

		try:
			assert self._req("get", "/lists_test/_design/list/_view/by_title", auth=test2Auth).status_code == 401
			assert self._req("get", "/shared_lists_test/_design/shares/_view/share_names?group=true").status_code == 200
			assert self._req("get", '/shared_lists_test/_design/shares/_view/by_name?startkey=["testShareB"]&endkey=["testShareB", {}, {}]').status_code == 200
			assert self._req("get", '/shared_lists_test/_design/shares/_list/feed/by_name?startkey=["testShareB"]&endkey=["testShareB", {}, {}]').status_code == 200
		except AssertionError:
			print e

		yield

		self.delete_user(TEST2_USER, TEST2_PASSW)
		self.delete_user(TEST_USER, TEST_PASSW)

		self._req("post", "/_users/_compact")
		self._req("post", "/_replicator/_compact")

if __name__ == "__main__":
	#CAUTION: This 'test runner' code passes in a stub for the
	#isSafeHtml function, making it possible to inject malicious html.
	#Do NOT use this in production.

	with open(os.path.join(os.path.dirname(__file__), "ot-web-config.json")) as f:
		config = json.load(f)
	couch = OTWebCouch(
		config["COUCHDB_HOST"],
		config["COUCHDB_ADMIN_USERNAME"],
		config["COUCHDB_ADMIN_PASSWORD"],
		os.path.join(os.path.dirname(__file__), "db_skeleton"),
		"function isSafeHtml () {return true;}"
	)

	iterator = couch.test()
	#set up
	next(iterator)
	raw_input("Press enter to continue... ")
	#and tear down
	try:
		next(iterator)
	except StopIteration:
		pass
