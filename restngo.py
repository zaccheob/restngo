#!/usr/bin/python3

import sys
import os
import re
import cgi
import json
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


	def manage_request(self):
		request_method = os.environ.get("REQUEST_METHOD")
		request_url = os.environ.get("REQUEST_URI")
		try:
			if request_method not in self.REQUEST_METHODS:
				raise RESTError("Unhandled REQUEST_METHOD {0}".format(request_method))

			for (url_regexp, resource_provider) in self.registered_urls[request_method]:
				mo = re.match(request_url, url_regexp)
				if mo:
					if request_method in ('POST', 'PUT') and os.environ.get('CONTENT_TYPE') != None:
						#This methods can send data
						data = self.readREpresentation(os.environ.get('CONTENT_TYPE'))
					else:
						data = None
					resource = resource_provider(request_method, mo.groups(), data)
					out = self.writeREpresentation(resource, self.representation_content_type)
					sys.stdout.write("Content-type: {0}\n\n".format(self.representation_content_type))
					print(out)
					return

			raise RESTError("Resource {0} not found for method {1}".format(request_url, request_method), http_status=404)

		except RESTError as err:
			sys.stdout.write("Status:{0}\nContent-type: {1}\n\n".format(err.http_status, self.representation_content_type))
			print(self.writeREpresentation(str(err), self.representation_content_type))
			
		except Exception as err:
			sys.stdout.write("Status:400\nContent-type: {0}\n\n".format(self.representation_content_type))
			print(self.writeREpresentation(str(err), self.representation_content_type))
	


def JSONWriter(data):
	return json.dumps(data)
register_content_type_writer('application/json', JSONWriter)

def JSONReader():
	return json.load(sys.stdin)
register_content_type_reader('application/json', JSONReader)

def defaultCGIReader():
	return cgi.FieldStorage()
register_content_type_reader('application/x-www-form-urlencoded', defaultCGIReader)
register_content_type_reader('multipart/form-data', defaultCGIReader)
