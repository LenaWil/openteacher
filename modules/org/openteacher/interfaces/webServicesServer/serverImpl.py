#FIXME: translations

import flask
import recaptcha.client.captcha
import functools
import collections
import json
import os
import contextlib

#import otCouch is handled by the module.

app = flask.Flask(__name__)

#utils
@app.before_request
def before_request():
	flask.g.couch = otCouch.OTWebCouch(app.config["COUCHDB_HOST"], app.config["COUCHDB_ADMIN_USERNAME"], app.config["COUCHDB_ADMIN_PASSWORD"])

def requires_auth(f):
	@functools.wraps(f)
	def decorated(*args, **kwargs):
		auth = flask.request.authorization
		if not auth or not flask.g.couch.check_auth(auth.username, auth.password):
			resp = flask.jsonify({"error": "authentication_required"})
			resp.status_code = 401
			resp.headers["WWW-Authenticate"] = 'Basic realm="OpenTeacher Web"'
			return resp
		return f(*args, **kwargs)
	return decorated

#services
@app.route("/", methods=["GET"])
def services():
	data = collections.OrderedDict([
		("welcome", "OpenTeacher Web services"),
		("entry_points", [
			flask.url_for("services_register"),
			flask.url_for("services_deregister"),
		]),
	])
	resp = flask.make_response(json.dumps(data, indent=4))
	resp.headers["Content-Type"] = "application/json"
	return resp

@app.route("/register", methods=["GET"])
def services_register():
	try:
		redirect = flask.request.args["redirect"]
	except KeyError:
		return "<h1>Required GET URL parameter: redirect.</h1>"
	screenshotOnly = flask.request.args.get("screenshotonly", "false")

	error = {
		"invalid_captcha": "Invalid captcha. Please try again.",
		"unsafe_password": "Your password should at least be 8 characters long, and contain special (non alphanumeric) characters. Please try again.",
		"username_taken": "The username you requested is already taken. Please try again."
	}.get(flask.request.args.get("error"), u"")
	if screenshotOnly == "true":
		captcha = ""
	else:
		publicKey = app.config["RECAPTCHA_PUBLIC_KEY"]
		captcha = recaptcha.client.captcha.displayhtml(publicKey)

	data = {"captcha": captcha, "redirect": redirect, "error": error}
	with open(os.path.join(os.path.dirname(__file__), "register-template.html")) as f:
		return flask.render_template_string(f.read(), **data)

@app.route("/register/send", methods=["POST"])
def services_register_send():
	redirect_url = flask.request.form["redirect"]
	def error(e):
		return flask.redirect(flask.url_for("services_register") + "?error=" + e + "&redirect=" + redirect_url)

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

@app.route("/deregister", methods=["POST"])
@requires_auth
def services_deregister():
	try:
		flask.g.couch.delete_user(auth.username, auth.password)
	except ValueError, e:
		resp = flask.jsonify({"error": str(e)})
		resp.status_code = 400
		return resp
	return flask.jsonify({"result": "ok"})

with contextlib.ignored(IOError):
	with open(os.path.join(os.path.dirname(__file__), "ot-web-config.json")) as f:
		app.config.update(json.load(f))
