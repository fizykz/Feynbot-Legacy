



info = {
	'name': "Verbose Override",
	'arguments': [],
	'summary': "Enables verbose overrides for the bot.",
	'hidden': True
}


async def command(interface):
	if (interface.isModerator()):
		interface.notifySuccess()
		boolean = interface.evaluateBoolean(0)
		if (boolean == None):
			boolean = not interface.bot.getSetting('verboseMessaging')
		if (boolean):
			interface.log(f"Enabling verbose overrides; requested by {interface.getFullUsername()}.", False, True)
			interface.reply("Enabling verbose overrides.")
		else:
			interface.log(f"Disabling verbose overrides; requested by {interface.getFullUsername()}.", False, True)
			interface.reply("Disabling verbose overrides.")
		interface.bot.setSetting('verboseMessaging', boolean)
		

