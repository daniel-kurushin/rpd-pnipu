from bs4 import BeautifulSoup as BS
from json import dump
import requests
import sys

soup = BS(requests.get('http://pstu.ru/title1/student/plans/').content)
content = soup.find('div', 'content')

subject_list = {}

for fac in content('ul'):
	fac_name = fac.text.strip().strip('\n')
	faculty_list = {}
	spec = fac.nextSibling
	while spec.name != 'ul':
		if spec.name == 'ol':
			links = spec('a')
			for link in links:
				_ = BS(requests.get(link['href']).content)
				_content = _.find('div', 'content')
				subj = {}
				for s in _content('a'):
					try:
						td = s.parent
						dept = td.previousSibling.previousSibling.text
						hour = td.nextSibling.nextSibling.text
						cont = td.nextSibling.nextSibling.nextSibling.nextSibling.text
					except AttributeError:
						dept = ''
						hour = ''
						cont = ''
					subj.update({s.text:{'кафедра':dept, 'трудоемкость': hour, 'контроль': cont}})
				faculty_list.update({link.text:subj})
				print(".", end = "", file = sys.stderr, flush = 1)
		spec = spec.nextSibling
		if not spec: break
	subject_list.update({fac_name:faculty_list})

print(subject_list)
dump(subject_list, open('/tmp/1.json','w'),indent = 4, ensure_ascii = 0)
