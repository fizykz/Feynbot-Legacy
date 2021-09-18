#info = {
#	'name': "",
#	'aliases': [],
#	'arguments': [],
#	'summary': "",
#	'hidden': True,
#}
#
#async def command(interface):
#	pass
import datetime

info = {
	'name': "Ping",
	'aliases': ["p"],
	'summary': "Measures the average one-way latency for the bot."
}

async def command(interface):
	start = interface.message.created_at
	ourMessage = await interface.reply(str(interface.bot.getBotEmoji('loading')) + " Ping!")
	end = ourMessage.created_at
	total = ("{:,}").format(int((end - start) / datetime.timedelta(microseconds=1) / 1000 / 2)) 	#Microsends in between, divided by 1000 to milli, then divided by two & formats with commas.
	await ourMessage.edit(content = str(interface.bot.getBotEmoji('success')) + " Pong: " + total + " ms.")
	interface.log(f"Average ping measured to be {total} ms.", title = 'Ping!')
