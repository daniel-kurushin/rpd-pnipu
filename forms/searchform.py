from bs4 import BeautifulSoup as BS
from json import load, dumps, dump
from lingv.util import nolatin, nodigit

class SearchForm:
	"""Форма поиска - основной экран системы"""
	def _safe_get_param(self, dic, key):
		return dic[key] if key in dic.keys() else None

	def __init__(self, get_post_params):
		keys = get_post_params.keys()
		self._user = self._safe_get_param(get_post_params,'login')
		self._query = self._safe_get_param(get_post_params,'query')
		self._is_auth = self._safe_get_param(get_post_params,'is_auth')

		self.template = 'static/rpd_main.html'

		subjectlist = load(open('database/subjects.json'))
		subjectindex = load(open('database/subject-index.json'))
		structure = load(open('database/structure.json'))

		self._join_(subjectlist, subjectindex, structure)

		self.soup = BS(open(self.template).read())

	def _join_(self, _subjectlist = {}, _subjectindex = {}, structure = {}):
		rez = {}
		for faculty in _subjectlist.keys():
			for specialisation in _subjectlist[faculty].keys():
				for subject in _subjectlist[faculty][specialisation].keys():
					_ = _subjectlist[faculty][specialisation][subject]
					_.update({"факультет":
						{
							"полное наименование"      : faculty,
							"сокращенное наименование" : structure[faculty]['сокращенное наименование']
						}
					})
					_.update({"специализация":specialisation})
					_.update({"индекс":_subjectindex[subject]})
					rez.update({
						subject:_
					})

		self.data = rez

	def _insert_data(self):
		def relsort(elem):
			try:
				key = elem[1]['rel']
			except KeyError:
				key = nolatin(nodigit(elem[0].strip().lower()))
			return key

		self.soup.find('input', 'search_text')['value'] = self._query
		self.soup.find('input', {'type':'hidden'})['value'] = self._user
		# from json import dumps
		# print(dumps(self.data, indent = 4, ensure_ascii = 0))
		# exit(0)
		to_insert = self.soup.find('subjectlist')
		n = 0

		sorted_data = sorted(
			self.data.items(),
			key = relsort,
			reverse = False if self._query else True
		)

		for subject, sbjdic in sorted_data:
			subject_tag = BS('<subject>\
								<name></name>\
								<faculty></faculty>\
								<department></department>\
								<speciality></speciality>\
								<hours></hours>\
								<rrr></rrr>\
							  </subject>').subject
			subject_tag.find('name'      ).insert(0,subject)
			subject_tag.find('faculty'   ).insert(0,sbjdic['факультет']['сокращенное наименование'])
			subject_tag.find('department').insert(0,sbjdic['кафедра'])
			subject_tag.find('speciality').insert(0,sbjdic['специализация'])
			subject_tag.find('hours'     ).insert(0,sbjdic['трудоемкость'])
			try:
				subject_tag.find('rrr'       ).insert(0,str(sbjdic['rel']))
			except KeyError:
				subject_tag.find('rrr'       ).insert(0,"-")

			to_insert.insert(0, subject_tag)

	def _do_query(self, data, q_words):
		dump([data, q_words], open('/tmp/55.json', 'w'), ensure_ascii = 0, indent = 4)
		rez = {}
		for subject in data.keys():
			rel = 1
			s_words = data[subject]['индекс']
			for q_word in q_words.keys():
				try:
					rel *= s_words[q_word] * q_words[q_word] * 1000
				except KeyError:
					rel *= 0.000000001
			rel = 0 if rel == 1 else 0 if rel < 1 else rel * 1000
			if rel > 0:
				try:
					data[subject].update({"rel":rel})
					rez.update({subject:data[subject]})
				except Exception as e:
					print(subject, rel)
		return rez

	def _process_query(self):
		import lingv.index as lingv
		q_words = lingv.index(str(self._query))
		rez = self._do_query(self.data, q_words)
		return rez


	def __str__(self):
		if self._query:
			self.data = self._process_query()
		self._insert_data()
		return self.soup.prettify()


if __name__ == '__main__':
	sf = SearchForm({})
	x = {"Интернет ресурсы и электронные словари в работе переводчика на первом иностранном языке": {
		"контроль": "Зач: 8",
		"специализация": "Перевод и переводоведение",
		"трудоемкость": "114,00",
		"индекс": {
			"вадимовна": 0.019230769230769232,
			"елена": 0.019230769230769232,
			"в": 0.0019230769230769232,
			"лингвистика": 0.019230769230769232,
			"интернет": 0.038461538461538464,
			"перевод": 0.019230769230769232,
			"ресурс": 0.038461538461538464,
			"на": 0.0019230769230769232,
			"язык": 0.038461538461538464,
			"словарь": 0.038461538461538464,
			"факультет": 0.0019230769230769232,
			"первый": 0.038461538461538464,
			"и": 0.0019230769230769232,
			"электронный": 0.038461538461538464,
			"переводчик": 0.038461538461538464,
			"переводоведение": 0.019230769230769232,
			"гуманитарный": 0.019230769230769232,
			"аликин": 0.019230769230769232,
			"иялп": 0.019230769230769232,
			"работа": 0.038461538461538464,
			"иностранный": 0.038461538461538464
		},
		"факультет": {
			"сокращенное наименование": "ГУМ",
			"полное наименование": "Гуманитарный факультет"
		},
		"кафедра": "ИЯЛП"
		}
	}
	y0 = {
		"перевод": 0.14285714285714285,
		"переводоведение": 0.14285714285714285,
		"и": 0.014285714285714285
	}
	y1 = {
		"интернет": 0.14285714285714285,
		"среда": 0.14285714285714285,
		"и": 0.014285714285714285
	}
	y2 = {
		"физика": 0.14285714285714285,
		"химия": 0.14285714285714285,
		"и": 0.014285714285714285
	}
	# sf._do_query(x, y0)
	# sf._do_query(x, y1)
	# sf._do_query(x, y2)
	print(dumps(sf._do_query(x, y0), indent=4, ensure_ascii = 0))
	print(dumps(sf._do_query(x, y1), indent=4, ensure_ascii = 0))
	print(dumps(sf._do_query(x, y2), indent=4, ensure_ascii = 0))
