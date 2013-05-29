#!/usr/bin/python3
#
# Copyright 2013 Zaccheo Bagnati
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import re
import cgi
import json
import http.client
import urllib.parse
import logging
logger = logging.getLogger(__name__)

registered_content_type_readers={}
registered_content_type_writers={}

def register_content_type_reader(content_type, reader):
	registered_content_type_readers[content_type] = reader

def register_content_type_writer(content_type, writer):
	registered_content_type_writers[content_type] = writer

class RESTError(Exception):
	def __init__(self, msg, http_status=400):
		self.http_status = http_status
		super(RESTError, self).__init__(msg)

class REST():
	REQUEST_METHODS = ('GET', 'POST', 'PUT', 'DELETE')

	def __init__(self, representation_content_type="application/json"):
		self.representation_content_type = representation_content_type
		self.registered_urls = {}
		for rm in self.REQUEST_METHODS:
			self.registered_urls[rm] = []
		logger.debug("REST instance created")

	def registerURL(self, url_regexp, request_method, resource_provider):
		self.registered_urls[request_method].append((url_regexp, resource_provider))

	def readREpresentation(self, content_type):
		try:
			read_data = registered_content_type_readers[content_type]
		except KeyError:
			raise RESTError("No reader defined for Content-type: {0}".format(content_type))
		return read_data()

	def writeREpresentation(self, resource, content_type):
		try:
			write_data = registered_content_type_writers[content_type]
		except KeyError:
			raise RESTError("No writer defined for Content-type: {0}".format(content_type))
		return write_data(resource)


	def application(self, environ, start_response):
		sys.stderr.write(repr(environ))
		sys.stderr.write("\n")
		request_method = environ.get("REQUEST_METHOD")
		request_url = environ.get("PATH_INFO")
		try:
			if request_method not in self.REQUEST_METHODS:
				raise RESTError("Unhandled REQUEST_METHOD {0}".format(request_method))

			out = None
			status = None
			headers = [('Content-type', self.representation_content_type)]

			for (url_regexp, resource_provider) in self.registered_urls[request_method]:
				mo = re.match(request_url, url_regexp)
				if mo:
					if request_method in ('POST', 'PUT') and environ.get('CONTENT_TYPE') != None:
						#This methods can send data
						data = self.readREpresentation(environ.get('CONTENT_TYPE'))
					else:
						data = None
					resource = resource_provider(request_method, mo.groups(), data)
					out = self.writeREpresentation(resource, self.representation_content_type)
					status = 200

			if status == None:
				raise RESTError("Resource {0} not found for method {1}".format(request_url, request_method), http_status=404)

		except RESTError as err:
			status = err.http_status
			out = self.writeREpresentation(str(err), self.representation_content_type)
			
		except Exception as err:
			status = 400
			out = self.writeREpresentation(str(err), self.representation_content_type)

		headers.append(("Content-length", str(len(out))))
		start_response("{0} {1}".format(status, http.client.responses[status]), headers)
		return [out]
	


def JSONWriter(data):
	return json.dumps(data).encode('UTF8')
register_content_type_writer('application/json', JSONWriter)

def JSONReader():
	return json.load(sys.stdin)
register_content_type_reader('application/json', JSONReader)

def defaultCGIReader():
	return cgi.FieldStorage()
register_content_type_reader('application/x-www-form-urlencoded', defaultCGIReader)
register_content_type_reader('multipart/form-data', defaultCGIReader)
