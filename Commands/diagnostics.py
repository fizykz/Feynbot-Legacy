async def command(cmd):
	if (cmd.isModerator()):
		cmd.notifySuccess()
		boolean = cmd.evaluateBoolean(0)
		if (boolean == None):
			boolean = not cmd.bot.getSetting('overrideDiagnostics')
		if (boolean):
			cmd.log(f"Enabling diagnostic overrides; requested by {cmd.getFullUsername()}.", False, True)
			cmd.reply("Enabling diagnostic overrides.")
		else:
			cmd.log(f"Disabling diagnostic overrides; requested by {cmd.getFullUsername()}.", False, True)
			cmd.reply("Disabling diagnostic overrides.")
		cmd.bot.setSetting('overrideDiagnostics', boolean)
		

info = {
	'name': "Diagnostics",
	'arguments': [],
	'summary': "Enables diagnostic overrides for the bot.",
	'hidden': True
}