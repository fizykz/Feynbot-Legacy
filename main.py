###
###
###
###
###
###
###
###
###
###
###
###
###
###

#Lead program stuff.  argparse, etc. #TODO: lang.py replacements.
import argparse
from utils import fileToJson
from attrdict import AttrDict as AttributeDictionary

packageInfo = fileToJson('./packageInfo.json')	#Todo:  All of these:  
parser = argparse.ArgumentParser(description = "A Python Discord bot with a powerful and modular architecture.")
parser.add_argument('--resetSafelock', '-s', dest = 'resetSafeLock', action = 'store_true', help = "Resets a safelock if it was in place.")
parser.add_argument('--livingCode', '-l', dest = 'livingCode', action = 'store_true', help = "Alllows the livingCode to be enabled.  Still needs to be unlocked before the safelock duration to be used the full session.")
parser.add_argument('--livingCodeSession', dest = 'livingCodeSession', action = 'store_true', help = "Turns off the unlock duration, so the bot won't automatically safelock.  Only use if you know what you're doing.")
parser.add_argument('--noPrinting', '-p', dest = 'noPrinting', action='store_true', help="Turns off printing for the bot.")
parser.add_argument('--verbose', '-v', dest = 'verbose', action = 'count', default = 0, help = "Prints more content when running the program, -vvv is more verbose than -v.")
parser.add_argument('--overrideDiagnostics', '-d', dest = 'overrideDiagnostics', action = 'store_true', default = 0, help = "Sends all logged messages to diagnostics.") 
parser.add_argument('--version', '-ver', action = 'version', version = packageInfo, help = "Prints more content when running the program, -vvv is more verbose than -v.")
CLIArguments = parser.parse_args()

#Build-in Libraries (Excluding argparse)
import numpy
import asyncio
import importlib
import os
import re
import subprocess
import sys
import warnings
import inspect
import math
import datetime

#Third party libraries (Excluding attrdict)
import pymongo
import discord

#Self made libraries.  NOTE: These are only the staticly imported libraries.  Under './Commands', './Overrides', and more, are dynamically imported libraries which aren't listed here.
import utils
import dbUtils
import commandInterface
import lang
import errors

