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
		word = ""
		try:
			word   = rez['analysis'][0]['lex']
		except IndexError as e:
			try:
				word = rez['text'].strip().lower()
			except KeyError:
				pass
		except KeyError:
			pass
		if word != "":
			weight = (1 / len(analysis))
			weight = weight / 10 if word in stop_words else weight
			idx.update({word:weight})

	return idx


if __name__ == '__main__':
	import sys
	import json
	print(
		json.dumps(
			index(sys.argv[1]),
			indent = 4,
			ensure_ascii = 0
		)
	)
# Химико-технологический факультет Автоматизация химико-технологических процессов и производств Методы и автоматизированные системы промышленного аналитического контроля
