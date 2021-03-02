import re
import inspect

import utils

class Class:
	def __init__(self, bot, message):
		self.bot = bot
		self.message = message
		self.guild = message.guild or None
		self.guildData = None
		self.commandIdentifier = self.isCommand(message.content)
		self.valid = None
		self.error = None

		if (self.commandIdentifier):	#Check if this is a command as soon as we can to save memory/computation.
			self.commandModule = bot.getCommand(self.commandIdentifier, self.channel.id, self.guild.id, True)

		if (self.commandIdentifier and self.commandModule): #Only keep going if it's a command with a valid module.
			self.valid = True
			if (type(self.commandModule) != SyntaxError):	#Make sure this command module didn't error.
				self.error = False
				self.commandName = commandModule.name
				self.botClass = bot.getClass()
				self.user = message.author
				self.permissionLevel = bot.getPermissionLevel(self.user.id)
				self.userData = None 
				self.channel = message.channel
				self.command = commandModule.command
			else:
				self.error = True
		

	def isCommand(self, string):	#returns a tuple, first is the command name if found, second is guild data if it was called for convenience.
		string = string.lower()
		data = None
		prefix = self.bot.prefix

		command = utils.substringIfStartsWith(string, '<@!806400496905748571>') 
		command = command or utils.substringIfStartsWith(string, '<@806400496905748571>')
		command = command or utils.substringIfStartsWith(string, '@feynbot ')
		if (not self.guild):
			command = command or command or utils.substringIfStartsWith(string, prefix)
		if (command): #Short circuit attempt.  If it ends up not being any of these, it's not a command and we can save a datastore call.
			command = re.match(r'^ *([a-z]+)\s', command, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
			if (command):
				return command.group(1) #return our capture group
			else:
				return None #no command found.


		if (self.guild): #check if we're in a guild.
			data = self.getGuildData()
			prefix = data['prefix']	#Get the guild prefix.

		command = utils.substringIfStartsWith(string, prefix) 
		if (command): 
			command = re.match(r'^ *([a-z]+)\s', command, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
			if (command):
				return command.group(1), data #return our capture group with guildData (to reduce calls)
			else:
				return None #no command found.

	def isValid(self): #True if fine, False if error, None if nothing,
		return self.valid and not self.error

	def getFullUsername(self, withID = True):
		self.bot.stringifyUser(self.user, withID)

	def parseMessage(self):
		return []

	def isOwner(self):
		return self.permissionLevel >= self.bot.state['levels']['owner']

	def isAdmin(self, id, canBeSelf = False):
		return self.permissionLevel >= self.bot.state['levels']['admin']

	def isModerator(self, id, canBeSelf = False):
		return self.permissionLevel >= self.bot.state['levels']['moderator']

	def isUser(self, id, canBeSelf = False):
		return self.permissionLevel >= self.bot.state['levels']['user']

	def isBanned(self, id, canBeSelf = False):
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

	def runCommand(self, concurrently):
		if (inspect.iscoroutinefunction(self.command)):
			return self.bot.addTask(self.command(self))
		else:
			return self.command(self)

	def tryRunning(self):
		try:
			return self.runCommand(concurrently)
		except Exception as error:
			self.notifyError()
			raise error

	def notifyError(self, error):
		bot.addTask(message.add_reaction(bot.getFrequentEmoji('reportMe')))	
		bot.alert("An error was raised when executing " + commandIdentifier, True)	#Print the error and reject it.
		
