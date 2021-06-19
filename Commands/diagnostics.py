#info = {
#	'name': "",
#	'aliases': [],
#	'arguments': [],	
#	'summary': "",
#	'hidden': True,
#}
#
#async def command(interface):
#	pass

info = {
	'name': "Diagnostics",
	'arguments': [],
	'summary': "Enables diagnostic overrides for the bot.",
	'hidden': True
}

async def command(interface):
	if (interface.isModerator()):
		boolean = interface.evaluateBoolean(0)
		if (len(interface.parsedArguments) == 0):
			interface.reply(f"Diagnostics are currently set to `{interface.bot.settings['overrideDiagnostics']}`")
			return 
		elif (boolean == None):
			interface.reply(f"Please check your first argument if you were attempting to set the override.\nDiagnostics are currently set to `{interface.bot.settings['overrideDiagnostics']}`")
			return 
		elif (boolean):
			interface.logLink(f"Enabling diagnostic overrides; requested by {interface.stringifyUser()}.", -1, True, True, color = 203, title = 'Settings')
			interface.reply("Enabling diagnostic overrides.")
			interface.notifySuccess()
		elif (boolean == False):
			interface.logLink(f"Disabling diagnostic overrides; requested by {interface.stringifyUser()}.", -1, True, True, color = 203, title = 'Settings')
			interface.reply("Disabling diagnostic overrides.")
			interface.notifySuccess()
		interface.bot.settings['overrideDiagnostics'] = boolean
		
		

