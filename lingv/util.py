import re
def sokr(_str):
	return re.findall(r"(\w)\w+[ -](\w)\w+([ -](\w)\w+)?", _str)

if __name__ == '__main__':
	print(sokr('химико-технологический факультет'))
	print(sokr('электротехнический факультет'))
