import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
from threading import Thread
from time import sleep
from datetime import datetime

class RPDRequestHandler(BaseHTTPRequestHandler):
	pass

if __name__ == '__main__':
	server = HTTPServer(('0.0.0.0', 8000), RPDRequestHandler)
	server.serve_forever()
