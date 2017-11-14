from bs4 import BeautifulSoup as BS
from json import load

class SearchForm:
	"""Форма поиска - основной экран системы"""
	def _safe_get_param(self, dic, key):
		return dic[key] if key in dic.keys() else None

	def __init__(self, get_post_params):
		keys = get_post_params.keys()
		self._user = self._safe_get_param(get_post_params,'username')
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
		self.soup.find('input', 'search_text')['value'] = self._query
		from json import dumps
		print(dumps(self.data, indent = 4, ensure_ascii = 0))
		exit(0)
		to_insert = self.soup.find('subjectlist')
		n = 0
		for faculty in subjectlist.keys():
			for specialisation in subjectlist[faculty].keys():
				for subject in subjectlist[faculty][specialisation].keys():
					if n < 40:
						n += 1
						subject_tag = BS('<subject><name></name><direction></direction><department></department><control></control></subject>').subject
						subject_tag.find('name'      ).insert(0,subject)
						# subject_tag.find('direction' ).insert(0,subjectlist[faculty][specialisation][subject]["контроль"])
						subject_tag.find('department').insert(0,subjectlist[faculty][specialisation][subject]["контроль"])
						# subject_tag.find('control'   ).insert(0,subjectlist[faculty][specialisation][subject]["трудоемкость"])
						subject_tag.find('hours'     ).insert(0,subjectlist[faculty][specialisation][subject]["кафедра"])
					else:
						pass
					to_insert.insert(0, subject_tag)

	def _process_query(self):
		import lingv.index as lingv
		q_words = lingv.index(str(self._query))
		rez = {}
		for subject in self.subjectindex.keys():
			rel = 1
			s_words = self.subjectindex[subject]
			for q_word in q_words.keys():
				try:
					rel *= s_words[q_word] * q_words[q_word]
				except KeyError:
					pass
			rel = 0 if rel == 1 else rel
			if rel > 0:
				try:
					rez.update(self.subjectlist[subject])
				except Exception as e:
					print(subject, rel)
		return rez



	def __str__(self):
		if self._query:
			self._process_query()
		self._insert_data()
		return self.soup.prettify()
