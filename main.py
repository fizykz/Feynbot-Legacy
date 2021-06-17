
#Lead program stuff.  argparse, etc. .
import argparse
from utils import fileToJson
from attrdict import AttrDict as AttributeDictionary

data = fileToJson('./config.json')
data['private'] = fileToJson('./private.json')
data['packageInfo'] = fileToJson('./packageInfo.json')

#Todo:  All of these as full features:  
parser = argparse.ArgumentParser(description = "A Python Discord bot with a powerful and modular architecture.")
parser.add_argument('--verbose', '-v', dest = 'verbosity', action = 'count', default = 0, help = "Prints more content when running the program, -vvv is more verbose than -v.")
parser.add_argument('--version', '-ver', action = 'version', version = data['packageInfo']['VERSION'], help = "Prints more content when running the program, -vvv is more verbose than -v.")
parser.add_argument('--overrideDiagnostics', '-d', dest = 'overrideDiagnostics', action = 'store_true', default = 0, help = "Sends all logged messages to diagnostics.") 
parser.add_argument('--noPrinting', '-np', dest = 'noPrinting', action='store_true', help="Removes trivial bot logging; still prints errors & key events.")

parser.add_argument('--reloadOnError', '-R', dest = 'reloadOnError', action = 'store_true', help = "Reloads commands, events, & more on most errors.")
parser.add_argument('--resetSafelock', '-s', dest = 'resetSafeLock', action = 'store_true', help = "Resets a safelock if it was in place.")
parser.add_argument('--livingCode', '-l', dest = 'livingCode', action = 'store_true', help = "Alllows the livingCode to be enabled.  Still needs to be unlocked before the safelock duration to be used the full session.")
parser.add_argument('--livingCodeSession', dest = 'livingCodeSession', action = 'store_true', help = "Turns off the unlock duration, so the bot won't automatically safelock.  Only use if you know what you're doing.")
CLIArguments = parser.parse_args()

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

import pymongo
import discord

#Self made libraries.  NOTE: These are only the staticly imported libraries.  Under './Commands', './Overrides', and more, are dynamically imported libraries which aren't listed here.
import utils
import dbUtils
import interface

