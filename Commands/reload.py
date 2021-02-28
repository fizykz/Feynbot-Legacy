#def __command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#

def __command(bot, message, taskQueue, guildData=None):
	if (bot.isAdmin(message.author.id)):
		user = bot.utils.stringifyUser(message.author)
		bot.alert(f"Command ordered by {user}.", True, True)
		bot.reloadCommands()

help = {
	'arguments': [],
	'summary': "Reloads all commands."
}