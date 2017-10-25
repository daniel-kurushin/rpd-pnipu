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
		n = 0
		while n < 10:
			element = element.nextSibling
			n += 1
			if element.name == 'w:tbl':
				break
		cells = [self.__safe_get_text(_) for _ in element.find_all('w:tc')]
		try:
			assert n < 10
			return {
				"трудоёмкость" : {
					cells[0]: [cells[1],cells[2]],
					cells[3]: [cells[4],cells[5]],
				}
			}
		except IndexError:
			return {"трудоёмкость": self.__safe_get_text(element)}
		except AssertionError:
			return {"трудоёмкость": n}

	def виды_контроля(self, element):
		n = 0
		while n < 10:
			element = element.nextSibling
			n += 1
			if element.name == 'w:tbl':
				break
		cells = [self.__safe_get_text(_) for _ in element.find_all('w:tc')]
		try:
			assert n < 10
			return {
				"виды контроля" : {
					cells[0]: cells[1],
					cells[2]: cells[3],
					cells[4]: cells[5],
					cells[6]: cells[7],
				}
			}
		except IndexError:
			return {"виды контроля": self.__safe_get_text(element)}
		except AssertionError:
			return {"виды контроля": n}

	def разработчик(self, element):
		def get_sokr(author_str):
			return re.findall(r"(\w\.\s*\w\.)", author_str.split('_')[-1])[0]

		def get_surname(initials, author_str):
			rez = re.findall(r".*[ _](.*) (%s)(.*).*" % initials, author_str)[0]
			return rez[0] if rez[0] != "" else rez[2]

		def get_grade(author_str):
			try:
				rez = re.findall(r"([^.]{2,7}\.[^.]{2,7}\.[^.]{2,7})[, ]", author_str)[0]
			except IndexError:
				try:
					rez = re.findall(r"(\w\.\w\.\w\.)", author_str)[0]
				except IndexError:
					raise ValueError
			return rez.strip(',')

		def get_position(grade, author_str):
			# доц.,  к.т.н., доц. _________________ курушин
			rez = re.findall(r"(.+?)?,?(%s), ?(.+?)? " % grade, author_str)[0]
			return rez[0] if rez[0] != "" else rez[2]

		def filter_sokr(initials):
			rez = tuple([s.strip() for s in initials.split(".")[0:2]])
			return ("%s. %s." % rez).upper()

		def filter_surname(surname):
			return surname.strip().capitalize()

		def filter_grade(grade):
			return re.sub(r"\.", ". ", re.sub(r"[, ]", "", grade)).strip()

		def filter_position(position):
			return re.sub(r"[, ]", "", position)

		n = 0
		text = ""
		while n < 20:
			n += 1
			element = element.nextSibling
			_ = self.__safe_get_text(element)
			if NCP("Рабочая программа рассмотрена и одобрена на заседании кафедры", _) > MIN_P:
				break
			text += "^" + _
		text = re.sub(r"\^+","^", text)
		rez = [_.strip() for _ in text.split("^") if _ != ""]
		authors = []
		for author in rez:
			try:
				initials = get_sokr(author)
				surname = get_surname(initials, author)
				grade = get_grade(author)
				position = get_position(grade, author)
				initials = filter_sokr(initials)
				surname = filter_surname(surname)
				grade = filter_grade(grade)
				position = filter_position(position)
				authors += [
					{
						"ФИО": "%s %s" % (initials, surname),
						"Должность": position,
						"Степень": grade,
					}
				]
			except Exception as e:
				pass

		return { "авторы" : authors }
		
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