class Feynbot(discord.Client):
	def __init__(self):
		super().__init__()
		self.interface = interface.Interface
		self.commands = {}
		self.commandOverrides = {}
		self.events = {}
		self.eventOverrides = {}
		self.settings = AttributeDictionary({
			'reloadOnError': CLIArguments.reloadOnError,
			'verbosity': CLIArguments.verbosity if not CLIArguments.noPrinting else -1, 
			'safelock': False,
			'prefix': data['other']['prefix']
		})
		self.state = AttributeDictionary({
			'owners': data['owners'],
			'admins': data['admins'],
			'moderators': data['moderators'],
			'channels': data['channels'],
			'banned': {},
		})
		self.log("Starting bot...")

		self.frequentEmojis = {
			'repeat': '🔁',
			'defaultAccepted': '✅',
			'defaultDenied': '❌',
			'accepted': 814316280299126794,
			'denied': 814316281376931890,
			'loading': 814316281393578026,
			'downvote': 814316273021616128,
			'upvote': 814316277291548683,
			'feynbot': 814316650291658793,
			'acceptedStatic': 815804106115383338,
			'deniedStatic': 815804106727489536,
			'bug': 815936904779399188,
		}

	#########################
	### Startup & Logging ###
	#########################
	def setVerbosity(self, verbosity):
		return 
	def log(self, message, verbosity = -1, vital = False, sendToDiagnostics = None):
		if verbosity <= self.settings['verbosity'] or vital:	#verbosity can be set to -1 if {noPrinting} is True.
			prefix = "ERROR: " if vital else ""
			print(prefix + str(message))
			if sendToDiagnostics or (sendToDiagnostics == None and vital):
				return  
	def addTask(self, *args, **kwargs):
		return asyncio.create_task(*args, **kwargs)
	def sleep(self, delay):
		self.log(f"Sleeping task for {delay} seconds.", 3)
		return asyncio.sleep(delay)
	def getClass(self):	
		return self.__class__
	def delayTask(self, delay, function, *args, **kwargs):
		async def helper():
			await self.sleep(delay)
			return function(args, kwargs)
		return self.addTask(helper())
	async def on_ready(self): #Bot ready to make API commands & to link events/commands.
		self.log("Setting up environment.")
		self.reloadCommands()
		self.reloadEvents()
		self.log("Bot ready!")
		#TODO Add verification for Living Code 

	#########################
	### Messaging & Other ###
	#########################
	def getBotEmoji(self, name):
		return self.get_emoji(self.frequentEmojis[name]) or self.get_emoji(name)
	def stringifyUser(self, user, withID = True):
		if (withID):
			return f"{user.name}#{str(user.discriminator)} <UID:{str(user.id)}>"
		return f"{user.name}#{str(user.discriminator)}"
	def addReaction(self, message, emoji):
		return self.addTask(message.add_reaction(emoji))
	def send(self, channel, content, *args, **kwargs):
		return self.addTask(channel.send(content, *args, **kwargs))
	def reply(self, message, content, *args, **kwargs):
		return self.send(message.channel, content, *args, **kwargs)
	######################	
	### Event Handling ###
	######################
	def reloadEvents(self, overrides=True):
		for fileName in os.listdir('./Events'):													# Iterate over normal event files.
			if (fileName.endswith('.py')):														# Only .py files.
				eventName = fileName[0:-3]														# Get rid of .py for the event name
				try:																			# Try, in case the module errors.
					self.events[eventName] = importlib.import_module('Events.' + eventName)		# Import and store the module in the events collection.
					importlib.reload(self.events[eventName])									# Reload module just in case this has been imported before and we're not sure.
					self.handleEvent(eventName)													# Make sure the event is listened for.
				except SyntaxError as error:													# Catch Syntax errors
					self.log(eventName + ".py errored: " + repr(error), -1, True)				# Warn us about import errors.
		for eventName, module in self.events.items():											# Go over current events, see if any were removed from our directory.
			if (not (eventName + '.py') in os.listdir('./Events')):								# Check if it's still in the directory
				self.events[eventName] = None 													# Remove module if they aren't.
		if (overrides):
			for folderName in os.listdir('./EventOverrides'):									# Iterate over override folders.
				if (re.match(r'\d+', folderName) and not re.search(r'\.', folderName)):			# Only get folder/files with a number sequence at the beginning and no '.' in the name
					ID = re.match(r'\d+', folderName).group(0)									# Get the number sequence of the override directory (ID)
					for fileName in os.listdir('./EventOverrides/' + folderName + '/'):			# Iterate over files in the directory.
						if (not ID in self.eventOverrides):										# Make sure the dictionary exists 
							self.eventOverrides[ID] = {											
								'__directory': './EventOverrides/' + folderName + '/',			# Create a collection for the collection of overrides.
							}
						if (fileName.endswith('.py')):											# Check to make sure it's a .py file.
							eventName = fileName[0:-3]											# Get the event name.
							try:																# Make sure it doesn't error on import 
								self.eventOverrides[ID][eventName] = importlib.import_module('EventOverrides.' + folderName + '.' + eventName)	# Manually import it and store it.
								importlib.reload(self.eventOverrides[ID][eventName])			# Reload in case it imports just the "old version".
								self.handleEvent(eventName)										# Make sure the event is listened for.
							except SyntaxError as error: 
								self.alert(eventName + ".py errored: " + repr(error), True)		# Warn if an error was thrown.
			for ID, folder in self.eventOverrides.items():										# Go over current override collections, see if any were removed
				for eventName in tuple(folder.keys()):											# Go over events in the collections.
					if (eventName != '__directory'):											# Make sure we're not iterating over the metadata
						if (not (eventName + '.py') in os.listdir(folder['__directory'])):		# If we can't find an event that's no longer in the folder.
							del folder[eventName]												# Delete any override we don't have anymore
	def handleEvent(self, eventName):															# Given an eventName it listens for the event and handles it, finds the correct event/passes args/etc.
		async def handler(*args):																	# Define our handler function, which is what is called when an event is fired.
			IDs = [] 																				# List of IDs to check for when looking for an *event override*.				
			if (eventName in self.events and hasattr(self.events[eventName], 'process')):			# If our event module has a process method we need to figure out how to sort overrides.
				process = self.events[eventName].process											# Get our process function.
				assert process.__code__.co_argcount - len(args) - 1 == 0, f"The {eventName} event process() function has {process.__code__.co_argcount} arguments, {eventName} event gives {len(args)} however.  Check Discord.py API reference."
				IDs = process(self, *args)
			try:
				if (inspect.iscoroutinefunction(self.getEvent(eventName, IDs).event)):					# Allows us to run coroutines & functions.	
					return self.addTask(self.getEvent(eventName, IDs).event(self, *args))				# Run a coroutine
				else:
					return self.getEvent(eventName, IDs).event(self, *args)								# Run a function
			except Exception as error:
				if self.settings['reloadOnError']:
					self.log("Reloading libraries after an error.", -1, True)
					self.reloadAll()
				raise error

		handler.__name__ = eventName 															# Rename the handler to the event name (Discord.py needs the name of the function to match.)
		self.event(handler)																		# Use Discord library to hook the event.	
	def getEvent(self, event, IDs):																# Get the highest priority event module.
		for ID in IDs:
			ID = str(ID)
			if (ID in self.eventOverrides and event in self.eventOverrides[ID]):
				return self.eventOverrides[ID][event]
		if (event in self.events):
			return self.events[event]
	########################
	### Command Handling ###
	########################
	def reloadCommands(self, overrides=True):
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
					self.alert(commandName + ".py errored: " + repr(error), True)

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
								self.alert(commandName + ".py errored: " + repr(error), True)
	def getCommand(self, commandIdentifier, channelID = None, guildID = None):
		module = None
		if (channelID and channelID in self.commandOverrides and commandIdentifier in self.commandOverrides[channelID]):
			module = self.commandOverrides[channelID][commandIdentifier]
		elif (guildID and guildID in self.commandOverrides and commandIdentifier in self.commandOverrides[guildID]):
			module = self.commandOverrides[guildID][commandIdentifier]
		elif (commandIdentifier in self.commands):
			module = self.commands[commandIdentifier]

		return module or None 
	##############################
	### Permissions & Security ###
	##############################
	def reloadAll(self, overrides = True):
		self.reloadEvents(overrides)
		self.reloadCommands(overrides)
		self.interface = importlib.reload(interface).Interface
	def isOwner(self, ID, canBeSelf = False):
		return ID in self.state.owners and (ID != self.user.id or canBeSelf)
	def isAdmin(self, ID, canBeSelf = False):
		return ID in self.state.admins or self.isOwner(ID, canBeSelf)
	def isModerator(self, ID, canBeSelf = False):
		return ID in self.state.moderators or self.isAdmin(ID, canBeSelf)
	def isBanned(self, ID):
		return ID in self.state.banned
	def addBanned(self, ID):
		self.state['bannedUsers'].append(ID)
		#TODO:  Add to datastore
	def clearAdmins(ownersToo = True):
		self.data['admins'] = []
		if (ownersToo):
			self.data['owner'] = []
	def safelock(self):
		self.log("Safelocking the bot.", -1, True)
		self.settings['safelock'] = False
	################
	### Database ###
	################
	def getGuildData(self, guild, forceOverride = False):
		ID = None 
		if (type(guild) == int):
			ID = guild 
			guild = None 
		data = dbUtils.getObjectByID(ID, forceOverride)
		if (data):
			return data
		if (not guild):
			guild = self.get_guild(ID)
		if (guild):
			return self.setupServer(guild)
	def getUserData(self, user, forceOverride = False): 
		ID = None 
		if (type(user) == int):
			ID = user 
			user = None 
		data = dbUtils.getObjectByID(user.id, forceOverride)
		if (data):
			return data
		if (not user):
			user = self.get_user(user.id)
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
	client = Feynbot()
	client.run(data['private']['bot']['token'])
else:
	pass
