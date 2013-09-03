import flask
import recaptcha.client.captcha
import functools
import collections
import superjson
import tempfile
import os
import datetime
import json
import contextlib

#Imports handled by the module:
#
#import createWebDatabase
#import gettextFunctions
#import loaders
#import savers

app = flask.Flask(__name__)

class DummyLesson(object):
	def __init__(self, list, *args, **kwargs):
		super(DummyLesson, self).__init__(*args, **kwargs)

		self.list = list
		self.resources = {}

#utils
@app.before_request
def before_request():
	flask.g.couch = createWebDatabase(
		app.config["COUCHDB_HOST"],
		app.config["COUCHDB_ADMIN_USERNAME"],
		app.config["COUCHDB_ADMIN_PASSWORD"],
	)

def requires_auth(f):
	def auth_err(msg):
		resp = jsonErr(msg, 401)
		resp.headers["WWW-Authenticate"] = 'Basic realm="OpenTeacher Web"'
		return resp

	@functools.wraps(f)
	def decorated(*args, **kwargs):
		auth = flask.request.authorization
		if not auth and flask.request.form.get("username"):
			auth = {
				"username": flask.request.form.get("username"),
				"password": flask.request.form.get("password", ""),
			}
		if not auth:
			return auth_err("authentication_required")
		if not flask.g.couch.check_auth(auth["username"], auth["password"]):
			return auth_err("wrong_username_or_password")
		return f(*args, **kwargs)
	return decorated

