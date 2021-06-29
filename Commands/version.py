import numpy

info = {
	'name': "Version",
	'arguments': [],
	'aliases': ['v'],
	'summary': "Gives the bot version & Discord.py version.",
	'hidden': True,
	'DMs': True,
	'DMsOnly': False
}

async def command(self):
	self.log(self.bot.discord.__version__)

