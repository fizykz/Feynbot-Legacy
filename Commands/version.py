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
#

import numpy

info = {
	'name': "Version",
	'arguments': [],
	'summary': "Gives the bot version & Discord.py version.",
	'hidden': False
}

async def command(interface):
	interface.log(interface.bot.discord.__version__)