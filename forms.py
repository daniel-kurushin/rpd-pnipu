from bs4 import BeautifulSoup as BS

class LoginForm():
	"""Форма входа в систему."""
	def __init__(self, redirect = None, error = None):
		self.redirect = redirect
		self.error = error

		self.template = 'static/auth.html'
		self.soup = BS(open(self.template).read())

	def __str__(self):
		return self.soup.prettify()