class Feynbot(discord.Client):
	def __init__(self):
		super().__init__()
		self.utils = utils
		self.addTask = asyncio.create_task
		self.sleep = asyncio.sleep
		self.runConcurrently = asyncio.gather

		self.frequentEmojis = {
			'repeat': '🔁',
			'defaultAccepted': '✅',
			'defaultDenied': '❌',
		}

		self.commands = {}
		self.commandOverrides = {}
		self.events = {}
		self.eventOverrides = {}


	async def on_ready(self): #Bot ready to make API commands and is recieving events.
		lang = self.program.lang.getContent('english', 'onReady')
		def unlockCheck(message):	#Function to check for an unlock command.
			if (self.isOwner(message.author.id)):
				cmd = commandInterface.CommandInterface(self, message)
				if (cmd.commandIdentifier == 'unlock'):
					return True
		self.log(lang[0], False, True)	#"Logged on and ready"
		self.reloadCommands()
		self.reloadEvents()
		for name, emojiID in config['emojis'].items():
			self.frequentEmojis[name] = self.get_emoji(emojiID)
		if (self.getSetting('livingCode')):
			return
		try:	#TODO:  Try-Excepts need to except any other errors to safelock.
			unlockMessage = await self.wait_for('message', check=unlockCheck, timeout=300)
			self.addReaction(unlockMessage, self.getFrequentEmoji('accepted'))
			PromptPINMessage = await self.DMUserFromMessage(unlockMessage, lang[1])	#"Please type administrative PIN"
			def DMCheck(message):
				if (PromptPINMessage.channel == message.channel and message.author != self.user):
					return True 
			try:
				PINMessage = await self.wait_for('message', check=DMCheck, timeout=60)
				print(PINMessage.content, privateData['PIN'])
				if (PINMessage.content != privateData['PIN']):
					self.addReaction(PINMessage, self.getFrequentEmoji('denied'))
					self.safelock()
					self.alert(lang[2], True)	#"Safelocking the bot; incorrect PIN.""
					return False
				self.addReaction(PINMessage, self.getFrequentEmoji('accepted'))
				PromptSMSMessage = await self.DMUserFromMessage(unlockMessage, lang[3]) #"Please type sent SMS key"
				SMSKey = utils.getRandomString(6)
				SMS = utils.sendSMS(privateData['phone']['number'], privateData['phone']['carrier'], lang[4] + SMSKey) #"Here is SMS key"
				if (not SMS):
					self.replyToMessage(PromptSMSMessage, lang[5]) #"Error occured while sending SMS"
					self.alert(lang[6].format(self.prefix), True)	#"Error occured while >unlocking"
					self.safelock()
					self.addReaction(PromptSMSMessage, self.getFrequentEmoji('denied'))
				SMSMessage = await self.wait_for('message', check=DMCheck, timeout=60)
				if (SMSMessage.content == SMSKey):
					self.DMUserFromMessage(unlockMessage, lang[6]) #"Bot has been unlocked for this session/until safelock."
					self.alert(lang[6], True) #"Same ^^^"
					self.setSetting('livingCode', True)
					self.addReaction(SMSMessage, self.getFrequentEmoji('accepted'))
					return True
				else:
					self.addReaction(SMSMessage, self.getFrequentEmoji('denied'))
					self.safelock()
					self.alert(lang[7].format(self.prefix), True)	#Incorrect SMS attempt, safelocking
					return False
			except asyncio.TimeoutError as error:
				self.alert(lang[8], True)	#Safelocking after a timeout after >unlock
				self.safelock()
		except asyncio.TimeoutError as error:
			self.log(lang[9], False)	#Safelocking after inactivity.
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
					self.alert(eventName + ".py errored: " + str(error), True)	#Warn us about import errors.
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
								self.alert(eventName + ".py errored: " + str(error), True)	#Warn if an error was thrown.
			for ID, folder in self.eventOverrides.items():	#Go over current override collections, see if any were removed
				for eventName in tuple(folder.keys()):	#Go over events in the collections.
					if (eventName != '__directory'):	#Make sure we're not iterating over the metadata
						if (not (eventName + '.py') in os.listdir(folder['__directory'])):
							del folder[eventName]	#Delete any override we don't have anymore

		self.log('Events reloaded.', True, True)
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
					self.alert(commandName + ".py errored: " + str(error), True)

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
								self.alert(commandName + ".py errored: " + str(error), True)


		self.log('Commands reloaded.', True, True)
		return #Iterate over folders, find modules, import.

	def getCommand(self, commandIdentifier, channelID = None, guildID = None, returnModule = False):
		module = None
		if (channelID and channelID in self.commandOverrides and commandIdentifier in self.commandOverrides[channelID]):
			module = self.commandOverrides[channelID][commandIdentifier]
		elif (guildID and guildID in self.commandOverrides and commandIdentifier in self.commandOverrides[guildID]):
			module = self.commandOverrides[guildID][commandIdentifier]
		elif (commandIdentifier in self.commands):
			module = self.commands[commandIdentifier]

		if (returnModule):	
			return module
		else:
			return module.command
		return None
	#################
	### Utilities ###
	#################
	def getClass(self):	
		return self.__class__

	def isOwner(self, ID, canBeSelf = False):
		return ID in self.state['owners'] and (ID != self.user.id or canBeSelf)

	def isAdmin(self, ID, canBeSelf = False):
		return ID in self.state['admins'] or self.isOwner(ID, canBeSelf)

	def isModerator(self, ID, canBeSelf = False):
		return ID in self.state['moderator'] or self.isAdmin(ID, canBeSelf)

	def isBanned(self, ID):
		return ID in self.state['bannedUsers']

	def addBanned(self, ID):
		self.state['bannedUsers'].append(ID)
		#TODO:  Add to datastore

	def clearAdmins(ownersToo = True):
		self.data['admins'] = []
		if (ownersToo):
			self.data['owner'] = []

	def getPermissionLevel(self, ID, canBeSelf = False):
		if (self.isOwner(ID, canBeSelf)):
			return config['levels']['owner']
		elif (self.isAdmin(ID)):
			return config['levels']['admin']
		elif (self.isBanned(ID)):
			return config['levels']['moderator']
		elif (self.isBanned(ID)):
			return config['levels']['banned']
		else:
			return config['levels']['user']

	def safelock(self):
		self.settings['safelock'] = False

	def sendMessage(self, channel, *args, **kwargs):
		return self.addTask(channel.send(*args, **kwargs))

	def replyToMessage(self, message, *args, **kwargs):
		return self.addTask(message.channel.send(*args, **kwargs))

	def DMUser(self, user, *args, **kwargs):
		channel = user.dm_channel
		if (channel):
			return self.addTask(channel.send(*args, **kwargs))
		else:
			async def helper():
				return await (await user.create_dm()).send(*args, **kwargs)
			return self.addTask(helper())
		
	def DMUserFromMessage(self, message, *args, **kwargs):
		return self.DMUser(message.author, *args, **kwargs)

	def editMessage(self, message, *args, concurrently = False, **kwargs):
		return self.addTask(message.edit(*args, **kwargs))

	def addReaction(self, message, emoji, *args, concurrently = False, **kwargs):
		return self.addTask(message.add_reaction(emoji, *args, **kwargs)) 

	def removeReaction(self, message, reaction, concurrently = False, member = None):
		if (not member):
			member = self.user
		return self.addTask(message.remove_reaction(reaction, member))

	def getFrequentEmoji(self, name):
		if (name in self.frequentEmojis):
			return str(self.frequentEmojis[name]) or str(self.frequentEmojis["reportMe"])
		else:
			return str(self.frequentEmojis["reportMe"])

	def stringifyUser(self, author, withID = True):
		if (withID):
			return author.display_name + '#' + str(author.discriminator) + ' (' + str(author.id) + ')'
		return author.display_name + '#' + str(author.discriminator)

	def reactWithBug(self, message):
		return self.addReaction(message, self.getFrequentEmoji('reportMe'))

	################
	### Database ###
	################
	def getGuildData(self, ID, forceOverride = False):
		data = dbUtils.getObjectByID(ID, forceOverride)
		if (data):
			return data
		guild = self.get_guild(ID)
		if (guild):
			return self.setupServer(guild)

	def getUserData(self, ID, preventBanned = True, forceOverride = False):
		if (preventBanned and self.isBanned(ID)):
			return False
		data = dbUtils.getObjectByID(ID, forceOverride)
		if (data):
			if (data['banned']):
				self.addBanned(id)
				if (preventBanned):
					return False
			return data
		user = self.get_user(ID)
		if (user):
			return self.setupUser(user)

	def setupServer(self, guild):	#Should only be ran if we know the server data is missing.
		data = {
			'_id': guild.id,
			'prefix': None,	#Allows the default prefix to be changed without worried of most servers being unaffected.
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
		dbUtils.setObject(data)
		return data 

	def setupUser(self, user):
		data = {
			'_id': user.id,
			'banned': False,
			'stats': {},
		}
		return #Boop

client = None
if (__name__ == '__main__'):
	client = FeynbotClass()
	client.run(privateData['token'])
else:
	pass
