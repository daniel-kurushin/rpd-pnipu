import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
from threading import Thread
from time import sleep
from datetime import datetime

from database.users import users
from database.users import calc_hash
from database.users import set_auth_cookies, check_auth_cookies, del_auth_cookies

from exceptions import LoginError, WrongPasswordError, WrongUsernameError
from forms import LoginForm, LostForm, ConfirmExitFrom, SearchForm

class RPDRequestHandler(BaseHTTPRequestHandler):
	def _get_cookies(self):
		rez = {}
		try:
			pairs = [_.split("=") for _ in self.headers['Cookie'].split('; ')]
			for pair in pairs:
				try:
					key, value = pair
					rez.update({key:urllib.parse.unquote_plus(value)})
				except ValueError:
					pass
			return rez
		except AttributeError:
			return {}

	def _get_referer(self):
		try:
			_host = self.headers['Host']
			rez = self.headers['Referer'].split(_host)[1]
		except (KeyError, AttributeError, IndexError):
			rez = ''
		return rez

	def _get_params(self):
		rez = {}
		try:
			rez.update({'is_auth':0})
			rez = urllib.parse.parse_qs(self.path.split("?")[1])
		except IndexError:
			pass

		if not rez['is_auth']:
			try:
				is_auth, _user = check_auth_cookies(self._get_cookies())
				rez.update({
					"is_auth": is_auth,
					"username": _user
				})
			except WrongUsernameError:
				rez.update({"is_auth": 0})
		else:
			pass
			# TODO: убрать при релизе!

		try:
			prev_path = self._get_referer()
			rez.update({'referer':prev_path})
		except KeyError:
			pass

		print(rez)
		return rez

	def _send_cookies(self, cookies = {}):
		for cookie in cookies.keys():
			self.send_header('Set-Cookie', "%s=%s" % (cookie, urllib.parse.quote_plus(cookies[cookie])))

	def _load_file(self, name, context=None, content_type='text/html', cookies = {}):
		self.send_response(200)
		self._send_cookies(cookies)
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

	def _redirect(self, url, cookies = {}):
		"""редирект клиента с опциональным выставлением куков"""
		self.send_response(302)
		self.send_header('Location', url)
		self._send_cookies(cookies)
		self.end_headers()
		self.wfile.write(bytes('data', 'utf-8'))

	def _load_str(self, data, cookies = {}):
		self.send_response(200)
		self._send_cookies(cookies)
		self.end_headers()
		self.wfile.write(bytes(str(data), 'utf-8'))

	def _to_json(self, data):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(str.encode(json.dumps(data, indent = 4)))

	def _do_login(self, login = '', password = ''):
		try:
			_user = login
			_pass = password
			_hash = calc_hash("%s^%s" % (_user, _pass))
			print(_hash, users)
			if users[_user]['hash'] != _hash:
				raise WrongPasswordError('Неверный пароль для пользователя "%s"' % _user)
		except KeyError:
			raise WrongUsernameError('Нет пользователя с именем "%s"' % _user)
		self._redirect('/rpd_main/?%s' % urllib.parse.urlencode({'login':_user}), cookies = set_auth_cookies(_user))

	def show_login_form(self, login = None, password = None, redirect = None, error = None):
		self._load_str(
			LoginForm(
				login = login,
				password = password,
				redirect = redirect,
				error = error
			)
		)

	def show_lost_form(self):
		self._load_str(
			LostForm()
		)

	def show_confirm_form(self, _forward = None, _return = None):
		self._load_str(
			ConfirmExitFrom(_forward = _forward, _return = _return)
		)

	def show_search_form(self, _user = None, _query = None):
		self._load_str(
			SearchForm(username = _user, query = _query)
		)

	def do_GET(self):
		params = self._get_params()

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
		elif self.path  == '/':
			self._redirect('/auth/')
		elif self.path.startswith('/auth'):
			self.show_login_form()
		elif self.path.startswith('/lost'):
			self.show_lost_form()
		elif params['is_auth'] and self.path.startswith('/rpd_main'):
			self.show_search_form()
		elif params['is_auth'] and self.path.startswith('/logout'):
			if self.path.endswith('yes'):
				self._redirect('/auth/', cookies = del_auth_cookies(params['username']))
			else:
				self.show_confirm_form(_forward = '/logout/yes', _return = params['referer'])
		else:
			self._redirect('/auth/')

	def do_POST(self):
		data = urllib.parse.parse_qs(
			self.rfile.read(
				int(self.headers.get('content-length'))
			).decode('utf-8')
		)
		# print(self.path, data, file = sys.stderr)
		if self.path.startswith('/auth'):
			try:
				_user = data['login'][0]
				_pass = data['pass'][0]
				self._do_login(_user, _pass)
			except LoginError as e:
				self.show_login_form(login = _user, password = _pass, error = e)
			except KeyError as e:
				self.show_login_form(error = e)


if __name__ == '__main__':
	server = HTTPServer(('0.0.0.0', 8000), RPDRequestHandler)
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nfinished\n")
		exit(1)
