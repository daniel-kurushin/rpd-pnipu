import sys

from rutermextract import TermExtractor as TE
from bs4 import BeautifulSoup as BS
from pymystem3 import Mystem
from json import dumps

Q = ['Кафедра информационных технологий',
'Файзрахманов',
'Проектирование информационных систем',
'Проектирование сублимационных систем',
'минимальный наука']

m = Mystem()

def index(text):
	terms = TE()(text)
	idx = {}

	for term in terms:
		for rez in m.analyze(str(term)):
			try:
				idx.update({rez['analysis'][0]['lex']:(term.count / len(terms))})
			except:
				pass

	return idx

def match(query, idx):
	r = 0.0
	n = 0
	for rez in m.analyze(str(query)):
		n += 1
		try:
			r += idx[rez['analysis'][0]['lex']]
		except:
			pass
	return r / n


if __name__ == '__main__':
	idx = index(BS(open(sys.argv[1]).read(), features="xml").get_text())
	print(dumps(idx, indent = 4, ensure_ascii = 0))

	for q in Q:
		print(q, match(q, idx))
