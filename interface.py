import re
import inspect
import discord
import random
import asyncio

import utils


class Interface:
	def __init__(self, bot, object, caller):
		self.bot = bot 
		self.utils = utils
		self.caller = caller
		if isinstance(object, discord.Message):
			self.message = object 
			self.user = self.message.author
			self.guild = self.message.guild or None 
			self.channel = self.message.channel
			self.parsedString = self.message.content.split()
			self.commandIdentifier = self.__prepareCommand__(self.message.content) 
			self.content = self.message.content
			self.url = self.message.to_reference().jump_url
			if self.guild:
				self.us = self.guild.get_member(self.bot.user.id)
			if (self.commandIdentifier):	#Check if this is a command as soon as we can to save memory/computation.
				self.commandModule = bot.getCommand(self.commandIdentifier, [self.user.id, self.channel.id, self.guild and self.guild.id]) or None
				if (self.commandModule): #Only keep going if it's a command with a valid module.
					if not (isinstance(self.commandModule, BaseException)):	#Make sure this command module didn't error.
						self.command = self.commandModule.command
					else:
						self.notifyError()
						raise self.commandModule from None 

		elif isinstance(object, discord.TextChannel): 
			self.channel = object
			self.guild = self.channel.guild or None 
		elif isinstance(object, discord.Guild):
			self.guild = object
		elif isinstance(object, discord.abc.User):
			self.user = object 
			self.guild = self.user.guild or None 

	############################
	### Bot Override Methods ###
	############################
	def getBotEmoji(self, *args, **kwargs):
		return self.bot.getBotEmoji(*args, **kwargs)
	def addTask(self, *args, **kwargs):
		return self.bot.addTask(*args, **kwargs)
	def sleep(self, *args, **kwargs):
		return self.bot.sleep(*args, **kwargs)
	def log(self, *args, logLink = True, **kwargs):
		return self.bot.log(*args, url = self.message.to_reference().jump_url if logLink else None, **kwargs)
	def stringifyUser(self, user = None, withID = True):
		if not user:
			user = self.user
		return self.bot.stringifyUser(user, withID)
	########################
	### Command Handling ###
	########################
	def __prepareCommand__(self, string):	#Returns command name.
		string = string.lower()
		data = None
		prefix = self.bot.settings['prefix']

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
					self.parsedArguments = self.parsedString[2:]
					self.prefix = self.parsedString[0]
				return substring.group(1) #return our capture group
			else:
				return None #no identifier found.

		if (self.guild): #check if we're in a guild.
			data = self.getGuildData()
			prefix = data['prefix'] or self.bot.settings['prefix']	#Get the guild prefix.
			substring = utils.substringIfStartsWith(string, prefix) 

			if (substring): 
				substring = re.match(pattern, substring, flags = re.S)	#grab the first alphabetical "word."  Needs to have only spaces before it and any whitespace after.
				if (substring):
					matchStart = re.search(substring.group(1), string, flags = re.S).span()[0]	#Grab the match from the original string and get the starting position.
					if (matchStart - 1 < len(self.parsedString[0])):	#If this is true, our parsedString[0] contains both the prefix and the identifier.
						self.parsedArguments = self.parsedString[1:]
						self.prefix = self.parsedString[0]
					else:
						self.parsedArguments = self.parsedString[2:]
						self.prefix = self.parsedString[0]
					return substring.group(1) #return our capture group with guildData (to reduce calls)
				else:
					return None #no identifier found.
	def isValidCommand(self): #True if fine, False if error, None if nothing,
		if hasattr(self, 'command'):
			return True 
		elif hasattr(self, 'commandModule'):
			return False
		return None 
	def getArgumentLength(self):
		return len(self.parsedArguments)
	def getPartLength(self):
		return len(self.parsedString)
	def getArgument(self, position = 0):
		if len(self.parsedArguments) > position:
			return self.parsedArguments[position]
		return None 
	def getPart(self, position = 0):
		if len(self.parsedString) > position:
			return self.parsedString[position]
		return None 
	def convertBreaks(self): 
		pass #converts , ; : etc into argument breaks.
	def evaluatePosition(self, position):
		pass #return the value & type
	def evaluateBoolean(self, position):
		if (position < self.getArgumentLength()):
			return utils.resolveBooleanPrompt(self.parsedArguments[position])
			try: 
				return utils.resolveBooleanPrompt(self.parsedArguments[position])
			except ValueError as error:
				return error
		return None
	def evaluateInteger(self, position):
		if (position < self.getArgumentLength()):
			try: 
				return int(self.parsedArguments[position])
			except ValueError as error:
				return error
		return None
	def evaluateNumber(self, position):
		if (position < self.getArgumentLength()):
			try: 
				return num(self.parsedArguments[position])
			except ValueError as error:
				return error
		return None
	async def runCommand(self):
		try:
			if (inspect.iscoroutinefunction(self.command)):
				return (await self.addTask(self.command(self)))
			else:
				return self.command(self)
		except Exception as error:
			self.notifyError()
			if self.bot.settings['reloadOnError']:
				self.log("Reloading libraries after an error.", -1, True, color = 12779530)
				self.bot.reloadAll()
			raise error from None
	def isOwner(self, ID = None, canBeSelf = False):
		return self.bot.isOwner(ID or self.user.id, canBeSelf)
	def isAdmin(self, ID = None, canBeSelf = False):
		return self.bot.isAdmin(ID or self.user.id, canBeSelf)
	def isModerator(self, ID = None, canBeSelf = False):
		return self.bot.isModerator(ID or self.user.id, canBeSelf)
	def isBanned(self, ID = None):
		return self.bot.isBanned(ID or self.user.id)
	def isDMs(self):
		return isinstance(self.channel, self.bot.discord.DMChannel)
	#####################################
	### Messaging, Reactions, & Other ###
	#####################################
	def addReactionTo(self, message, emoji):	#have an ID check
		return self.bot.addReactionTo(message, emoji)
	def removeReactionTo(self, message, emoji):
		return self.bot.removeReactionTo(message, emoji)
	def reactWith(self, emoji, message = None):
		return self.addReactionTo(message or self.message, emoji)
	def unreactWith(self, emoji, message = None, user = None):
		return self.bot.removeReactionTo(message or self.message, emoji, user or self.bot.user)
	def unreactUserWith(self, emoji, message = None, user = None):
		return self.bot.removeReactionTo(message or self.message, emoji, user or self.user)
	def notifySuccess(self, message = None):
		return self.addReactionTo(message or self.message, self.getBotEmoji('success'))
	def notifyFailure(self, message = None):
		return self.addReactionTo(message or self.message, self.getBotEmoji('failure'))
	def promptRepeat(self, message = None):
		return self.addReactionTo(message or self.message, self.getBotEmoji('repeat'))
	def notifyError(self, message = None):
		return self.addReactionTo(message or self.message, self.getBotEmoji('bug'))
	def deleteMessage(self, message, *args, delay = None, **kwargs):
		return self.bot.deleteMessage(message, *args, delay = delay, **kwargs)
	def delete(self, *args, delay = None, **kwargs):
		return self.deleteMessage(self.message, *args, delay = delay, **kwargs)
	def giveUserRoles(self, user, *roles, audit = None, **kwargs):
		return self.bot.giveRoles(user, roles *args, audit = audit, **kwargs)
	def giveRoles(self, *roles, audit = None, user = None, **kwargs):
		return self.bot.giveRoles(user or self.user, *roles, audit = audit, **kwargs)
	def replyTo(self, message, content, *args, ping = False, **kwargs):
		return self.bot.replyTo(message, content, *args, ping = ping, **kwargs)
	def reply(self, content, *args, ping = False, **kwargs):
		return self.replyTo(self.message, content, *args, ping = ping, **kwargs)
	def replyInvalid(self, content, message = None, *args, ping = True, flavorText = None, **kwargs):
		flavorText = flavorText or random.choice([
			"I'm sorry, I don't seem to understand.",
			"Something seems to be wrong here... but I can't quite put my digits on it...",
			"Uh-oh spaghettios.",
			"Hmmm, this doesn't seem to be right.",
			"I think we should've taken left back there instead.",
			"What if we tried...",
			"#&%@!",
			"01001111 01101000 00100000 01101110 01101111 00100001",
			"Oh no not again!",
			"NOT THE BEES!",
			"The code was a lie.",
		])
		self.replyTo(message or self.message, f"{flavorText}\n{content}", *args, ping = ping, **kwargs)
	def replyTimedOut(self, content, message = None, *args, ping = True, **kwargs):
		flavorText = random.choice([
			"Tick-tock!",
			"Tiktok!",
			"Any day now...",
			"Maybe next time.",
			"3fast5u",
			"Go to timeout!  Oh wait... I timed out.",
		])
		self.replyTo(message or self.message, f"{flavorText}\n{content}", *args, ping = ping, **kwargs)
	async def prompt(self, timeOut = 30, checkFunction = None, userID = None, DMs = False, sameChannel = True, cannotBeCommand = True):
		userID = self.user.id if userID == None else userID
		promptInterface = None
		def qualifies(message):
			nonlocal promptInterface
			if (sameChannel and message.channel == self.channel) and (DMs and not hasattr(message.channel, 'guild')):
				return False 
			if userID == message.author.id:	
				if sameChannel and message.channel == self.channel:
					promptInterface = Interface(self.bot, message, self)
				elif DMs and hasattr(message.channel, 'recipient'):
					promptInterface = Interface(self.bot, message, self)
				elif not sameChannel:
					promptInterface = Interface(self.bot, message, self)
			else:
				try:
					iter(userID)
					for ID in userID:
						if message.author.id == ID:
							if sameChannel and message.channel == self.channel:
								promptInterface = Interface(self.bot, message, self)
							elif DMs and hasattr(message.channel, 'recipient') and message.channel.recipient.id == ID:
								promptInterface = Interface(self.bot, message, self)
							elif not sameChannel:
								promptInterface = Interface(self.bot, message, self)
				except TypeError:
					pass
			if promptInterface and not (cannotBeCommand and promptInterface.isValidCommand()):
				if checkFunction and checkFunction(promptInterface):
					return True  
				elif checkFunction == None:
					return True 
			return False 
		try:
			message = await self.bot.wait_for('message', check = qualifies, timeout = timeOut)
		except asyncio.TimeoutError:
			return False
		else: 
			return promptInterface

	###############################
	### Datastore & Permissions ###
	###############################
	def getPermissions(self):
		if hasattr(self, 'permissions'):
			return self.permissions 
		self.permissions = self.channel
	def getUserData(self):
		if (hasattr(self, 'user') and hasattr(self, 'userData')):
			return self.userData 
		if (hasattr(self, 'user')):
			data = self.bot.getUserData(self.user.id)
			self.userData = data 
			return data 
		return None
	def getUserPermission(self, canBeSelf = False):
		if hasattr(self, 'permissionLevel'):
			return self.permissionLevel
		if hasattr(self, 'channel'):
			return bot.getPermissionLevel(self.user.id, canBeSelf)
		return 
	def getGuildData(self):
		if (self.guild and hasattr(self, 'guildData')):
			return self.guildData 
		if (self.guild):
			data = self.bot.getGuildData(self.guild.id)
			self.guildData = data 
			if data == None:
				self.bot.setupGuild(self.guild)
			return data 
		return None 




	
		
