#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#

async def command(bot, message, taskQueue, guildData=None):
	if (bot.isAdmin(message.author.id)):
		user = message.author.display_name + '#' + message.author.discriminator
		bot.alert(f"Restart ordered by {user} ({message.author.id})", True, True)
		await bot.restart()

help = {
	'arguments': [],
	'summary': "Restarts the bot."
}