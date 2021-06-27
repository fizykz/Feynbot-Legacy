import numpy

async def command(interface):
	interface.log(interface.bot.discord.__version__)

info = {									
	'name': "Version",						
	'arguments': [],						
	'aliases': ['v'],							
	'summary': "Gives the bot version & Discord.py version.",	
	'hidden': True, 						
	'DMs': True,							
	'DMsOnly': False						
}

state = {}				

async def startup(bot):	
	pass 

async def init(bot):	
	pass 

async def command(self):
	interface.log(interface.bot.discord.__version__)

