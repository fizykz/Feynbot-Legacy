#The name of the command file (removing .py, of course) is the original command.  
#I.e. `>commandTemplate` would run this file.

async def command(cmd):	#Can be asynchronous or not, is always passed a commandInstance object.  Please look at the documentation/code for that or examples for explanation.
	pass

info = {	#Dictionary of values.
	'name': "Restart",	#Name of the command (Doesn't need to match file name)
	'arguments': [],	#List of tuples.  First item is the argument name, followed by any necessary descriptions (optional).
	'aliases': ["TemplateCommand"],	#Aliases for the same command to be registered under  (Case insenstive, alphanumerical).
	'summary': "Restarts the bot.",	#Summary of the command itself.  Or a description.
	'hidden': True 	#Hidden to the help command and users.
}