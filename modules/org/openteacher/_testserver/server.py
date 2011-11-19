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

import cherrypy
import cherrypy.wsgiserver
import cherrypy.wsgiserver.ssl_builtin

import os
import sys
import django.core.handlers.wsgi

def main():
	sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ot_testserver"))
	os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

	cherrypy.config.update({
		"server.ssl_certificate": "cert.pem",
		"server.ssl_private_key": "privatekey.pem",
		"server.socket_port": 8080,
	})

	cherrypy.tree.graft(django.core.handlers.wsgi.WSGIHandler(), "/")
	cherrypy.tree.mount(None, "/static/admin", {"/": {
			"tools.staticdir.on": True,
			"tools.staticdir.dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "admin_files")),
		}
	})
	cherrypy.engine.start()
	cherrypy.engine.block()

if __name__ == "__main__":
	main()
