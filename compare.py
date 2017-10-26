from nltk.tokenize import WordPunctTokenizer as WPT

MIN_P = 0.55
MIN_W = 0.62
PUNKT = set(['.', ',', ':', '!', '?'])
DIGITS = set([str(i) for i in range(10)])

def ngramm_compare_phrase(P1, P2):
	word_tokenizer = WPT()

	words1 = list(set(word_tokenizer.tokenize(P1)) - PUNKT - DIGITS)
	words2 = list(set(word_tokenizer.tokenize(P2)) - PUNKT - DIGITS)

	P = 1.0
	for i in range(max(len(words1),len(words2))):
		p = {-1:1, 0:1, 1:1}
		for j in p.keys():
			try:
				p[j] *= ngramm_compare(words1[i], words2[i+j])
			except IndexError:
				p[j] = 0
		P *= max(p.values())

	return P

def ngramm_compare(S1,S2):
	S1 = S1.replace(" ", "")
	S2 = S2.replace(" ", "")
	ngrams = [S1[i:i+3] for i in range(len(S1))]
	count = 0
	for ngram in ngrams:
		count += S2.count(ngram)

	return count/max(len(S1), len(S2))
