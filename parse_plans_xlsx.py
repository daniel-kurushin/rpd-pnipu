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
	fname = "/tmp/%s" % href.split('/')[-1]
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

for faculty in structure.keys():
	for plan in structure[faculty]:
		plan_structure = {}
		wb = open_workbook(get_xlsx(plan["Учебный план"]))
		params, values = get_work_plan(wb)
		try:
			dis_sh = wb.sheet_by_name("Дисциплины")
		except:
			dis_sh = wb.sheet_by_name("План")
		vyb_sh = wb.sheet_by_name("Дисциплины по выбору")
		n = 0
		for param in params:
			try:
				plan_structure.update({param:values[n]})
			except Exception as e:
				print(
					param, values, plan, _, e
				)
				exit(0)
			n += 1

		plan["Учебный план"] = plan_structure


print(dumps(structure, indent = 4, ensure_ascii = 0))
exit(0)

for element in soup('li', 'active'):
	if element.text.strip() == 'Факультеты':
		break
element = element.nextSibling
while element.name != 'ul':
	element = element.nextSibling
for child in element.children:
	if child.name == 'li':
		try:
			href = "http://pstu.ru%s" % child.a['href']
			_ = BS(requests.get(href).content)
			content = _.find('div', 'content')
		except KeyError:
			content = soup.find('div', 'content')
		faculty_data = {}
		faculty_name = content.find('h1', itemprop='Name').text
		faculty_container = content.find('div', 'fac')
		dean_fio = faculty_container.find(itemprop="Fio").text
		dean_deg = faculty_container.find(itemprop="Degree").text
		structure.update({
			faculty_name:{
				"декан":{
					"фио":dean_fio,
					"ученая степень":dean_deg
				},
				"href":href,
			}
		})
dump(structure, open('/tmp/11.json', 'w'), indent = 4, ensure_ascii = 0)

for faculty in structure.keys():
	href = structure[faculty]['href']
	content = BS(requests.get(href).content).find('div', 'content')
	for element in content('h6'):
		if element.text.strip().lower() == 'кафедры факультета':
			break
	while element.name != 'ul':
		element = element.nextSibling
	depts = element('a')
	кафедры = {}
	for dept in depts:
		try:
			dept_name, dept_shrt = re.findall(r'.+афедра (.+) \((.+)\)',dept.text)[0]
		except IndexError:
			print(dept)
		dept_href = dept['href']
		кафедры.update({
			dept_shrt:{
				"наименование": dept_name,
				"href": dept_href
			}
		})

	structure[faculty].update({"кафедры":кафедры})

dump(structure, open('/tmp/22.json', 'w'), indent = 4, ensure_ascii = 0)
# structure = load(open('/tmp/22.json'))
for faculty in structure.keys():
	for dept in structure[faculty]["кафедры"].keys():
		try:
			href = "http://pstu.ru%s" % structure[faculty]["кафедры"][dept]['href']
			content = BS(requests.get(href).content).find('div', 'content')

			head_fio = content.find(itemprop = "Fio").text
			head_deg = content.find(itemprop = "Degree").text

			structure[faculty]["кафедры"][dept].update({
				"заведующий кафедрой": {
					"фио":head_fio,
					"ученая степень":head_deg
				}
			})

			for link in content('a'):
				if link.text.strip(" \n").lower() == "сотрудники кафедры":
					href = "http://pstu.ru%s" % link['href']
					break
			content = BS(requests.get(href).content).find('div', 'content')
			сотрудники = {}
			for person in content('a'):
				person_fio = person.text.strip(" \n")
				try:
					person_short = "%s %s.%s." % re.findall("(\w+)\s(\w)\w+\s(\w)\w+", person_fio)[0]
				except IndexError:
					print (href, person_fio)
				person_pos = person.parent.text.split(person_fio)[1].strip(" ,")
				try:
					person_deg, person_pos = [_.strip() for _ in person_pos.split(",")]
				except ValueError:
					person_deg = ""
				сотрудники.update({
					person_short: {
						"фио":person_fio,
						"ученая степень":person_deg,
						"должность":person_pos,
					}
				})
			structure[faculty]["кафедры"][dept].update({
				"сотрудники": сотрудники
			})
		except KeyError:
			pass


# print(dumps(structure, indent = 4, ensure_ascii = 0))
dump(structure, open('/tmp/33.json', 'w'), indent = 4, ensure_ascii = 0)
		# for dept_container in faculty_container('h6'):
		# 	if dept_container.text == 'Кафедры факультета':
		# 		break
		# while dept_container.name != 'ul':
		# 	dept_container = dept_container.nextSibling
		#
		# for department in dept_container('li'):
		# 	department_name = department.text
		# 	href = "http://pstu.ru/%s" % department.a['href']
