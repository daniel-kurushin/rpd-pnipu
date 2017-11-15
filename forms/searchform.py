from bs4 import BeautifulSoup as BS
from json import load, dumps

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
				key = elem[0]
			return key

		self.soup.find('input', 'search_text')['value'] = self._query
		self.soup.find('input', {'type':'hidden'})['value'] = self._user
		# from json import dumps
		# print(dumps(self.data, indent = 4, ensure_ascii = 0))
		# exit(0)
		to_insert = self.soup.find('subjectlist')
		n = 0

		sorted_data = sorted(self.data.items(), key = relsort, reverse = False)

		for subject, sbjdic in sorted_data:
			if n < 40:
				n += 1
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

	def _process_query(self):
		import lingv.index as lingv
		q_words = lingv.index(str(self._query))
		rez = {}
		for subject in self.data.keys():
			rel = 1
			s_words = self.data[subject]['индекс']
			for q_word in q_words.keys():
				try:
					rel *= s_words[q_word] * q_words[q_word]
				except KeyError:
					pass
			rel = 0 if rel == 1 else rel * 1000
			if rel > 0:
				try:
					self.data[subject].update({"rel":rel})
					rez.update({subject:self.data[subject]})
				except Exception as e:
					print(subject, rel)
		return rez



	def __str__(self):
		if self._query:
			self.data = self._process_query()
		self._insert_data()
		return self.soup.prettify()
