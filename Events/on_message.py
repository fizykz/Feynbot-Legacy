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

	commandInterface = bot.commandInterface(bot, message)
	if (commandInterface.isValidCommand()):
		bot.log("Found command: \'" + commandInterface.commandName + "\'")
		try: 
			return await commandInterface()
		except Exception as error:
			commandInterface.notifyError(error)
