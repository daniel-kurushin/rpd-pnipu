import sys
import re

from docx import Document
from bs4 import BeautifulSoup as BS
from json import dumps

from compare import ngramm_compare as NC
from compare import ngramm_compare_phrase as NCP
from compare import MIN_W, MIN_P

class RPD():
	content = {}

	def __safe_get_text(self, element):
		try:
			return re.sub(r"[\t\r\n]+", " ", element.get_text().strip().lower())
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

	def программа(self, element):
		return {'программа':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def направление_подготовки(self, element):
		_ = self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])
		шифр = re.findall(r"(\d+\.\d+\.\d+)", _)[0]
		наименование = re.findall(r"'(.*)'", _)[0]
		return {'направление подготовки': {'шифр':шифр, 'наименование':наименование}}

	def parse(self):
		self.soup = BS(self.docx.element.xml)
		with open('log', 'w') as f:
			f.write(self.soup.prettify())
			f.close()
		for p in self.soup.find_all('w:p'):
			t = self.__safe_get_text(p)
			if NC(t, "факультет") > MIN_W:
				self.content.update(self.факультет(p))
			if NC(t, "кафедра") > MIN_W:
				self.content.update(self.кафедра(p))
			if NCP(t, "проректор по учебной работе") > MIN_P:
				self.content.update(self.проректор(p))
			if NCP(t, "учебно-методический комплекс дисциплины") > MIN_P:
				self.content.update(self.умкд(p))
			if NC(t, "программа") > MIN_W:
				self.content.update(self.программа(p))
			if NCP(t, "направление подготовки") > MIN_P:
				self.content.update(self.направление_подготовки(p))


		print(dumps(self.content, indent = 4, ensure_ascii = 0))

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
