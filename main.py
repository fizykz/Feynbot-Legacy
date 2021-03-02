import numpy
import asyncio
import importlib
import os
import re
import subprocess
import sys
import warnings
import inspect

import pymongo
import discord

import utils
import dbUtils
from commandInstance

privateData = utils.fileToJson('./private.json')
config = utils.fileToJson('./config.json')


class FeynbotClass(discord.Client):
	def __init__(self):
		super().__init__()
		self.botClass = self.getClass()
		self.utils = utils
		self.addTask = asyncio.create_task
		self.sleep = asyncio.sleep
		self.runConcurrently = asyncio.gather

		self.frequentEmojis = {
			"repeat": '🔁'
		}

		self.commands = {}
		self.commandOverrides = {}
		self.events = {}
		self.eventOverrides = {}

		self.prefix = config['defaultPrefix']
		self.commandInstance = commandInstance.Class
		self.state = {
			'levels': config['levels'],
			'owners': config['owners'],
			'admins': config['admins'],
			'moderators': config['moderators'],
			'channels': config['linkedChannels'],
			'bannedUsers': [],
		}
		self.settings = config['defaultSettings']

	async def on_ready(self): #Bot ready to make API commands and is recieving events.
		def checkFunction(message):
			content = message.content 
			if (self.isOwner(message.author.id)):
				cmd = commandInstance.Class(self, message)
				if (cmd.commandIdentifier == 'unlock'):
					return True

		self.log("Logged on and ready.", False, True)
		self.reloadCommands()
		self.reloadEvents()
		for name, emojiID in config['emojis'].items():
			self.frequentEmojis[name] = self.get_emoji(emojiID)
		try:
			await self.wait_for('on_message', check=checkFunction, timeout=5)
		except asyncio.TimeoutError as error:
			self.log("Safelocking the bot.", True)
			self.safelock()

	######################
	### Event Handling ###
	######################
	def handleEvent(self, eventName):
		async def handler(*args):
			IDs = [] #List of IDs to check for when looking for an event override.
			if (eventName in self.events and hasattr(self.events[eventName], 'process')):
				process = self.events[eventName].process
				assert process.__code__.co_argcount - len(process.__defaults__ or ()), "The " + eventName + " process() function has the incorrect number of arguments.  Check Discord.py API reference."
				IDs = process(self, *args)

			if (inspect.iscoroutinefunction(self.getEvent(eventName, IDs))):
				return self.addTask(self.getEvent(eventName, IDs)(self, *args))
			else:
				return self.getEvent(eventName, IDs)(self, *args)

		handler.__name__ = eventName #Rename the handler to the event name (Discord.py needs this).
		self.event(handler)	#Use Discord library to hook the event.

	def reloadEvents(self, overrides=True):
		self.log('Reloading events...', True, True)			

		for fileName in os.listdir('./Events'):	#Iterate over event files.
			if (fileName.endswith('.py')):	#Only .py files.
				eventName = fileName[0:-3]	#Get rid of .py for the event name
				try:	#Try, in case the module errors.
					self.events[eventName] = importlib.import_module('Events.' + eventName)	#Import and store the module in the events collection.
					importlib.reload(self.events[eventName])	#Reload module just in case
					self.handleEvent(eventName)
				except SyntaxError as error:
					self.alert(eventName + ".py errored: " + str(error), True, SyntaxWarning)	#Warn us about import errors.
		for eventName, module in self.events.items():				#Go over current events, see if any were removed
			if (not (eventName + '.py') in os.listdir('./Events')):	# Check if it's still in the directory
				self.events[eventName] = None 	#Remove module.

		if (overrides):
			for folderName in os.listdir('./EventOverrides'):	#Iterate over override folders.
				if (re.match(r'\d+', folderName) and not re.search(r'\.', folderName)):	#Only get folder/files with a number sequence at the beginning and no '.' in the name
					ID = re.match(r'\d+', folderName).group(0)	#Get the number sequence (ID)
					for fileName in os.listdir('./EventOverrides/' + folderName + '/'):	#Iterate over override events.
						if (not ID in self.eventOverrides):	#Make sure the dictionary exists 
							self.eventOverrides[ID] = {
								'__directory': './EventOverrides/' + folderName + '/',	#Create a collection for the collection of overrides.
							}
						if (fileName.endswith('.py')):	#Check to make sure it's a .py file.
							eventName = fileName[0:-3]	#Get the event name.
							try:	#Make sure it doesn't error on import
								self.eventOverrides[ID][eventName] = importlib.import_module('EventOverrides.' + folderName + '.' + eventName)	#Manually import it and store it.
								importlib.reload(self.eventOverrides[ID][eventName])	#Reload in case it was prior.
								self.handleEvent(eventName)
							except SyntaxError as error: 
								self.alert(eventName + ".py errored: " + str(error), True, SyntaxWarning)	#Warn if an error was thrown.
			for ID, folder in self.eventOverrides.items():	#Go over current override collections, see if any were removed
				for eventName in tuple(folder.keys()):	#Go over events in the collections.
					if (eventName != '__directory'):	#Make sure we're not iterating over the metadata
						if (not (eventName + '.py') in os.listdir(folder['__directory'])):
							del folder[eventName]	#Delete any override we don't have anymore

		self.log('Events reloaded.', False, True)
		return #Iterate over folders, find modules, import.

	def getEvent(self, event, IDs, returnModule = False):
		for ID in IDs:
			ID = str(ID)
			if (ID in self.eventOverrides and event in self.eventOverrides[ID]):
				if (returnModule):
					return self.eventOverrides[ID][event]
				else: 
					return self.eventOverrides[ID][event].event
		if (event in self.events):
			if (returnModule):
				return self.events[event]
			else: 
				return self.events[event].event
		return None
	########################
	### Command Handling ###
	########################
	def reloadCommands(self, overrides=True):
		self.log('Reloading commands...', True, True)			

		for commandName in tuple(self.commands.keys()):				#Go over current commands, see if any were removed
			if (not (commandName + '.py') in os.listdir('./Commands')):
				del self.commands[commandName]

		for fileName in os.listdir('./Commands'):				#Iterate over command files.
			if (fileName.endswith('.py') and fileName[0:-3].isalnum()):
				commandName = fileName[0:-3]
				try:
					self.commands[commandName] = importlib.import_module('Commands.' + commandName)
					importlib.reload(self.commands[commandName])	#Reload module just in case
					if ('aliases' in self.commands[commandName].info):
						for alias in self.commands[commandName].info['aliases']:
							assert alias.isalnum(), "Aliases should be alphanumerical."
							alias = alias.lower()
							if not (alias in self.commands and self.commands[alias].__name__ != self.commands[commandName].__name__):	#Check to make sure there's not a different module here.
								self.commands[alias] = self.commands[commandName]
							else:
								self.alert(commandName + ".py errored trying to impliment alias \"" + alias + "\" but it was already taken by " + self.commands[alias].__name__ + ".py", True, True)
				except SyntaxError as error:
					self.commands[commandName] = error 
					self.alert(commandName + ".py errored: " + str(error), True, SyntaxError)

		if (overrides):
			for ID in tuple(self.commandOverrides.keys()):				#Go over current commands, see if any were removed
				folder = self.commandOverrides[ID]
				for commandName in tuple(folder.keys()):
					if (commandName != '__directory'):			#Make sure we're not iterating over the metadata
						if (not (commandName + '.py') in os.listdir(folder['__directory'])):
							del folder[commandName]

			for folderName in os.listdir('./CommandOverrides'):						#Iterate over override folders.
				if (re.match(r'\d+', folderName) and not re.match(r'\.', folderName)):
					ID = re.match(r'\d+', folderName).group(0)
					for fileName in os.listdir('./CommandOverrides/' + folderName + '/'):	#Iterate over override commands.
						if (not ID in self.commandOverrides):
							self.commandOverrides[ID] = {
								'__directory': './CommandOverrides/' + folderName + '/',
							}
						if (fileName.endswith('.py') and fileName[0:-3].isalnum()):
							commandName = fileName[0:-3]
							try:
								self.commandOverrides[ID][commandName] = importlib.import_module('CommandOverrides.' + folderName + '.' + commandName)
								importlib.reload(self.commandOverrides[ID][commandName])
								if ('aliases' in self.commandOverrides[ID][commandName].info):
									for alias in self.commandOverrides[ID][commandName].info['aliases']:
										assert alias.isalnum(), "Aliases should be alphanumerical."
										alias = alias.lower()
										if not (alias in self.commandOverrides[ID] and self.commandOverrides[ID][alias].__name__ != self.self.commandOverrides[ID][commandName].__name__):	#Check to make sure there's not a different module here.
											self.commandOverrides[ID][alias] = self.commandOverrides[ID][commandName]
										else:
											self.alert(commandName + ".py errored trying to impliment alias \"" + alias + "\" but it was already taken by " + self.commandOverrides[ID][alias].__name__ + ".py", True, True)
							except SyntaxError as error:
								self.commands[commandName] = error
								self.alert(commandName + ".py errored: " + str(error), True, SyntaxError)


		self.log('Commands reloaded.', False, True)
		return #Iterate over folders, find modules, import.

	def getCommand(self, message, command, returnModule = False):
		module = None
		if (message.channel.id in self.commandOverrides and command in self.commandOverrides[message.channel.id]):
			module = self.commandOverrides[message.channel.id][command]
		elif (message.guild and message.guild.id in self.commandOverrides and command in self.commandOverrides[message.guild.id]):
			module = self.commandOverrides[message.guild.id][command]
		elif (command in self.commands):
			module = self.commands[command]

		if (returnModule):	
			return module
		else:
			return module.command
		return None
	#################
	### Utilities ###
	#################
	def isOwner(self, id):
		return id in self.data['owner']

	def isAdmin(self, id):
		return id in self.data['admins'] or id in self.data['owner']

	def safelock(self):
		self.settings['safelock'] = False

	def sendMessage(self, channel, *args, **kwargs):
		return self.addTask(channel.send(*args, **kwargs))

	def editMessage(self, message, *args, **kwargs):
		return self.addTask(message.edit(*args, **kwargs))

	def addReaction(self, message, emoji, *args, **kwargs):
		return self.addTask(message.add_reaction(emoji, *args, **kwargs))

	def removeReaction(self, message, reaction, member = None):
		if (not member):
			member = self.user 
		bot.addTask(message.remove_reaction(bot.getFrequentEmoji('repeat'), bot.user))

	def getFrequentEmoji(self, name):
		if (name in self.frequentEmojis):
			return str(self.frequentEmojis[name]) or str(self.frequentEmojis["reportMe"])
		else:
			return str(self.frequentEmojis["reportMe"])

	def stringifyUser(self, author):
		return author.display_name + '#' + str(author.discriminator) + ' (' + str(author.id) + ')'

	def parseString(self, string):
		return []

	def log(self, message, verbose=True, sendToDiagnostics=False):
		if (not (not self.settings['verboseMessaging'] and verbose)):   #Send all messages except verbose ones when verbose messaging is off.  Send_verbose nand Verbose
			print(message)
			if sendToDiagnostics or self.settings['overrideDiagnostics']:
				return #Send to channel

	def alert(self, message, sendToDiagnostics=False, error=False):
		if (error):
			warnings.warn(message, UserWarning)
		else:
			print("ALERT: \t" + str(message))
		if sendToDiagnostics or self.settings['overrideDiagnostics']:
			#send to major or minor depending on the argument 
			return #Send to channel

	async def reactWithBug(self, message):
		await self.addReaction(message, self.getFrequentEmoji('reportMe'))

	async def restart(self, endDelay=0, startDelay=0):
		await asyncio.sleep(endDelay)
		try:
			await self.close()
		except:
			pass
		await self.logout()
		await asyncio.sleep(startDelay)
		subprocess.call([sys.executable, "main.py"])

	async def end(self, endDelay=0):
		await asyncio.sleep(endDelay)
		try:
			await self.close()
		except:
			pass
		await self.logout()

	################
	### Database ###
	################
	def getObjectByID(self, ID, forceOverride=False):
		return dbUtils.getObject('_id', ID, forceOverride)

	def getObject(self, *args):
		return dbUtils.getObject(*args)

	def setObject(self, *args):
		dbUtils.setObject(data)

	def setupServer(self, guild):
		if (dbUtils.getObjectByID(guild.id)) :
			return
		#Check if server is already contained/setup/updated
		data = {
			'_id': guild.id,
			'prefix': '>',
			'roleData': {},
			'stats': {},
			'disabledCommands': [],
			'roleInfo': {
				'starter': [],
				'verification': [],
				'ranks': [],
				'selection': {},
			},

		}
		self.setObject(data)

	def setupUser(self, user):
		return #Boop

client = FenynbotClass()
client.run(client.privateData['token'])