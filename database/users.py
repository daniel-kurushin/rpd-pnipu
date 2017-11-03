users = {
	"преподаватель" : {
		"hash": "478f8397fe60993a02db85d5a0cbfcd17068f234e072a43b0f27dd9a",
		"ФИО": "Курушин"
	}
}

def calc_hash(_str = ""):
	import hashlib
	return hashlib.sha224(_str.encode('utf-8')).hexdigest()
