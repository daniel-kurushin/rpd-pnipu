from bs4 import BeautifulSoup as BS

class ConfirmExitFrom:
	"""Форма подтверждения выхода - тест работы с реферером"""
	def __init__(self, _forward = None, _return = None):
		self._forward = _forward
		self._return = _return
		self.template = 'static/confexit.html'

		self.soup = BS(open(self.template).read())

	def _insert_data(self):
		yes = self.soup('yes')[0]
		no = self.soup('no')[0]
		yes.a['href'] = self._forward
		no.a['href'] = self._return

	def __str__(self):
		self._insert_data()
		return self.soup.prettify()
