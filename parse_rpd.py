import sys
import re

from docx import Document
from bs4 import BeautifulSoup as BS
from json import dumps

from compare import ngramm_compare as NC
from compare import ngramm_compare_phrase as NCP
from compare import MIN_W, MIN_P
from pymystem3 import Mystem

class RPD():
	content = {}

	def __safe_get_text(self, element):
		try:
			return re.sub(r"[\t\r\n]+", " ", element.get_text().strip().lower())
		except:
			return ""

	def __is_not_set(self, key):
		try:
			self.content[key]
			return False
		except KeyError:
			return True

	def __find_end_of_text(self, element, const, limit = 20):
		n = 0
		text = ""
		log = []
		while n < limit:
			n += 1
			element = element.nextSibling
			_ = self.__safe_get_text(element)
			x = NCP(const, _)
			log += [(x, _)]
			if x > MIN_P:
				break
			text += "^" + _
		text = re.sub(r"\^+","^", text)
		try:
			assert n < limit
			return [_.strip() for _ in text.split("^") if _ != ""]
		except AssertionError:
			raise ValueError("«%s» is not found in limit %s, text = %s, log = %s" % (const, limit, text, log))

	def __collect_text_from(self, element, limit = 10):
		n = 0
		text = ""
		while n < limit:
			n += 1
			element = element.nextSibling
			try:
				text += re.sub(r"[\n\r\t]+", " ", element.get_text()).strip()
			except AttributeError:
				pass
		return text

	def __find_next_element(self, element, const, limit = 10):
		n = 0
		while n < limit:
			n += 1
			element = element.nextSibling
			if element.name == const:
				break
		try:
			assert n < limit
			return element
		except AssertionError:
			raise ValueError("«%s» is not found in limit %s" % (const, limit))

	def факультет(self, element):
		return {'факультет':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def кафедра(self, element):
		return {"кафедра":self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def проректор(self, element):
		element = self.__find_next_element(element, 'w:tbl')
		try:
			return {
				"проректор по учебной работе":
				re.sub(r"\s+", " ", re.sub(r"[\n\xa0_]", " ", element.get_text())).strip()
			}
		except AttributeError:
			pass
		return None

	def умкд(self, element):
		text = self.__collect_text_from(element)
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

	def профиль_программы_магистратуры(self, element):
		return {'профиль программы магистратуры':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def квалификация_выпускника(self, element):
		return {'квалификация выпускника':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def выпускающая_кафедра(self, element):
		return {'выпускающая кафедра':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def форма_обучения(self, element):
		return {'форма обучения':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def курс(self, element):
		return {'курс':self.__safe_get_text(element.parent.parent.find_all('w:tc')[1])}

	def семестр(self, element):
		return {'семестр(-ы)':self.__safe_get_text(element.parent.parent.find_all('w:tc')[3])}

	def трудоёмкость(self, element):
		element = self.__find_next_element(element, 'w:tbl')
		cells = [self.__safe_get_text(_) for _ in element.find_all('w:tc')]
		return {
			"трудоёмкость" : {
				cells[0]: [cells[1],cells[2]],
				cells[3]: [cells[4],cells[5]],
			}
		}

	def виды_контроля(self, element):
		element = self.__find_next_element(element, 'w:tbl')
		cells = [self.__safe_get_text(_) for _ in element.find_all('w:tc')]
		return {
			"виды контроля" : {
				cells[0]: cells[1],
				cells[2]: cells[3],
				cells[4]: cells[5],
				cells[6]: cells[7],
			}
		}

	def разработчик(self, element):
		rez = self.__find_end_of_text(element, "Рабочая программа рассмотрена и одобрена на заседании кафедры", 20)
		authors = []
		for author in rez:
			if re.match(r".*(\w\.\s?\w\.)[^.]*", author):
				authors += [re.sub(r"_", "", author)]

		return { "авторы" : authors }

	def утверждение_и_согласование(self, element):
		element = self.__find_next_element(element, 'w:tbl')
		кафедра, дата, протокол = [self.__safe_get_text(_) for _ in element.find_all('w:tc')][0:3]
		element = self.__find_next_element(element, 'w:tbl')
		вед_кафедра = [self.__safe_get_text(_) for _ in element.find_all('w:tc')][1]
		element = self.__find_next_element(element, 'w:tbl')
		element = self.__find_next_element(element, 'w:tbl')
		вып_кафедра = [self.__safe_get_text(_) for _ in element.find_all('w:tc')][1]

		return {
			"утверждение и согласование" :
			{
				"кафедра": кафедра,
				"дата": дата,
				"протокол №": протокол,
				"ведущая кафедра": вед_кафедра,
				"выпускающая кафедра": вып_кафедра
			}
		}

	def цель_дисциплины(self, element):
		rez = self.__find_end_of_text(element, "в процессе изучения данной дисциплины студент осваивает следующие компетенции")
		# print(rez)
		# exit(0)
		return {"цель дисциплины": str(rez)}

	def parse(self):
		self.soup = BS(self.docx.element.xml)
		with open('log', 'w') as f:
			f.write(self.soup.prettify())
			f.close()
		for p in self.soup.find_all('w:p'):
			t = self.__safe_get_text(p)
			if self.__is_not_set("факультет") and NC(t, "факультет") > MIN_W:
				self.content.update(self.факультет(p))
			if self.__is_not_set("кафедра") and NC(t, "кафедра") > MIN_W:
				self.content.update(self.кафедра(p))
			if self.__is_not_set("проректор по учебной работе") and NCP(t, "проректор по учебной работе") > MIN_P:
				self.content.update(self.проректор(p))
			if self.__is_not_set("учебно-методический комплекс дисциплины") and NCP(t, "учебно-методический комплекс дисциплины") > MIN_P:
				self.content.update(self.умкд(p))
			if self.__is_not_set("программа") and NC(t, "программа") > MIN_W:
				self.content.update(self.программа(p))
			if self.__is_not_set("направление подготовки") and NCP(t, "направление подготовки") > MIN_P:
				self.content.update(self.направление_подготовки(p))
			if self.__is_not_set("профиль программы магистратуры") and NCP(t, "профиль программы магистратуры") > MIN_P:
				self.content.update(self.профиль_программы_магистратуры(p))
			if self.__is_not_set("квалификация выпускника") and NCP(t, "квалификация выпускника") > MIN_P:
				self.content.update(self.квалификация_выпускника(p))
			if self.__is_not_set("выпускающая кафедра") and NCP(t, "выпускающая кафедра") > MIN_P:
				self.content.update(self.выпускающая_кафедра(p))
			if self.__is_not_set("форма обучения") and NCP(t, "форма обучения") > MIN_P:
				self.content.update(self.форма_обучения(p))
			if self.__is_not_set("курс") and NC(t, "курс:") > MIN_W:
				self.content.update(self.курс(p))
			if self.__is_not_set("семестр(-ы)") and NC(t, "семестр(-ы)") > MIN_W:
				self.content.update(self.семестр(p))
			if self.__is_not_set("трудоёмкость") and NC(t, "трудоёмкость") > MIN_W:
				self.content.update(self.трудоёмкость(p))
			if self.__is_not_set("виды контроля") and NCP(t, "виды контроля") > MIN_P:
				self.content.update(self.виды_контроля(p))
			if self.__is_not_set("разработчик(-и)") and NC(t, "разработчик(-и)") > MIN_W:
				self.content.update(self.разработчик(p))
			if self.__is_not_set("утверждение и согласование") and NCP(t, "рабочая программа рассмотрена и одобрена на заседании кафедры") > MIN_P:
				self.content.update(self.утверждение_и_согласование(p))
			# print(NCP(t, "Цель учебной дисциплины"), t)
			if self.__is_not_set("цель дисциплины") and NCP(t, "Цель учебной дисциплины") > MIN_P:
				self.content.update(self.цель_дисциплины(p))

		print(dumps(self.content, indent = 4, ensure_ascii = 0))

	def __init__(self, docpath = "", content = {}):
		self.ma = Mystem()
		try:
			open(docpath)
			self.docx = Document(docpath)
			self.docpath = docpath
			self.parse()
		except FileNotFoundError:
			self.docx = Document()
		self.content = content

def test():
	rpd = RPD('РПД_дисциплины_1.docx')
	del rpd
	rpd = RPD()


if __name__ == '__main__':
	test()
