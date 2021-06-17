#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#
import datetime

async def command(interface):
	start = interface.message.created_at
	ourMessage = await interface.reply(interface.bot.getFrequentEmoji('loading') + " Pong!")
	end = ourMessage.created_at
	total = int((end - start) / datetime.timedelta(microseconds=1) / 1000 / 2) #Microsends in between, divided by 1000 to milli, then divided by two. 
	await ourMessage.edit(content = interface.bot.getFrequentEmoji('acceptedStatic') + " Pong: " + str(total) + " ms.")

info = {
	'name': "Ping",
	'aliases': ["p"],
	'summary': "Measures the average one-way latency for the bot."
}