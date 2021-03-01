def process(bot, message):
	return [message.channel.id, message.guild.id, message.author.id]


async def event(bot, message):
	#Parse message 
	#Find command module, (Might be overridden)
	#Execute module function
	#Check if bot/exception/excluded or permissions are missing.
	#Check if command (Server prefix/global prefix)
	#Pass message/bot to command module.
	if (message.author.bot): #unless excluded.
		return

	prefix = None
	data = None
	command = None
	if (message.content.startswith('<@!806400496905748571> ') or message.content.startswith('<@806400496905748571> ') or message.content.lower().startswith('@feynbot ')):
		command = re.match(r'^[\@\<\!\w]+\>?\s*([a-z]+)', message.content).group(1)
	else:
		if (message.guild):
			data = bot.getObjectByID(message.guild.id)
			if (not data):
				bot.setupServer(message.guild)
		else:

		prefix = data and data['prefix'] or '>'

	if (command or message.content.lower().startswith(prefix)):
		if (not command):
			command = message.content.lower()[len(prefix):]
		commandFunction = bot.getCommand(message, command)
		if (commandFunction):
			bot.log("Found command: \'" + command + "\'")
			taskQueue = bot.utils.TaskQueue()
			if (guildData):
				taskQueue.addTask(commandFunction, bot, message, guildData)
			else: 
				taskQueue.addTask(commandFunction, bot, message)
			await taskQueue()