#!/usr/bin/python3

import restngo
import logging
import os
from cgi import FieldStorage, MiniFieldStorage
from wsgiref.simple_server import make_server


def test(m, urlcomponents, data):
	dataout = {}
	if isinstance(data, FieldStorage) or isinstance(data, MiniFieldStorage):
		for k in data.keys():
			dataout[k] = data.getfirst(k)
	else:
		dataout = data
	return {"msg": "Resource test called with method {0}".format(m), "data": dataout}

def env(m, urlcomponents, data):
	return dict(os.environ)

def main():
	logger = logging.getLogger('rest')
	logger.setLevel(logging.DEBUG)
	lh = logging.StreamHandler()
	lh.setLevel(logging.DEBUG)
	lf = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	lh.setFormatter(lf)
	logger.addHandler(lh)

	r = restngo.REST()
	r.registerURL("/test", "GET", test)
	r.registerURL("/test", "POST", test)
	r.registerURL("/test", "PUT", test)
	r.registerURL("/test", "DELETE", test)
	r.registerURL("/env", "POST", env)

	
	httpd = make_server('localhost', 8080, r.application)
	httpd.serve_forever()

if __name__ == '__main__':
	main()
