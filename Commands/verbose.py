async def command(cmd):
	if (cmd.isModerator()):
		cmd.notifySuccess()
		boolean = cmd.evaluateBoolean(0)
		if (boolean == None):
			boolean = not cmd.bot.getSetting('verboseMessaging')
		if (boolean):
			cmd.log(f"Enabling verbose overrides; requested by {cmd.getFullUsername()}.", False, True)
			cmd.reply("Enabling verbose overrides.")
		else:
			cmd.log(f"Disabling verbose overrides; requested by {cmd.getFullUsername()}.", False, True)
			cmd.reply("Disabling verbose overrides.")
		cmd.bot.setSetting('verboseMessaging', boolean)
		

info = {
	'name': "Verbose Override",
	'arguments': [],
	'summary': "Enables verbose overrides for the bot.",
	'hidden': True
}

