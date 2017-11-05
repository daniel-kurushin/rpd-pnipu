from bs4 import BeautifulSoup as BS

from exceptions import WrongPasswordError, WrongUsernameError

class LoginForm():
	"""Форма входа в систему."""
	def __init__(self, login = None, password = None, redirect = None, error = None):
		self.login = login
		self.password = password
		self.redirect = redirect
		self.error = error

		self.template = 'static/auth.html'

		self.soup = BS(open(self.template).read())

	def __str__(self):
		self._insert_data()
		if not self.error and not self.redirect:
			return self.soup.prettify()
		elif self.error:
			return self._insert_error()
		elif self.redirect:
			return self._insert_redirect()
		else:
			raise Exception("Непонятно!")

	def _insert_data(self):
		inputs = self.soup.find('login')('input')
		inputs[0]['value'] = self.login if self.login != None else ""
		inputs[1]['value'] = self.password if self.password != None else ""

	def _insert_error(self):
		inputs = self.soup.find('login')('input')
		if type(self.error) == WrongPasswordError:
			input_to_change_class = inputs[1]
		elif type(self.error) == WrongUsernameError:
			input_to_change_class = inputs[0]
		else:
			input_to_change_class = inputs[0]
		input_to_change_class['style'] = 'background-color:coral;'
		input_to_change_class['title'] = str(self.error)
		p = BS('<p><a href="/lost/">Забыли пароль?</a></p>').p
		inputs[2].insert_after(p)
		return self.soup.prettify()

	def _insert_redirect(self):
		input_to_change_class = self.soup.find('login').find('input')
		input_to_change_class['class'] = 'error'
		input_to_change_class['title'] = str(self.error)
		return self.soup.prettify()


class ConfirmExitFrom:
	def __init__(self, login = None, redirect = None, error = None):

		self.arg = arg
