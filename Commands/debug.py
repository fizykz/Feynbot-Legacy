#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#
import datetime

async def command(bot, message, guildData=None):
	if (bot.isAdmin(message.author.id)):
		ourMessage = await message.channel.send(message.content) 
		bot.log(message.content, False, False)

help = {
	'name': "Debug",
	'summary': "Prints message content and sends an identical message.",
	'hidden': True
}