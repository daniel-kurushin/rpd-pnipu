from json import load
# from lingv.index import index
from pymystem3 import Mystem
from rutermextract import TermExtractor as TE

def index(text, mystem = Mystem()):
	terms = TE()(text)
	idx = {}

	for term in terms:
		for rez in mystem.analyze(str(term)):
			try:
				idx.update({rez['analysis'][0]['lex']:(term.count / len(terms))})
			except:
				pass

	return idx

def index_subjects():
	mystem = Mystem()
	subjects = load(open('database/subjects.json'))
	structur = load(open('database/structure.json'))

	def find_department(short):
		rez = ('', '')
		for faculty in structur.keys():
			try:
				_ = structur[faculty]["кафедры"][short]
				rez = (_["наименование"], _["заведующий кафедрой"])
				break
			except KeyError:
				pass

		return rez

	rez = {}

	for faculty in subjects.keys():
		for specialisation in subjects[faculty].keys():
			for subject in subjects[faculty][specialisation].keys():
				try:
					short = subjects[faculty][specialisation][subject]['кафедра'].replace('и','')
					department, head = find_department(short)
					text = "%s %s %s %s %s %s" % (faculty, specialisation, subject, department, short, head)
					idx = index(text, mystem)
					rez.update({subject: idx})
				except Exception as e:
					print(e, faculty, specialisation, subject, subjects[faculty][specialisation][subject])
					raise e

subject_index = index_subjects()
import json
print(json.dumps(subject_index, indent = 4, ensure_ascii = 0))


# {
#     "Химико-технологический факультет": {
#         "Автоматизация химико-технологических процессов и производств": {
#             "Химия": {
#                 "контроль": "Зач: 2",
#                 "трудоемкость": "108,00",
#                 "кафедра": "ХБТ"
#             },
#             "Физика": {
#                 "контроль": "Экз: 1; ДифЗач: 2",
#                 "трудоемкость": "396,00",
#                 "кафедра": "ПФ"
#             },
#             "Организация и планирование автоматизированных производств": {
#                 "контроль": "Зач: 8",
#                 "трудоемкость": "108,00",
#                 "кафедра": "АТП"
#             },
#
# {
#     "Горно-нефтяной факультет": {
#         "href": "http://pstu.ru/title1/faculties/gnf/",
#         "декан": {
#             "фио": "Галкин Сергей Владиславович",
#             "ученая степень": "Доктор геолого-минералогических наук"
#         },
#         "кафедры": {
#             "ГНГ": {
#                 "href": "/title1/faculties/gnf/gng/?cid=30",
#                 "наименование": "Геология нефти и газа",
#                 "сотрудники": {
#                     "Расторгуев М.Н.": {
#                         "должность": "Ассистент",
#                         "фио": "Расторгуев Михаил Николаевич",
#                         "ученая степень": ""
#                     },
#                     "Кочнева О.Е.": {
#                         "должность": "Доцент",
#                         "фио": "Кочнева Ольга Евгеньевна",
#                         "ученая степень": "Кандидат геолого-минералогических наук"
#                     },
#                     "Галкин В.И.": {
#                         "должность": "Заведующий кафедрой",
#                         "фио": "Галкин Владислав Игнатьевич",
#                         "ученая степень": "Доктор геолого-минералогических наук"
#                     },
