class LoginError(ValueError):
	pass

class WrongPasswordError(LoginError):
	pass

class WrongUsernameError(LoginError):
	pass
