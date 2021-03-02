#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#

async def command(bot, message, guildData=None):
	if (bot.isAdmin(message.author.id)):
		bot.runConcurrently(message.add_reaction(bot.getFrequentEmoji('accepted')))
		user = bot.stringifyUser(message.author)
		bot.alert(f"Reload ordered by {user}.", True)
		bot.reloadCommands()
		bot.reloadEvents()

help = {
	'arguments': [],
	'summary': "Reloads all commands.",
	'hidden': True
}