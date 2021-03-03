import re
import inspect

import utils

class Class:
	def __init__(self, bot, message):
		self.bot = bot
		self.message = message
		self.guild = message.guild or None
		self.guildData = None
		self.channel = message.channel
		self.parsedString = utils.parseString(message.content)
		self.commandIdentifier = self.__prepareCommand__(message.content)
		self.valid = None
		self.error = None
		self.utils = bot.utils
		self.content = message.content

		if (self.commandIdentifier):	#Check if this is a command as soon as we can to save memory/computation.
			self.commandModule = bot.getCommand(self.commandIdentifier, self.channel.id, self.guild and self.guild.id, True)

			if (self.commandModule): #Only keep going if it's a command with a valid module.

				self.valid = True
				if (type(self.commandModule) != SyntaxError):	#Make sure this command module didn't error.
					try:
						self.error = False
						self.commandName = self.commandModule.info['name']
						self.botClass = bot.getClass()
						self.user = message.author
						self.permissionLevel = bot.getPermissionLevel(self.user.id)
						self.userData = None 
						self.command = self.commandModule.command
					except Exception as error:
						self.notifyError(error)
						raise error
				else:
					self.notifyError(self.commandModule)
					self.error = True
		

	def __prepareCommand__(self, string):	#returns a tuple, first is the command name if found, second is guild data if it was called for convenience.
		string = string.lower()
		data = None
		prefix = self.bot.prefix

		pattern = r'^ *([a-z]+)(?:\s|$)'

		#Possible Global Prefixes
		substring = utils.substringIfStartsWith(string, '<@!806400496905748571>') 
		substring = substring or utils.substringIfStartsWith(string, '<@806400496905748571>')
		substring = substring or utils.substringIfStartsWith(string, '@feynbot ')	
		if (not self.guild):	#Check if we need to check for the default prefix.
			substring = substring or substring or utils.substringIfStartsWith(string, prefix)	#After this, substring is either none, or the remaining string with a global prefix removed.

		if (substring): #Short circuit attempt.  If it ends up not being any of these, it's not a valid identifier (as it did indeed begin with a global prefix) and we can save a datastore call.
			substring = re.match(pattern, substring, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
			if (substring):
				matchStart = re.search(substring.group(1), string, flags = re.S).span()[0]	#Grab the match from the original string and get the starting position.
				if (matchStart - 1 < len(self.parsedString[0])):	#If this is true, our parsedString[0] contains both the prefix and the identifier.
					self.parsedArguments = self.parsedString[1:]
					self.prefix = self.parsedString[0][:matchStart]
				else:
					elf.parsedArguments = self.parsedString[2:]
					self.prefix = self.parsedString[0]
				return substring.group(1) #return our capture group
			else:
				return None #no identifier found.

		if (self.guild): #check if we're in a guild.
			data = self.getGuildData()
			prefix = data['prefix']	#Get the guild prefix.
			substring = utils.substringIfStartsWith(string, prefix) 

			if (substring): 
				substring = re.match(pattern, substring, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
				if (substring):
					matchStart = re.search(substring.group(1), string, flags = re.S).span()[0]	#Grab the match from the original string and get the starting position.
					if (matchStart - 1 < len(self.parsedString[0])):	#If this is true, our parsedString[0] contains both the prefix and the identifier.
						self.parsedArguments = self.parsedString[1:]
						self.prefix = self.parsedString[0]
					else:
						elf.parsedArguments = self.parsedString[2:]
						self.prefix = self.parsedString[0]
					return substring.group(1) #return our capture group with guildData (to reduce calls)
				else:
					return None #no identifier found.

	def isValid(self): #True if fine, False if error, None if nothing,
		return self.valid and not self.error

	def getArgumentLength(self):
		return len(self.parsedArguments)

	def reply(self, *args, **kwargs):
		return self.bot.replyToMessage(self.message, *args, **kwargs)

	def addTask(self, *args, **kwargs):
		return self.bot.addTask(*args, **kwargs)

	def sleep(self, *args, **kwargs):
		return self.bot.sleep(*args, **kwargs)

	def delayEdit(self, message, delay, *args, **kwargs):
		async def helper():
			await self.sleep(delay)
			return await message.edit(*args, **kwargs)
		return self.addTask(helper())

	def edit(self, message, *args, **kwargs):
		self.addTask(message.edit(*args, **kwargs))

	def evaluateBoolean(self, position):
		if (position < self.getArgumentLength()):
			return utils.resolveBooleanPrompt(self.parsedArguments[position])
		return None

	def evaluateInteger(self, position):
		if (position < self.getArgumentLength()):
			return int(self.parsedArguments[position])
		return None

	def evaluateNumber(self, position):
		if (position < self.getArgumentLength()):
			return num(self.parsedArguments[position])
		return None

	def getFullUsername(self, withID = True):
		return self.bot.stringifyUser(self.user, withID)

	def isOwner(self):
		return self.permissionLevel >= self.bot.state['levels']['owner']

	def isAdmin(self):
		return self.permissionLevel >= self.bot.state['levels']['admin']

	def isModerator(self):
		return self.permissionLevel >= self.bot.state['levels']['moderator']

	def isUser(self):
		return self.permissionLevel >= self.bot.state['levels']['user']

	def isBanned(self):
		return self.permissionLevel >= self.bot.state['levels']['banned']

	def getGuildData(self):
		if (self.guild and self.guildData):
			return self.guildData 
		if (self.guild):
			data = self.bot.getGuildData(self.guild.id)
			self.guildData = data 
			return data 
		return None 

	def getUserData(self):
		if (self.guild and self.guildData):
			return self.guildData 
		if (self.guild):
			data = self.bot.getGuildData(self.guild.id)
			self.guildData = data 
			return data 

	def runCommand(self):
		try:
			if (inspect.iscoroutinefunction(self.command)):
				return self.bot.addTask(self.command(self))
			else:
				return self.command(self)
		except Exception as error:
			self.notifyError(error)
	def __call__(self, *args):
		return self.runCommand()

	def notifySuccess(self):
		return self.bot.addReaction(self.message, self.bot.getFrequentEmoji('accepted'))

	def notifyFailure(self):
		return self.bot.addReaction(self.message, self.bot.getFrequentEmoji('denied'))

	def promptRepeat(self):
		return self.bot.addReaction(self.message, self.bot.getFrequentEmoji('repeat'))

	def log(self, *args, **kwargs):
		self.bot.log(*args, **kwargs)

	def alert(self, *args, **kwargs):
		self.bot.alert(*args, **kwargs)

	def notifyError(self, error):
		self.bot.addReaction(self.message, self.bot.getFrequentEmoji('reportMe'))	
		self.alert("An error was raised when executing " + self.commandIdentifier + ".py:\n" + str(error), True)	#Print the error and reject it.
		
