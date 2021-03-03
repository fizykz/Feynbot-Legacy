import re
import inspect

def process(bot, message):
	return [message.channel.id, message.guild and message.guild.id or 0, message.author.id]


async def event(bot, message):
	bot.log("String representation:", repr(message.content))
	if (message.author.id == bot.user.id): #NEVER EVER respond to ourselves.  Huge security risk.
		return
	
	if (message.author.bot): #Don't respond to other bots, (or potentially some)
		return

	commandInstance = bot.commandInstance(bot, message)
	if (commandInstance.isValid()):
		bot.log("Found command: \'" + commandInstance.commandName + "\'")
		try: 
			return await commandInstance()
		except Exception as error:
			commandInstance.notifyError(error)
