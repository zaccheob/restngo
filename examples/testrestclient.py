#!/usr/bin/python3
import sys
import http.client
import urllib.parse
import json
import argparse

def make_request(url, method, content_type, data, filename):
	u = urllib.parse.urlparse(url)
	httpconn=http.client.HTTPConnection(u.netloc)
	try:
		if method in ('POST', 'PUT') and data != None:
			data = eval(data)
			if content_type=="application/json":
				body = json.dumps(data)
			elif content_type=="application/x-www-form-urlencoded":
				body = urllib.parse.urlencode(data)
			else:
				raise ValueError("Unhandled content_type: {0}".format(content_type))
		else:
			body=None
		httpconn.connect()
		httpconn.request(method, u.path, body=body, headers={'Content-type': 'application/x-www-form-urlencoded'})
		response = httpconn.getresponse()
		print("DEBUG: body: %s" % body)
		print("Request: {0} {1}".format(method, url))
		print("Response status: {0} {1}".format(response.status, response.reason))
		print("Response headers:")
		for header in response.getheaders():
			print(header)
		print("Response body:")
		print(response.read())
		#print(json.loads(response.read().decode()))
	finally:
		httpconn.close()


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("url", help="URL of resource to request")
	parser.add_argument("--method", help="HTTP method of the request", choices=["GET", "POST", "PUT", "DELETE"], default="GET")
	parser.add_argument("--body", help="Data to send in body (as python dictionary)")
	parser.add_argument("--file", help="File to send")
	parser.add_argument("--content_type", help="Content type for data to send in body", choices=["application/json", "application/x-www-form-urlencoded"], default="application/x-www-form-urlencoded")
	args = parser.parse_args()
	make_request(args.url, args.method, args.content_type, args.body, args.file)

if __name__ == '__main__':
	main()
