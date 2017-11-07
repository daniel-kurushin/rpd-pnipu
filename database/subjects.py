from json import load
# from lingv.index import index
from pymystem3 import Mystem

def index(text, mystem = Mystem()):
	stop_words = [
		"в",
		"введение",
		"глава",
		"ее",
		"и",
		"из",
		"институт",
		"кафедра",
		"на",
		"основа",
		"пример",
		"средство",
		"учение",
		"факультет",
	]
	idx = {}

	analysis = mystem.analyze(text)
	for rez in analysis:
		try:
			word   = rez['analysis'][0]['lex']
			weight = (1 / len(analysis))
			weight = weight / 10 if word in stop_words else weight
			idx.update({word:weight})
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
				rez = (_["наименование"], _["заведующий кафедрой"]["фио"])
				break
			except KeyError:
				pass

		return rez

	rez = {}

	for faculty in subjects.keys():
		for specialisation in subjects[faculty].keys():
			for subject in subjects[faculty][specialisation].keys():
				try:
					print(".", end="", flush=1)
					short = subjects[faculty][specialisation][subject]['кафедра'].replace('и','')
					department, head = find_department(short)
					text = "%s %s %s %s %s %s" % (faculty, specialisation, subject, department, short, head)
					idx = index(text, mystem)
					rez.update({subject: idx})
				except Exception as e:
					print(e, faculty, specialisation, subject, subjects[faculty][specialisation][subject])
					raise e

	return rez

subject_index = index_subjects()
import json
print(json.dumps(subject_index, indent = 4, ensure_ascii = 0))
json.dump(subject_index, open('/tmp/44.json', 'w'), indent = 4, ensure_ascii = 0)
