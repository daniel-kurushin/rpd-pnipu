from bs4 import BeautifulSoup as BS
from json import dump, dumps, load
import requests
import sys
import re

href = 'http://pstu.ru/activity/educational/fgosvpo/uchplans/'
try:
	_ = open("/tmp/in").read()
except FileNotFoundError:
	_ = requests.get(href).content
	open("/tmp/in", "wb").write(_)

soup = BS(_)

structure = {}

content = soup.find('div', 'content')
table = content.find('table')
n = 0
for tr in table('tr'):
	print(tr.text)
	n += 1
	# if re.match('\w{2,5}', tr.text):

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
