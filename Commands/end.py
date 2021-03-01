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
		await message.add_reaction(bot.getFrequentEmoji('accepted'))
		user = bot.stringifyUser(message.author)
		bot.alert(f"Bot closure ordered by {user}.", True)
		await bot.end()

help = {
	'arguments': [],
	'summary': "Restarts the bot."
}