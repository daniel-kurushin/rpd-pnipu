import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
from threading import Thread
from time import sleep
from datetime import datetime

from database.users import users
from database.users import calc_hash

from exceptions import LoginError
from forms import LoginForm

class RPDRequestHandler(BaseHTTPRequestHandler):
	def _load_file(self, name, context=None, content_type='text/html'):
		self.send_response(200)
		self.send_header('Content-type', content_type)
		self.end_headers()
		data = ''
		with open(name, 'rb') as _file:
			data = _file.read()
		if context:
			for key in context:
				data = data.replace(
					bytes(key, 'utf-8'),
					bytes(context[key], 'utf-8')
				)
		self.wfile.write(data)

	def _redirect(self, url, cookies = ""):
		"""редирект клиента с опциональным выставлеинем куков"""
		self.send_response(302)
		self.send_header('Location', url)
		if cookies:
			self.send_header('Set-Cookie', cookies)
		self.end_headers()
		self.wfile.write(bytes('data', 'utf-8'))

	def _load_str(self, data):
		self.send_response(200)
		self.end_headers()
		self.wfile.write(bytes(str(data), 'utf-8'))

	def _to_json(self, data):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(str.encode(json.dumps(data, indent = 4)))

	def _do_login(self, data):
		try:
			_user = data['login'][0]
			_pass = data['pass'][0]
			_hash = calc_hash("%s^%s" % (_user, _pass))
			print(_hash, users)
			if users[_user]['hash'] != _hash:
				raise LoginError('Неверный пароль для порльзователя "%s"' % _user)
		except KeyError:
			raise LoginError('Нет пользователя с именем "%s"' % _user)
		self._redirect('/rpd_main/?%s' % urllib.parse.urlencode({'login':_user}))

	def show_login_form(self, redirect = None, error = None):
		self._load_str(
			LoginForm(
				redirect = redirect,
				error = error
			)
		)

	def do_GET(self):
		if self.path.endswith('png'):
			self._load_file(self.path.lstrip('/'), content_type='image/png')
		elif self.path.endswith('jpg'):
			self._load_file(self.path.lstrip('/'), content_type='image/jpeg')
		elif self.path.startswith('/static'):
			content_type = 'text/html'
			if self.path.endswith('jpg'):
				content_type = 'image/jpeg'
			elif self.path.endswith('css'):
				content_type = 'text/css'
			self._load_file(self.path.lstrip('/'), content_type=content_type)
		elif self.path.startswith('/auth'):
			self.show_login_form()
		elif self.path.startswith('/rpd_main'):
			self._load_file('static/rpd_main.html')
		else:
			self._load_file('index.html')

	def do_POST(self):
		data = urllib.parse.parse_qs(
			self.rfile.read(
				int(self.headers.get('content-length'))
			).decode('utf-8')
		)
		print(self.path, data, file = sys.stderr)
		if self.path.startswith('/auth'):
			try:
				self._do_login(data)
			except LoginError as e:
				self.show_login_form(e)


if __name__ == '__main__':
	server = HTTPServer(('0.0.0.0', 8000), RPDRequestHandler)
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nfinished\n")
		exit(1)
