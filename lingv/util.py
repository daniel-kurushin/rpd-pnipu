import re
NO_LATIN_TABLE = {}
NO_DIGIT_TABLE = {}

for keys, value in zip(list('abcdefghijklmnopqrstuvwxyz'), list('абцдефгхийклмноркрстюввхыз')):
	NO_LATIN_TABLE.update(dict.fromkeys(map(ord, keys), value))

for keys, value in zip(list('1234567890'), ["од", "дв", "тр", "че", "пя", "ше", "се", "во", "де", "но"]):
	NO_DIGIT_TABLE.update(dict.fromkeys(map(ord, keys), value))

def sokr(_str):
	return re.findall(r"(\w)\w+[ -](\w)\w+([ -](\w)\w+)?", _str)

def nodigit(_str):
	return _str.translate(NO_DIGIT_TABLE)

def nolatin(_str):
	return _str.translate(NO_LATIN_TABLE)

if __name__ == '__main__':
	print(nolatin("abcdefghijklmnopqrstuvwxyz-технологии"))
	print(nodigit("3D-технологии"))
	print(nostopwords(" теория организации отраслевых рынков "))