#Thanks Armin Ronacher! See: http://flask.pocoo.org/snippets/56/
def crossdomain(origin=None, methods=None, headers=None, credentials="false", max_age=21600, attach_to_all=True, automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	if isinstance(max_age, datetime.timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and flask.request.method == 'OPTIONS':
				resp = app.make_default_options_response()
			else:
				resp = flask.make_response(f(*args, **kwargs))
			if not attach_to_all and flask.request.method != 'OPTIONS':
				return resp

			h = resp.headers

			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			if credentials:
				h['Access-Control-Allow-Credentials'] = "true"
			return resp

		f.provide_automatic_options = False
		return functools.update_wrapper(wrapped_function, f)
	return decorator

def allowCrossDomainFromTrustedOrigins(f):
	return crossdomain(origin=app.config["TRUSTED_ORIGINS"], credentials=True, headers="authorization")(f)

def jsonErr(msg, code=400):
	resp = jsonify({"error": msg})
	resp.status_code = code
	return resp

def load_exts(_cache=[]):
	if not _cache:
		for loader in loaders:
			for ext, dataTypes in loader.loads.iteritems():
				if "words" in dataTypes:
					_cache.append(ext)
	return _cache

def save_exts(_cache=[]):
	if not _cache:
		for saver in savers:
			_cache.extend(saver.saves.get("words", []))
	return _cache

def jsonDefault(item):
	try:
		return item.isoformat()
	except AttributeError, e:
		raise TypeError("Can't provide a default value")

def jsonify(data):
	dataJson = superjson.dumps(data, indent=4, default=jsonDefault)
	resp = flask.make_response(dataJson)
	resp.headers["Content-Type"] = "application/json"
	return resp

def initialize_endpoints():
	#services
	@app.route("/", methods=["OPTIONS", "GET"])
	@allowCrossDomainFromTrustedOrigins
	def services():
		data = collections.OrderedDict([
			("welcome", "OpenTeacher Web services"),
			("info", "All api entry points require HTTP Basic Authentication."),
			("web_entry_points", [
				flask.url_for("register"),
			]),
			("api_entry_points", [
				flask.url_for("deregister"),
				flask.url_for("load"),
				flask.url_for("supported_load_extensions"),
				flask.url_for("save"),
				flask.url_for("supported_save_extensions"),
			])
		])
		return jsonify(data)

	@app.route("/register")
	def register():
		try:
			redirect = flask.request.args["redirect"]
		except KeyError:
			return "<h1>Required GET URL parameter: redirect.</h1>"
		try:
			language = flask.request.args["language"]
		except KeyError:
			return "<h1>Required GET URL parameter: language. ('C' will suffice if your app is available in English only.)</h1>"
		screenshotOnly = flask.request.args.get("screenshotonly", "false")

		_, ngettext = gettextFunctions(language)

		error = {
			"invalid_captcha": _("Invalid captcha. Please try again."),
			"unsafe_password": _("Your password should at least be %s characters long, and contain special (non alphanumeric) characters. Please try again.") % 8,
			"username_taken": _("The username you requested is already taken. Please try again.")
		}.get(flask.request.args.get("error"), u"")

		if screenshotOnly == "true":
			#fetching a captcha is too much overhead when the website is
			#just shown for 'screenshot' purposes.
			captcha = ""
		else:
			publicKey = app.config["RECAPTCHA_PUBLIC_KEY"]
			captcha = recaptcha.client.captcha.displayhtml(publicKey)

		data = {"captcha": captcha, "redirect": redirect, "error": error, "_": _, "ngettext": ngettext, "language": language}
		with open(app.config["REGISTER_TEMPLATE_PATH"]) as f:
			return flask.render_template_string(f.read(), **data)

	@app.route("/register/send", methods=["OPTIONS", "POST"])
	def register_send():
		redirect_url = flask.request.form["redirect"]
		language = flask.request.form["language"]
		def error(e):
			return flask.redirect(flask.url_for("register") + "?error=" + e + "&redirect=" + redirect_url + "&language=" + language)

		try:
			challenge = flask.request.form["recaptcha_challenge_field"]
			response = flask.request.form["recaptcha_response_field"]
		except KeyError:
			return error("invalid_captcha")

		private_key = app.config["RECAPTCHA_PRIVATE_KEY"]
		ip = flask.request.remote_addr
		valid = recaptcha.client.captcha.submit(challenge, response, private_key, ip).is_valid
		if not valid:
			return error("invalid_captcha")

		username = flask.request.form["username"]
		password = flask.request.form["password"]
		try:
			flask.g.couch.new_user(username, password)
		except ValueError, e:
			return error(str(e))

		return flask.redirect(redirect_url + "?status=ok")

	@app.route("/deregister", methods=["OPTIONS", "POST"])
	@allowCrossDomainFromTrustedOrigins
	@requires_auth
	def deregister():
		auth = flask.request.authorization
		try:
			flask.g.couch.delete_user(auth.username, auth.password)
		except ValueError, e:
			return jsonErr(str(e))
		return jsonify({"result": "ok"})

	@app.route("/load/supported_extensions", methods=["GET", "OPTIONS"])
	@allowCrossDomainFromTrustedOrigins
	@requires_auth
	def supported_load_extensions():
		return jsonify({"result": load_exts()})

	@app.route("/load", methods=["OPTIONS", "POST"])
	@allowCrossDomainFromTrustedOrigins
	@requires_auth
	def load():
		try:
			f = flask.request.files["file"]
		except KeyError, e:
			return jsonErr("Please upload a file (name='file')")
		ext = os.path.splitext(f.filename)[1]
		#strip the . in .otwd
		if not ext[1:] in load_exts():
			return jsonErr("Invalid file type for the uploaded file.")

		fd, path = tempfile.mkstemp(ext)
		os.close(fd)
		f.save(path)

		resp = jsonErr("Couldn't load file")
		for loader in loaders:
			if loader.getFileTypeOf(path) == "words":
				try:
					result = loader.load(path)
				except Exception:
					continue
				else:
					resp = jsonify(result["list"])
					break

		os.remove(path)
		return resp

	@app.route("/save/supported_extensions", methods=["GET", "OPTIONS"])
	@allowCrossDomainFromTrustedOrigins
	@requires_auth
	def supported_save_extensions():
		return jsonify({"result": save_exts()})

	@app.route("/save", methods=["OPTIONS", "POST"])
	@allowCrossDomainFromTrustedOrigins
	@requires_auth
	def save():
		try:
			list = json.loads(flask.request.form["list"])
		except KeyError:
			return jsonErr("Please specify the 'list' field in the body form data.")
		except ValueError:
			return jsonErr("The posted list is invalid json.")

		dateFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
		for item in list.get("items", []):
			with contextlib.ignored(KeyError):
				item["created"] = datetime.datetime.strptime(item["created"], dateFormat)
		for test in list.get("tests", []):
			for result in test.get("results", []):
				with contextlib.ignored(KeyError):
					result["active"]["start"] = datetime.datetime.strptime(result["active"]["start"], dateFormat)
					result["active"]["end"] = datetime.datetime.strptime(result["active"]["end"], dateFormat)
		lesson = DummyLesson(list)

		try:
			filename = flask.request.form["filename"]
		except KeyError:
			return jsonErr("Please specify the 'filename' field in the body form data.")

		#[1:] tears of the . in .txt
		ext = os.path.splitext(filename)[1][1:]
		if not ext in save_exts():
			return jsonErr("Unsupported filename extension. (%s)" % ext)

		fd, path = tempfile.mkstemp(ext)
		os.close(fd)
		for saver in savers:
			if ext in saver.saves.get("words", []):
				saver.save("words", lesson, path)
				resp = flask.send_file(path, as_attachment=True, attachment_filename=filename)
				break

		os.remove(path)
		return resp
