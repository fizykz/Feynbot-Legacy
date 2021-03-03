#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#
import datetime

async def command(cmd):
	if (cmd.isModerator()):
		cmd.reply(cmd.content)
		cmd.log(cmd.content, False, True)

info = {
	'name': "Debug",
	'summary': "Prints message content and sends an identical message.",
	'hidden': True
}