import re
import inspect

def process(self, message):
	return [message.channel.id, message.guild and message.guild.id or 0, message.author.id]


async def event(self, message):
	if (message.author.id == self.user.id): 								#NEVER EVER respond to ourselves.  Huge security risk.
		return
	
	if (message.author.bot):											 	#Don't respond to other selfs, (or potentially some)
		return

	try:
		commandInterface = self.interface(self, message, None)
		self.log(f"on_message: {repr(message.content)} | Valid: {commandInterface.isValidCommand()}", verbosity = 4)
		if (commandInterface.isValidCommand()):
			self.log(f"Command `{repr(commandInterface.commandIdentifier)}` found.", verbosity = 2, title = 'Command')
			await commandInterface.runCommand()
		elif (isinstance(message.channel, self.discord.DMChannel)):
			commandInterface.reply("This was a DM!")
			#Get list of mutual servers.
			#see which ones are listening to DM info
			#check if there's a DM command specific to a server.
				#does it have a conflict?
				#if no pass & run.
				#otherwise prompt the user to choose one.
	except Exception as error:
		if self.settings['reloadOnError']:
			self.log("Reloading libraries after an error.", verbosity = -1, critical = True, color = 12779530)
			self.reloadAll()
		raise error from None			
