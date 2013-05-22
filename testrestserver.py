#!/usr/bin/python3

import rest
import logging
import os
from cgi import FieldStorage, MiniFieldStorage


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

	r = rest.REST()
	r.registerURL("/test", "GET", test)
	r.registerURL("/test", "POST", test)
	r.registerURL("/test", "PUT", test)
	r.registerURL("/test", "DELETE", test)
	r.registerURL("/env", "POST", env)

	r.manage_request()

if __name__ == '__main__':
	main()
