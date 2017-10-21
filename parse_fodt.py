import sys
import re

from bs4 import BeautifulSoup as BS
from json import dumps

rpd = {}
s = BS(open(sys.argv[1]).read(), features="xml")

def факультет(element):
	return {'факультет':safe_get_text(element.parent.parent.find_all('table-cell')[1])}

def кафедра(element):
	return {'кафедра':safe_get_text(element.parent.parent.find_all('table-cell')[1])}

def проректор(element):
	n = 0
	while n < 10:
		n += 1
		element = element.nextSibling
		if element.name == 'table':
			break
	try:
		return {
			"проректор по учебной работе":
			re.sub(r"\s+", " ", re.sub(r"[\n\xa0_]", " ", element.get_text())).strip()
		}
	except AttributeError:
		pass
	return None

def умкд(element):
	n = 0
	while n < 10:
		n += 1
		element = element.nextSibling
		try:
			return {
				"учебно-методический комплекс дисциплины":
				re.findall(r'[«"](.*)[»"]', element.get_text())[0]
			}
		except AttributeError:
			pass
	return None


def safe_get_text(element):
	try:
		return element.get_text().strip().lower()
	except:
		return ""

for p in s.find_all('p'):
	t = safe_get_text(p)
	if t == "факультет":
		rpd.update(факультет(p))
	if t == "кафедра":
		rpd.update(кафедра(p))
	if t == "проректор по учебной работе":
		rpd.update(проректор(p))
	if t == "учебно-методический комплекс дисциплины":
		rpd.update(умкд(p))


print(dumps(rpd, indent = 4, ensure_ascii = 0))
