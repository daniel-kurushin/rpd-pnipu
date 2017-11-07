from rutermextract import TermExtractor as TE
from pymystem3 import Mystem

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
