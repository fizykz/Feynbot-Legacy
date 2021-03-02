async def command(cmd):
	if (cmd.isAdmin()):
		cmd.bot.addReaction(message, cmd.bot.getFrequentEmoji('accepted'))
		cmd.bot.alert(f"Reload ordered by {cmd.getFullUsername()}.", True)
		cmd.bot.reloadCommands()
		cmd.bot.reloadEvents()

info = {
	'arguments': [],
	'summary': "Reloads all commands.",
	'hidden': True
}