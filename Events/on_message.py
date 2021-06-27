import re
import inspect

def process(bot, message):
	return [message.channel.id, message.guild and message.guild.id or 0, message.author.id]


async def event(bot, message):
	bot.log(f"on_message: {repr(message.content)}", 4)
	if (message.author.id == bot.user.id): 									#NEVER EVER respond to ourselves.  Huge security risk.
		return
	
	if (message.author.bot):											 	#Don't respond to other bots, (or potentially some)
		return

	commandInterface = bot.interface(bot, message)
	if (commandInterface.isValidCommand()):
		bot.log(f"Command `{repr(commandInterface.commandIdentifier)}` found.", 2, title = 'Command')
		await commandInterface.runCommand()
	elif (isinstance(message.channel, bot.discord.DMChannel)):
		commandInterface.reply("This was a DM!")
		#Get list of mutual servers.
		#see which ones are listening to DM info
		#check if there's a DM command specific to a server.
			#does it have a conflict?
			#if no pass & run.
			#otherwise prompt the user to choose one.
			
