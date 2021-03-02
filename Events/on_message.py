import re

def process(bot, message):
	return [message.channel.id, message.guild and message.guild.id or 0, message.author.id]


async def event(bot, message):
	#Parse message 
	#Find command module, (Might be overridden)
	#Execute module function
	#Check if bot/exception/excluded or permissions are missing.
	#Check if command (Server prefix/global prefix)
	#Pass message/bot to command module.
	print("String representation:", repr(message.content))
	if (message.author.id == bot.user.id): #NEVER EVER respond to ourselves.  Huge security risk.
		return
	if (message.author.bot): #unless excluded.
		return

	prefix = None
	data = None
	command = None
	if (message.content.startswith('<@!806400496905748571>') or message.content.startswith('<@806400496905748571>') or message.content.lower().startswith('@feynbot')):
		command = re.search(r'^[\@\<\!\w]+\>?\s*([a-z]+)', message.content, flags=re.S)
		if command:
			command = command.group(1)
		else:
			return
		command = re.sub(r'\n', r' ', command, flags=re.S)
		command = re.sub(r'^(\w+)\W+.*$', r'\1', command, flags=re.S)
	else:
		if (message.guild):
			data = bot.getObjectByID(message.guild.id)
			if (not data):
				bot.setupServer(message.guild)
			prefix = data and data['prefix'] or '>'
		else:
			prefix = '>'

	if (command or message.content.lower().startswith(prefix)):
		if (not command):
			command = message.content.lower()[len(prefix):]
			command = re.sub(r'\n', r' ', command, flags=re.S)
			command = re.sub(r'^(\w+)\W*.*$', r'\1', command, flags=re.S)
		commandFunction = bot.getCommand(message, command) 
		if (commandFunction):
			bot.log("Found command: \'" + command + "\'")
			taskQueue = bot.utils.TaskQueue()
			if (data):
				taskQueue.addTask(commandFunction, bot, message, data)
			else: 
				taskQueue.addTask(commandFunction, bot, message)
			await taskQueue()			try:
			try:
				if (inspect.iscoroutinefunction(commandFunction)):
					return await commandFunction(bot, message, data)
				else:
					return commandFunction(bot, message, data)
			except Exception as error:
				bot.addTask(message.add_reaction(bot.getFrequentEmoji('reportMe')))	
				bot.alert("An error was raised when executing " + commandName, True, error)	#Print the error and reject it.
				raise error
