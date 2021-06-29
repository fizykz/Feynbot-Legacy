
#Lead program stuff.  argparse, etc. .
import argparse
from utils import fileToJson

data = fileToJson('./config.json')
data['private'] = fileToJson('./private.json')
data['packageInfo'] = fileToJson('./packageInfo.json')

CLIArguments = None 
parser = argparse.ArgumentParser(description = "A Python Discord bot with a powerful and modular architecture.")		#CLI Argument parsing
parser.add_argument('--verbose', '-v', dest = 'verbosity', action = 'count', default = 0, help = "Prints more content when running the program, -vvv is more verbose than -v.")
parser.add_argument('--version', '-ver', action = 'version', version = data['packageInfo']['VERSION'], help = "Prints more content when running the program, -vvv is more verbose than -v.")
parser.add_argument('--overrideDiagnostics', '-d', dest = 'overrideDiagnostics', action = 'store_true', default = False, help = "Sends all logged messages to diagnostics.") 

parser.add_argument('--discordWarnings', '-w', dest = 'discordWarnings', action = 'store_true', help = "Starts logging warnings from Discord's logging feature.")
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
import random
if CLIArguments.discordWarnings:
	import logging
	logging.basicConfig(level = logging.WARNING)

import pymongo
import discord

#Self made libraries.  NOTE: These are only the staticly imported libraries.  Under './Commands', './Overrides', and more, are dynamically imported libraries which aren't listed here.
import utils
import dbUtils
import interface

