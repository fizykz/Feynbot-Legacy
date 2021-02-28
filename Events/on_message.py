





async def __event(bot, message):
	#Parse message 
	#Find command module, (Might be overridden)
	#Execute module function
	#Check if bot/exception/excluded or permissions are missing.
	#Check if command (Server prefix/global prefix)
	#Pass message/bot to command module.
	print("!!!!")
	if (message.author.bot): #unless excluded.
		return

	guildData = None
	command = None
	if (message.content.startswith('<@!806400496905748571> ') or message.content.startswith('<@806400496905748571> ') or message.content.lower().startswith('@feynbot ')):
		command = re.match(r'^[\@\<\!\w]+\>?\s*([a-z]+)', message.content).group(1)
	else:
		guildData = dbUtils.getObjectByID(message.guild.id)

	if (command or message.content.lower().startswith(guildData['prefix'])):
		if (not command):
			command = message.content.lower()[len(guildData['prefix']):]
		commandModule = bot.getCommand(message, command)
		if (commandModule):
			bot.log("Found command: \'" + command + "\'")
			taskQueue = utils.TaskQueue()
			if (guildData):
				taskQueue.addTask(commandModule, (bot, message, taskQueue, guildData))
			else: 
				taskQueue.addTask(commandModule, (bot, message, taskQueue))
			await taskQueue()