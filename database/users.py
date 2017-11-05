from exceptions import WrongUsernameError
import urllib

users = {
	"Курушин" : {
		"hash": "4fe0f2dd072ac82c99d16bdab240a1075d7d0960c5a491ab5a23e9b7",
		"ФИО": "Курушин Даниил Сергеевич",
		"степень": "кандидат технических наук",
		"должность": "доцент",
		"штатный": "да",
		"место работы": "кафедра ИТАС"
	},
	"Файзрахманов" : {
		"hash": "478f8397fe60993a02db85d5a0cbfcd17068f234e072a43b0f27dd9a",
		"ФИО": "Файзрахманов Рустам Абубакирович",
		"степень": "доктор экономических наук",
		"должность": "Заведующий кафедрой",
		"штатный": "да",
		"место работы": "кафедра ИТАС",
		"ученое звание": "Профессор",
	},
	"Петренко" : {
		"hash": "478f8397fe60993a02db85d5a0cbfcd17068f234e072a43b0f27dd9a",
		"ФИО": "Петренко Александр Анатольевич",
		"должность": "доцент",
		"степень": "кандидат технических наук",
		"штатный": "да",
		"место работы": "кафедра ИТАС"
	}
}

def calc_hash(_str = ""):
	import hashlib
	return hashlib.sha224(_str.encode('utf-8')).hexdigest()

def set_auth_cookies(_user):
	from random import randint
	_auth = calc_hash(str(randint(1000000, 100000000000)))
	cookies = [
		"session=%s" % _auth,
		"username=%s" % urllib.parse.quote_plus(_user),
	]
	try:
		users[_user].update({'auth':_auth})
		return cookies
	except KeyError:
		raise WrongUsernameError

def check_auth_cookies(_cookies):
	for cookie in cookies:
		pass
	try:
		return users[_user]['auth'] == _cookies
	except KeyError:
		raise WrongUsernameError

def del_auth_cookies(_user, _cookies):
	try:
		del users[_user]['auth']
	except KeyError:
		raise WrongUsernameError
