#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#

def command(bot, message, taskQueue, guildData=None):
	if (bot.isAdmin(message.author.id)):
		user = bot.utils.stringifyUser(message.author)
		bot.alert(f"Reload ordered by {user}.", True, True)
		bot.reloadCommands()
		bot.reloadEvents()

help = {
	'arguments': [],
	'summary': "Reloads all commands."
}