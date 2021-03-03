#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#
async def command(cmd):
	if (cmd.isAdmin()):
		await cmd.bot.addReaction(cmd.message, cmd.bot.getFrequentEmoji('accepted'))
		cmd.bot.alert(f"Bot closure ordered by {cmd.getFullUsername()}.", True)
		await cmd.bot.end()

info = {
	'name': "end",
	'aliases': ["close"],
	'arguments': [],
	'summary': "Ends the program."
}