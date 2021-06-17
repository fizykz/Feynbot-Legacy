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

info = {
	'name': "Debug",
	'summary': "Prints message content and sends an identical message.",
	'hidden': True
}

import datetime

async def command(interface):
	if (interface.isModerator()):
		interface.reply(interface.content)
		interface.log(interface.content, False, True)
		interface.notifySuccess()

