#The name of the command file (removing .py, of course) is the original command.  
#I.e. `>commandTemplate` would run this file.

#File name is case sensitive and only works normally if it's all lowercase—this is intentional.
#You can make the command uppercase to only allow it to work with aliases alternatively.  

info = {									#Dictionary of values.
	'name': "example",						#Name of the command (Doesn't need to match file name)
	'arguments': [],						#List of tuples.  First item is the argument name, followed by any necessary descriptions (optional).
	'aliases': ["testCommand"],				#Aliases for the same command to be registered under  (Case insenstive, alphanumerical).
	'summary': "Just a random command!",	#Summary of the command itself.  Or a description.
	'hidden': True, 						#Hidden to the help command and users.
	'DMs': False,							#Allows the command to be used in DMs.
	'DMsOnly': False,						#Only allows the command to be used in DMs.
	'register': True,						#This can be left unset, but if set to False, this command will not be registered publicly.
}

state = {}									#Collection of state for this command.

async def startup(bot):		#Ran when the bot reloads the command for the first time on startup.
	pass 

async def init(bot):		#Ran when the bot reloads the command.
	pass 

async def command(self):	#Ran when the command is run.
	pass

