async def command(cmd):
	if (cmd.isAdmin()):
		await cmd.bot.addReaction(message, cmd.bot.getFrequentEmoji('accepted'), concurrently = True)
		cmd.bot.alert(f"Restart ordered by {cmd.getFullUsername()}.", True)
		await cmd.bot.restart()

info = {
	'name': "Restart",
	'arguments': [],
	'summary': "Restarts the bot.",
	'hidden': True
}