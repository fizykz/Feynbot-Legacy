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
		self.commandIdentifier = self.isCommand(message.content)
		self.valid = None
		self.error = None

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
						self.notifyError()
						raise error
				else:
					self.error = True
		

	def isCommand(self, string):	#returns a tuple, first is the command name if found, second is guild data if it was called for convenience.
		string = string.lower()
		data = None
		prefix = self.bot.prefix

		pattern = r'^ *([a-z]+)(?:\s|$)'

		command = utils.substringIfStartsWith(string, '<@!806400496905748571>') 
		command = command or utils.substringIfStartsWith(string, '<@806400496905748571>')
		command = command or utils.substringIfStartsWith(string, '@feynbot ')
		if (not self.guild):
			command = command or command or utils.substringIfStartsWith(string, prefix)
		if (command): #Short circuit attempt.  If it ends up not being any of these, it's not a command (as it did indeed begin with a global prefix) and we can save a datastore call.
			command = re.match(pattern, command, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
			if (command):
				return command.group(1) #return our capture group
			else:
				return None #no command found.

		if (self.guild): #check if we're in a guild.
			data = self.getGuildData()
			prefix = data['prefix']	#Get the guild prefix.
			command = utils.substringIfStartsWith(string, prefix) 
			if (command): 
				command = re.match(pattern, command, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
				if (command):
					return command.group(1) #return our capture group with guildData (to reduce calls)
				else:
					return None #no command found.

	def isValid(self): #True if fine, False if error, None if nothing,
		return self.valid and not self.error

	def getFullUsername(self, withID = True):
		return self.bot.stringifyUser(self.user, withID)

	def parseMessage(self):
		return []

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

	def runCommand(self, concurrently = True):
		if (inspect.iscoroutinefunction(self.command)):
			return self.bot.addTask(self.command(self))
		else:
			return self.command(self)

	def tryRunning(self, concurrently = True):
		try:
			return self.runCommand(concurrently)
		except Exception as error:
			self.notifyError()
			raise error

	def notifyAccepted(self):
		pass 

	def notifyDenied(self):
		pass

	def notifyError(self):
		self.bot.addTask(self.message.add_reaction(self.bot.getFrequentEmoji('reportMe')))	
		self.bot.alert("An error was raised when executing " + self.commandIdentifier, True)	#Print the error and reject it.
		