class Feynbot(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.discord = discord
		self.isReady = False
		self.interface = interface.Interface
		self.commands = {}
		self.commandOverrides = {}
		self.events = {}
		self.eventOverrides = {}

		#Collection of settings/configs that influence how the bot runs.
		self.settings = {
			'overrideDiagnostics': CLIArguments.overrideDiagnostics,
			'reloadOnError': CLIArguments.reloadOnError,
			'verbosity': CLIArguments.verbosity,
			'safelock': False,
			'prefix': data['other']['prefix']
		}

		#Collection of data
		self.state = {
			'owners': data['owners'],
			'admins': data['admins'],
			'moderators': data['moderators'],
			'banned': {},
		self.log("Starting bot...")

		self.frequentEmojis = {
			'repeat': '🔁',
			'successDefault': '✅',
			'failureDefault': '❌',
			'success': 814316280299126794,
			'failure': 814316281376931890,
			'loading': 814316281393578026,
			'downvote': 855650498487910410,
			'upvote': 855650503283310632,
			'feynbot': 814316650291658793,
			'successStatic': 855650490892288050,	
			'failureStatic': 855650498035318804,
			'bug': 855650094083080212,
			'unableToSpeak': 855650088890269716,
			'fizykz': 855650614200631326,
			'feynbot': 855650527484706876,
			'credentials': data['private'],
			'links': {},
		}

	#########################
	### Startup & Logging ###
	#########################
	async def on_ready(self): #Bot ready to make API commands & to link events/commands.
		self.state.links['alertsChannel'] = self.get_channel(data['channels']['alerts'])
		self.state.links['infoChannel'] =  self.get_channel(data['channels']['info'])
		self.log("Setting up environment and inititializing commands & command structure.", 1, True, True, title = 'Setting Up', color = 430090)
		self.reloadCommands()
		self.reloadEvents()
		self.log(f"Bot ready & started.", -1, True, True, title = 'Ready', color = 430090)
		#TODO Add verification for Living Code 
	def setVerbosity(self, verbosity):
		return 
	def log(self, message, verbosity = -1, vital = False, sendToDiagnostics = None, *args, prefix = None, **kwargs):
		if verbosity <= self.settings['verbosity'] or vital:	#verbosity can be set to -1 if {noPrinting} is True.
			prefix = prefix if prefix else "VITAL: " if vital else ""
			print(prefix + str(message))
			if self.isReady and (sendToDiagnostics or (sendToDiagnostics == None and (vital or self.settings.overrideDiagnostics))):
				channel = self.state.links['alertsChannel'] if vital else self.state.links['infoChannel']
				if not channel:
					self.state.links['alertsChannel'] = self.get_channel(data['channels']['alerts'])
					self.state.links['infoChannel'] =  self.get_channel(data['channels']['info'])
				color = (kwargs['color'] if 'color' in kwargs else (12779530 if vital else 213))
				title = (kwargs['title'] if 'title' in kwargs else ('Alert' if vital else 'Post'))
				return self.send(channel, None, embed = discord.Embed(
					type = 'rich',
					title = title,
					description = message,
					url = kwargs['url'] if 'url' in kwargs else discord.embeds.EmptyEmbed,	#https://github.com/Rapptz/discord.py/issues/6657
					color = color,	# Green = 430090, Orange = 16744202, Yellow = 12835850, Red = 12779530, Blue = 213
					))

	def addTask(self, *args, **kwargs):
		return asyncio.create_task(*args, **kwargs)
	def sleep(self, delay, log = True):
		if delay == 0 or log == False:
			return asyncio.sleep(delay)
		self.log(f"Sleeping task for {delay} seconds.", 3)
		return asyncio.sleep(delay)
	def getClass(self):	
		return self.__class__
	def delayTask(self, delay, function, *args, **kwargs):
		async def helper():
			await self.sleep(delay)
			return function(args, kwargs)
		return self.addTask(helper())
	async def restart(self, shutdownDelay = 0, startupDelay = 0, cancellable = True):
		self.log(f"Closing the bot in {shutdownDelay} second(s) followed by a {startupDelay} second pause until restart.", -1, True, True, title = 'Restart')
		try:
			await self.sleep(shutdownDelay, False)	
			asyncio.run_coroutine_threadsafe(self.close(), self.loop) #https://github.com/Rapptz/discord.py/issues/5786
			self.isReady = False
		except Exception as error:
			print("VITAL ERROR: While shutting down: " + str(error))
		finally: 
			await self.sleep(startupDelay, False)
			subprocess.call([sys.executable] + sys.argv)	#reruns the script as its last remaining task with the same arguments.
	async def end(self, shutdownDelay = 0, cancellable = True):
		self.log(f"Closing the bot in {shutdownDelay} second(s) & remaining closed until further commands.", -1, True, True, title = 'Shutdown', color = 12779530)
		await self.sleep(shutdownDelay, False)
		asyncio.run_coroutine_threadsafe(self.close(), self.loop) #https://github.com/Rapptz/discord.py/issues/5786
		self.isReady = False
	#########################
	### Messaging & Other ###
	#########################
	def getBotEmoji(self, name):
		if name in self.frequentEmojis:
			try:
				return self.get_emoji(int(self.frequentEmojis[name]))
			except ValueError:
				return self.frequentEmojis[name]
		return self.get_emoji(name)
	def stringifyUser(self, user, withID = True):
		if (withID):
			return f"{user.name}#{str(user.discriminator)} <UID:{str(user.id)}>"
		return f"{user.name}#{str(user.discriminator)}"
	def addReactionTo(self, message, emoji):
		return self.addTask(message.add_reaction(emoji))
	def removeReactionTo(self, message, emoji, member):
		return self.addTask(message.remove_reaction(emoji, member))
	def send(self, channel, content, *args, ping = None, **kwargs):
		return self.addTask(channel.send(content, *args, mention_author = ping, **kwargs))
	def replyTo(self, message, content, *args, ping = None, **kwargs):
		return self.addTask(message.reply(content, *args, mention_author = ping, **kwargs))
	def DMUser(self, user, content, *args, ping = None, **kwargs):
		if user.dm_channel:
			return self.send(user.dm_channel, content, *args, mention_author = ping, **kwargs)
		else:
			async def DMHelper():
				await user.create_dm()
				return self.send(user.dm_channel, content, *args, mention_author = ping, **kwargs)
			return self.addTask(DMHelper)
	def deleteMessage(self, message, *args, **kwargs):
		return self.addTask(message.delete(*args, **kwargs))
	def giveRoles(self, member, *roles, audit = None, **kwargs):
		for i in range(len(roles)):
			try:
				roles[i] = member.guild.get_role(int(roles[i]))
			except ValueError:
				pass 
		return self.addTask(member.add_roles(*roles, *args, reason = audit, **kwargs))
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
								self.log(eventName + ".py errored: " + repr(error), -1, True)	# Warn if an error was thrown.
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
					self.log("Reloading libraries after an error.", -1, True, color = 12779530)
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
					if ('init' in self.commands[commandName].info and self.commands[commandName].info['init']):
						self.commands[commandName].init(self)
					if ('aliases' in self.commands[commandName].info):	#TODO: eventually have a register command module function that also checks if info even exists.  wrap init in a try/except
						for alias in self.commands[commandName].info['aliases']:
							assert alias.isalnum(), "Aliases should be alphanumerical."
							alias = alias.lower()
							if not (alias in self.commands and self.commands[alias].__name__ != self.commands[commandName].__name__):	#Check to make sure there's not a different module here.
								self.commands[alias] = self.commands[commandName]
							else:
								self.log(commandName + ".py errored trying to impliment alias \"" + alias + "\" but it was already taken by " + self.commands[alias].__name__ + ".py", -1, True)
				except SyntaxError as error:
					self.commands[commandName] = error 
					self.log(commandName + ".py errored: " + repr(error), -1, True)

		if (overrides):
			for ID in tuple(self.commandOverrides.keys()):		#Go over current commands, see if any were removed
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
								if ('init' in self.commandOverrides[ID][commandName].info and self.commandOverrides[ID][commandName].info['init']):
									self.commandOverrides[ID][commandName].init(self)
								if ('aliases' in self.commandOverrides[ID][commandName].info):
									for alias in self.commandOverrides[ID][commandName].info['aliases']:
										assert alias.isalnum(), "Aliases should be alphanumerical."
										alias = alias.lower()
										if not (alias in self.commandOverrides[ID] and self.commandOverrides[ID][alias].__name__ != self.self.commandOverrides[ID][commandName].__name__):	#Check to make sure there's not a different module here.
											self.commandOverrides[ID][alias] = self.commandOverrides[ID][commandName]
										else:
											self.log(commandName + ".py errored trying to impliment alias \"" + alias + "\" but it was already taken by " + self.commandOverrides[ID][alias].__name__ + ".py", -1, True)
							except SyntaxError as error:
								self.commands[commandName] = error
								self.log(commandName + ".py errored: " + repr(error), -1, True)
	def getCommand(self, commandIdentifier, IDs):
		for ID in IDs:
			ID = str(ID)
			if ID in self.commandOverrides and commandIdentifier in self.commandOverrides[ID]:
				return self.commandOverrides[ID][commandIdentifier]
		if (commandIdentifier in self.commands):
			return self.commands[commandIdentifier]
		return None 
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
			return self.setupGuild(guild)
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
	def setupGuild(self, guild):	#Should only be ran if we know the server data is missing.
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
	statuses = random.choice(["test"])
	client = Feynbot(intents = discord.Intents.all(), chunk_guild_at_startup = False, allowed_mentions = discord.AllowedMentions(everyone = False, roles = False), activity = discord.Activity(name = "quantum collapse!", type = discord.ActivityType.watching))
	client.run(data['private']['bot']['token'])
else:
	pass
