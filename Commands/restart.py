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
		await bot.addReaction(message, bot.getFrequentEmoji('accepted'))
		user = bot.stringifyUser(message.author)
		bot.alert(f"Restart ordered by {user}.", True)
		await bot.restart()
info = {
	'name': "Restart",
	'arguments': [],
	'summary': "Restarts the bot.",
	'hidden': True
}