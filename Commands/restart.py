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
		user = bot.utils.stringifyUser(message.author)
		bot.alert(f"Restart ordered by {user}.", True, True)
		await bot.restart()

help = {
	'arguments': [],
	'summary': "Restarts the bot."
}