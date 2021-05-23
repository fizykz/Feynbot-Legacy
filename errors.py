import languageModule


#TODO: Lang

class SafelockError(Exception):
	def __init__(self):
		super().__init__("Attempted to override the safelock setting.")		#"Attempted to override the safelock setting."
