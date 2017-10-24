import sys
import re

from docx import Document
from bs4 import BeautifulSoup as BS
from json import dumps

class RPD():
	content = {}

	def __safe_get_text(self, element):
		try:
			return element.get_text().strip().lower()
		except:
			return ""

	def факультет(self, element):
		return {'факультет':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def кафедра(self, element):
		return {"кафедра":self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def проректор(self, element):
		n = 0
		while n < 10:
			n += 1
			element = element.nextSibling
			if element.name == 'w:tbl':
				break
		try:
			return {
				"проректор по учебной работе":
				re.sub(r"\s+", " ", re.sub(r"[\n\xa0_]", " ", element.get_text())).strip()
			}
		except AttributeError:
			pass
		return None

	def умкд(self, element):
		n = 0
		text = ""
		while n < 10:
			n += 1
			element = element.nextSibling
			try:
				text += re.sub(r"[\n\r\t]+", " ", element.get_text()).strip()
			except AttributeError:
				pass
		with open('/tmp/a', 'w') as f:
			f.write(text)
		return {
			"учебно-методический комплекс дисциплины":
			re.findall(r'[«"](.*)[»"]', text)[0].strip()
		}


	def parse(self):
		self.soup = BS(self.docx.element.xml)
		with open('log', 'w') as f:
			f.write(self.soup.prettify())
			f.close()
		for p in self.soup.find_all('w:p'):
			t = self.__safe_get_text(p)
			if t == "факультет":
				self.content.update(self.факультет(p))
			if t == "кафедра":
				self.content.update(self.кафедра(p))
			if t == "проректор по учебной работе":
				self.content.update(self.проректор(p))
			if t == "учебно-методический комплекс дисциплины":
				self.content.update(self.умкд(p))

		print(self.content)

	def __init__(self, docpath = "", content = {}):
		try:
			open(docpath)
			self.docx = Document(docpath)
			self.docpath = docpath
			self.parse()
		except FileNotFoundError:
			self.docx = Document()
		self.content = content

def test():
	rpd = RPD('РПД_дисциплины.docx')
	del rpd
	rpd = RPD()


if __name__ == '__main__':
	test()
