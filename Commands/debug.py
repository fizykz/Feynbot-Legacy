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
	'name': "Copy-Cat",
	'summary': "Prints message content and sends an identical message.",
	'hidden': True
}

import datetime

async def command(interface):
	if (interface.isModerator()):
		interface.reply(interface.content)
		interface.logLink(interface.content, False, True)
		interface.notifySuccess()

