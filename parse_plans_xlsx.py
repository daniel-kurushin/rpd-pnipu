from bs4 import BeautifulSoup as BS
from json import dump, dumps, load
from xlrd import open_workbook
import requests
import sys
import re


def clean(_str):
	return re.sub(r'[*:\n\r\xa0\t]', '', _str)

def get_soup():
	href = 'http://pstu.ru/activity/educational/fgosvpo/uchplans/'
	try:
		_ = open("/tmp/in").read()
	except FileNotFoundError:
		_ = requests.get(href).content
		open("/tmp/in", "wb").write(_)

	return BS(_)

def get_xlsx(href):
	if not href.startswith('http://pstu.ru'):
		href = "http://pstu.ru" + href
	fname = "xls/%s" % href.split('/')[-1]
	try:
		_ = open(fname)
	except FileNotFoundError:
		try:
			_ = requests.get(href).content
			open(fname, "wb").write(_)
		except:
			print(href)
			exit(0)
	return fname

def get_work_plan(wb):
	params = []
	values = []
	ws = wb.sheet_by_index(0)
	for i in range(ws.nrows):
		for j in range(ws.ncols):
			if re.match(r"([^\n]+\n){6,}", ws.cell(i,j).value, re.MULTILINE):
				params = [ clean(_) for _ in ws.cell(i,j).value.split("\n") ]
				for k in range(j+1,ws.ncols):
					if re.match(r"([^\n]+\n){6,}", ws.cell(i,k).value, re.MULTILINE):
						values = [ clean(_) for _ in ws.cell(i,k).value.split("\n") ]
						break
				if values: break
		if params+values: break

	assert len(params) > 1 and len(values) > 1

	return params, values

def get_plan_structure(wb):
	n = 0
	rez = {}
	params, values = get_work_plan(wb)
	for param in params:
		rez.update({param:values[n]})
		n += 1

	return rez

def get_disc_structure(wb):

	def _collect_sheet(ws):
		rez = {}
		maxrow = 0
		for j in range(ws.ncols-1,0,-1):
			for i in range(min(ws.nrows, 16)):
				if ws.cell(i,j).value in params.keys():
					params.update({ws.cell(i,j).value:j})
					maxrow = i if i > maxrow else maxrow

		for subject, row in [ (ws.cell(i, params["Наименование дисциплины"]).value, i) for i in range(maxrow, ws.nrows) ]:
			if subject:
				subject_data = {}
				for param in set(params.keys()) - {"Наименование дисциплины"}:
					col = params[param]
					_ = ws.cell(row, col).value
					if _: subject_data.update({param:_})
				rez.update({subject:subject_data})

		return rez

	# Вид контроля по семестрам
	# Общая трудоемкость по видам учебной работы, АЧ
	rez = {}
	params = {
		"Кафедра":0,
		"Индекс дисциплины":0,
		"Наименование дисциплины":0,
		"Экзамен":0,
		"Диф. зачет":0,
		"Зачет":0,
		"Курсовой проект":0,
		"Курсовая работа":0,
		"Всего":0,
		"Аудиторные":0,
		"СРС":0,
		"Лекции":0,
		"Лабораторные":0,
		"Практические":0,
		"КСР":0,
		"Общая трудоемкость, ЗЕ":0,
		"Код компетенции":0
	}
	try:
		ws = wb.sheet_by_name("Дисциплины")
	except:
		ws = wb.sheet_by_name("План")

	rez.update(_collect_sheet(ws))
	ws = wb.sheet_by_name("Дисциплины по выбору")
	rez.update(_collect_sheet(ws))

	return rez

def make_flat(structure = {}):
	rez = {}
	for faculty in structure.keys():
		for plan in structure[faculty]:
			subject_data = {}
			for subject in plan["Учебный план"]["Дисциплины"].keys():
				rez.update({subject:1})
	return rez

def main():
	table = get_soup().find('div', 'content').find('table')

	faculty = None
	structure = {}
	headers = []

	for tr in table('tr'):
		text = clean(tr.text)
		if re.match('^\w{2,5}$', text):
			try:
				structure.update({faculty:faculty_data})
			except:
				pass
			faculty = text
			faculty_data = []
		else:
			if faculty and headers:
				n = 0
				item = {}
				for td in tr('td'):
					a = td.find('a')
					if a:
						item.update({headers[n]: a["href"]})
					else:
						item.update({headers[n]: clean(td.text)})
					n += 1
				faculty_data += [item]
			else:
				for td in tr('th'):
					headers += [clean(td.text)]
	structure.update({faculty:faculty_data})

	for faculty in structure.keys():
		for plan in structure[faculty]:
			wb = open_workbook(get_xlsx(plan["Учебный план"]))
			plan["Учебный план"] = get_plan_structure(wb)
			plan["Учебный план"].update({"Дисциплины":get_disc_structure(wb)})

	structure = make_flat(structure)

	print(dumps(structure, indent = 4, ensure_ascii = 0))

if __name__ == '__main__':
	main()
