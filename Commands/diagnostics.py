async def command(interface):
	if (interface.isModerator()):
		interface.notifySuccess()
		boolean = interface.evaluateBoolean(0)
		if (boolean == None):
			boolean = not interface.bot.getSetting('overrideDiagnostics')
		if (boolean):
			interface.log(f"Enabling diagnostic overrides; requested by {interface.getFullUsername()}.", False, True)
			interface.reply("Enabling diagnostic overrides.")
		else:
			interface.log(f"Disabling diagnostic overrides; requested by {interface.getFullUsername()}.", False, True)
			interface.reply("Disabling diagnostic overrides.")
		interface.bot.setSetting('overrideDiagnostics', boolean)
		

info = {
	'name': "Diagnostics",
	'arguments': [],
	'summary': "Enables diagnostic overrides for the bot.",
	'hidden': True
}