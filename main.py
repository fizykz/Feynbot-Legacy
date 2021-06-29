#Argparsing first in case we end up terminating early.
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

#Self made libraries.  NOTE: These are only the staticly imported libraries.  
#Under './Commands', './Overrides', and more, are dynamically imported libraries which aren't listed here.
#See architecture documentation #TODO
import utils
import dbUtils
import interface

class Feynbot(discord.Client):
	"""The Feynbot class.""" #TODO

	#Libraries
	interface = interface.Interface
	discord = discord

	#Frequent Emojis #TODO: update all old IDs to new dev server.
	frequentEmojis = {
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
		'feynbot': 855650527484706876,}
	def __init__(self, *args, **kwargs):
		"""Initializes a bot instance.  This represents the bot's state & interface.
		Passing arguments passes them directly to the superclass, discord.Client.
		See discord.Client for more information on how the bot is actually operated, as this package serves mostly as an overlaying interface.
		"""
		#Superclass
		super().__init__(*args, **kwargs)

		self.isReady = False
		
		#Command collection
		self.commands = {}
		self.commandOverrides = {}

		#Event collection.
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
			'credentials': data['private'],
			'links': {},
		}
		self.log("Starting bot...")
	################
	### Asynchio ###
	################
	def addTask(self, *args, **kwargs):
		"""Creates an asynchio task through the bot and returns it."""
		return asyncio.create_task(*args, **kwargs)
	def isFuture(self, *args, **kwargs):
		"""Returns true if an object is a future object.
		Short circuit to asyncio.isfuture
		"""
		return asyncio.isfuture(*args, **kwargs)
	def sleep(self, delay, *args, log = True):
		"""Sleeps the current coroutine for {delay} seconds.  Will also optionally log if verbosity >= 3."""
		if delay == 0 or log == False:
			return asyncio.sleep(delay)
		self.log(f"Sleeping task for {delay} seconds.", 3)
		return asyncio.sleep(delay)
	def delayTask(self, delay, function, *args, log = True, **kwargs):
		"""Delays a function by {delay} and returns an Asynchio task of the function.  Can take coroutines or functions."""
		async def helper():
			"""Check if our function is a coroutine, if not just run and return, otherwise await it's return."""
			await self.sleep(delay, log = log)
			if inspect.iscoroutinefunction(function):
				return await function(*args, **kwargs)
			else:
				return function(*args, **kwargs)
			
		return self.addTask(helper())
	def runFunction(self, function, *args, **kwargs):
		"""Runs a coroutine or a function, regardless of type."""
		if inspect.iscoroutinefunction(function):
			return self.addTask(function(*args, **kwargs))
		else:
			return function(*args, **kwargs)
	######################
	### Error Handling ###
	######################
	def HTTPError(self, error):	#TODO Notify repetitive HTTPExceptions.
		"""Handles an HTTP Exception, currently incomplete."""
		self.log("HTTPError: ", error, repr = True)	
	def ForbiddenError(self, error):
		"""Handles an HTTP Exception, currently incomplete."""
		self.log("HTTPError: ", error, repr = True)
	###############
	### Fetches ###
	###############
	async def getChannels(self, *IDs, guilds = None, fetch_guilds = False, suppress = False):
		"""Returns a list of channels given IDs/or if they're channels already, asserts them.
		A list entry will be False if Forbidden, None if an HTTPException occured, or raise an error if it wasn't a proper channel ID.
		"""
		channels = []
		#Go through and grab or fetch all the channels by their IDs, might be awaiting them.
		#If an {ID} is already a channel, just make sure it is and not something else.
		if len(IDs) == 0 and not guilds:
			raise error("getChannel() was called with no IDs and no guilds.")
		for ID in IDs:
			channel = self.get_channel(ID)
			if channel:
				channels.append(channel)
			else:
				try:
					channel = self.addTask(self.fetch_channel(ID))	#TODO supress errors if suppress
					#Will still potentially raise NotFound & InvalidData errors.
				except discord.HTTPException as error:
					channels.append(None)
					self.HTTPError(error)
				except discord.Forbidden as error:
					channels.append(False)
					self.ForbiddenError(error)
		#Await all our channels.
		for channel in channels:
			if self.isFuture(channel):
				await channel
		if guilds:
			for guild in guilds:
				if fetch_guilds:
					channels.extend(await guild.fetch_channels())
				else:
					channels.extend(guild.channels)
		return tuple(channels)
	####################################
	### Startup, Logging, & Settings ###
	####################################
	async def on_ready(self): 
		"""The function first ran when the bot opens up.
		API calls are able to be made at this point, which the bot first uses to find and get it's logging channels.
		These logging channels represent Discord channels which have information pushed to them when asked to through Feynbot.log()

		What's most important about this function however is it's when it initializes bot commands & events.  
		Commands are initialized first then events (so all commands are available on the events being listened to)
		More info on these in the respective sections.
		"""
		#Link our channels.
		self.state['links']['alertsChannel'] = await self.fetch_channel(data['channels']['alerts'])	
		self.state['links']['infoChannel'] =  await self.fetch_channel(data['channels']['info'])
		self.log("Setting up environment and inititializing commands & command structure.", verbosity = 1, critical = True, title = 'Setting Up', color = 430090)
		self.reloadAll(startup = True)	#reload all with the intention of startup.
		self.log(f"Bot ready & started.", verbosity = -1, critical = True, title = 'Ready', color = 430090)
		#TODO Add verification for Living Code 
	def setVerbosity(self, verbosity):
		"""Sets the bot's verbosity to an interger from 0 to 4.
		Higher numbers represent higher verbosity and more messages being sent to logging.
		High verbosity is not recommended with overriding diagnostic messages to linked channels.
		"""
		try:
			verbosity = float(verbosity)
			if (verbosity % 1 == 0 and 0 <= verbosity and verbosity <= 4):	#check it's an integer 0 to 4.
				self.settings['verbosity'] = verbosity
			else:
				raise ValueError(f"Verbosity should be an integer 0 to 4 but got {repr(verbosity)} instead.")
		except ValueError: 
			raise ValueError(f"Verbosity should be an integer 0 to 4 but got {repr(verbosity)} instead.") from None
	def log(self, *args, verbosity = -1, critical = False, sendToDiagnostics = None, useRepr = False, prefix = None, title = None, url = None, color = None):
		"""Logs a message to the bot console & possibly logging channels.
		{*args} represents what to print, spaced and concatenated by a horizontal tab.
		{verbosity} is a check if a message should be printed.

		Green = 430090, Orange = 16744202, Yellow = 12835850, Red = 12779530, Blue = 213
		"""
		#Return if it doesn't meet verbosity requirements and it's not critical.
		if verbosity >= self.settings['verbosity'] and not critical:	
			return 

		message = "" 
		for msg in args:	#Go through our arguments and convert everything to a string using {str} or {repr}
			if useRepr:
				message = message + f'{repr(msg)}\t'
			else:
				 message = message + f'{str(msg)}\t'
		prefix = prefix if prefix else "Σ: " if critical else "λ: "
		print(prefix + message)

		#Check if we need to send to the diangostic channels.	
		if self.isReady and (sendToDiagnostics or (sendToDiagnostics == None and (critical or self.settings['overrideDiagnostics']))):
			#If it's critical, send to the alerts channel, otherwise info.
			channel = self.state['links']['alertsChannel'] if critical else self.state['links']['infoChannel']
			color = (kwargs['color'] if 'color' in kwargs else (12779530 if critical else 213))
			title = (kwargs['title'] if 'title' in kwargs else ('Alert' if critical else 'Post'))
			return self.send(channel, None, embed = discord.Embed(
				type = 'rich',
				title = title,
				description = message,
				url = kwargs['url'] if 'url' in kwargs else discord.embeds.EmptyEmbed,	#https://github.com/Rapptz/discord.py/issues/6657
				color = color,
				))
	async def restart(self, shutdownDelay = 0, startupDelay = 0, cancellable = True):
		"""Shutsdown the bot in {shutdownDelay} seconds. 
		Then restarts the bot in {startupDelay}.
		{cancellable} dictates if it be cancelled by command.
		"""
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
		"""Shutsdown the bot in {shutdownDelay} seconds. 
		{cancellable} dictates if it be cancelled by command.
		"""
		self.log(f"Closing the bot in {shutdownDelay} second(s) & remaining closed until further commands.", -1, True, True, title = 'Shutdown', color = 12779530)
		await self.sleep(shutdownDelay, False)
		asyncio.run_coroutine_threadsafe(self.close(), self.loop) #https://github.com/Rapptz/discord.py/issues/5786
		self.isReady = False
	#########################
	### Messaging & Other ###
	#########################
	def getBotEmoji(self, name):
		"""Grabs a frequent or another bot emoji"""
		if name in self.frequentEmojis:
			try:
				return self.get_emoji(int(self.frequentEmojis[name]))
			except ValueError:
				return self.frequentEmojis[name]
		return self.get_emoji(name)
	def addReactionTo(self, message, emoji):	#TODO allow grabbing an emoji if it isn't already an emoji
		"""Add an {emoji} to a {message}"""
		return self.addTask(message.add_reaction(emoji))
	def removeReactionTo(self, message, emoji, member = None):	#TODO allow grabbing an emoji if it isn't already an emoji
		"""Removes an {emoji} of a given {message} of a certain {member} or the bot be default."""
		return self.addTask(message.remove_reaction(emoji, member or self.user))
	def send(self, channel, content, *args, ping = None, **kwargs):
		"""Sends a message to a given channel."""
		return self.addTask(channel.send(content, *args, mention_author = ping, **kwargs))
	def replyTo(self, message, content, *args, ping = None, **kwargs):
		"""Replies to a message."""
		return self.addTask(message.reply(content, *args, mention_author = ping, **kwargs))
	def DMUser(self, user, content, *args, ping = None, **kwargs):
		"""DMs a {user}"""
		if user.dm_channel:
			return self.send(user.dm_channel, content, *args, mention_author = ping, **kwargs)
		else:
			async def DMHelper():
				await user.create_dm()
				return self.send(user.dm_channel, content, *args, mention_author = ping, **kwargs)
			return self.addTask(DMHelper)
	def deleteMessage(self, message, *args, **kwargs):
		"""Deletes a message."""
		return self.addTask(message.delete(*args, **kwargs))
	def giveRoles(self, member, *IDs, audit = None, **kwargs): #TODO
		"""Gives a member a list of roles from a list of IDs."""
		roles = []
		for ID in IDs:
			try:
				roles.append(member.guild.get_role(int(ID)))
			except ValueError:
				pass 
		return self.addTask(member.add_roles(*roles, reason = audit, **kwargs))
	################################	
	### Command & Event Handling ###
	################################
	def registerEvent(self, *, eventName, modulePath, override, startup):
		"""Given an eventName, the module path, [the override key], and startup, this registers an event.
		This will manually import and reload the module, handling syntax errors.
		Finally it'll also run an init() and startup() function, if present in the right context.
		"""
		module = None 
		events = self.events
		if (override):
			events = self.eventOverrides[override]
		try:
			module = importlib.import_module(modulePath)
			module = importlib.reload(module)	#Reload the module just in case we've ran before.
		except SyntaxError as error:
			events[eventName] = error 
			self.log(f"{error.filename}:{error.lineno}:{error.offset}:\n{error.text}", verbosity = -1, critical = True)
			return False
		events[eventName] = module

		#We'll now try running either startup() or init() if they exist.
		try:
			if (startup and hasattr(module, 'startup')):
				self.log(f"Running {modulePath}.py startup().", verbosity = 1, critical = True)
				self.runFunction(module.startup, self)
			elif (hasattr(module, 'init')):		#Note this runs init on startup if startup doesn't exist.
				self.log(f"Running {modulePath}.py init().", verbosity = 1, critical = True)
				self.runFunction(module.init, self)
		except Exception as error:
			if (startup and hasattr(module, 'startup')):
				self.log(f"{modulePath}.py errored on startup(): {str(error)}", verbosity = -1, critical = True)
			else:
				self.log(f"{modulePath}.py errored on init(): {str(error)}", verbosity = -1, critical = True)
			del events[eventName] #Remove the command after a setup error.
			return False 
		if not override:
			self.handleEvent(eventName)
		return True 
	def reloadEvents(self, *, overrides=True, startup = False):
		"""Reloads all commands.
		This will iterate over ./Events and ./OverrideEvents
		It will process them and store them in the bots dictionaries.
		This will make them available to getEvent() which is called when an event is fired.
		This is called through handleEvent()'s handler() function.
		"""
		#Remove previous events.
		for eventName in tuple(self.events.keys()):
			del self.events[eventName]

		#Iterate over & register.
		for fileName in os.listdir('./Events'):
			if (fileName.endswith('.py')):
				eventName = fileName[0:-3]
				self.registerEvent(eventName = eventName, modulePath = f'Events.{eventName}', override = False, startup = startup)

		if (overrides):
			#Remove previous events.
			for ID in tuple(self.eventOverrides.keys()):
				del eventOverrides[ID]

			for folderName in os.listdir('./EventOverrides'):
				if (re.match(r'\d+', folderName) and not re.search(r'\.', folderName)):
					ID = re.match(r'\d+', folderName).group(0)
					self.eventOverrides[ID] = {}
					for fileName in os.listdir('./EventOverrides/' + folderName + '/'):
						if (fileName.endswith('.py')):
							eventName = fileName[0:-3]
							self.registerEvent(eventName = eventName, modulePath = f'EventOverrides.{folderName}.{eventName}', override = True, startup = startup)
	def handleEvent(self, eventName):
		"""This function binds an event to a handler() function which takes care of all the calls.
		This function without handler() only connects it to begin with, but it is not ran everytime an event fires.
		See the inner handler() function for that.
		"""
		async def handler(*args, **kwargs):
			"""This function is called and takes all args and kwargs from an event when one is fired.
			It begins by getting a list of IDs from the process function in the default event module in /events.
			After this, it will call getEvent() and find the highest overriding event and call that module's event function with all it's arguments.
			"""
			IDs = [] 
			if (eventName in self.events and hasattr(self.events[eventName], 'process')):		# If our event module has a process method we need to figure out how to sort overrides.
				process = self.events[eventName].process										# Get our process function.
				assert process.__code__.co_argcount - len(args) - 1 == 0, f"The {eventName} event process() function has {process.__code__.co_argcount} arguments, {eventName} event gives {len(args)} however.  Check Discord.py API reference."
				IDs = process(self, *args)
				event = self.getEvent(eventName, IDs)											# Our event module.
				try:
					assert event.event.__code__.co_argcount - len(args) - 1 == 0, f"The {event.__file__} event function has {event.event.__code__.co_argcount} arguments, {eventName} event gives {len(args)} however.  Check Discord.py API reference."
					if (inspect.iscoroutinefunction(event.event)):					# Is this a coroutine or a function?
						return self.addTask(event.event(self, *args))				# Run a coroutine
					else:
						return event.event(self, *args)								# Run a function
				except Exception as error:	# Catch any error to reload the library, we'll raise it again after.
					if self.settings['reloadOnError']:
						self.log("Reloading libraries after an error.", verbosity = -1, critical = True, color = 12779530)
						self.reloadAll()
					raise error from None 
			elif (eventName in self.events):
				self.log(f"Event {eventName} doesn't have a process function and wasn't able to be checked for overrides!  Consider adding it!", verbosity = -1, critical = -1, title = "No Process Function")
			else:
				self.log(f"Event {eventName} was removed from the events dictionary when the event was fired!  Consider unlistening ot the event or ensuring it remains.", verbosity = -1, critical = -1, title = "No Event")
				raise RuntimeError(f"Event {eventName} was removed from the events dictionary when the event was fired!  Consider unlistening ot the event or ensuring it remains.")
		handler.__name__ = eventName 	# Rename the handler to the event name (Discord.py needs the name of the function to match.)
		self.event(handler)				# Use Discord library to hook the event and start listening.
	def getEvent(self, event, IDs):
		"""Grabs the high priority event module.
		This is dictated by the default event's process() function, it will be given all event arguments and return a list of IDs.
		Which will be the list of IDs given to this function.
		This function then iterates over those IDs, checking what's the highest priority and then running that module.
		"""
		for ID in IDs:	#Check if there's an overriding event for any of our IDs.
			ID = str(ID)
			if (ID in self.eventOverrides and event in self.eventOverrides[ID]):
				return self.eventOverrides[ID][event]
		#We didn't find any, we'll grab the default event instead.
		if (event in self.events):
			return self.events[event]
	def registerCommand(self, *, commandName, modulePath, override, startup):
		"""Given a commandName, the module path, [the override key], and startup, this registers a commands.
		This will manually import and reload the module, handling syntax errors.
		It will process aliases & also give some tips/warnings if anythings out of sorts.
		Finally it'll also run an init() and startup() function, if present in the right context.
		"""
		module = None 
		commands = self.commands
		if (override):
			commands = self.commandOverrides[override]
		try:
			module = importlib.import_module(modulePath)
			module = importlib.reload(module)	#Reload the module just in case we've ran before.
			self.log(f"{module.__file__} reloaded.", verbosity = 2)
		except SyntaxError as error:
			commands[commandName] = error 
			self.log(f"{error.filename}:{error.lineno}:{error.offset}:\n{error.text}", verbosity = -1, critical = True)
			return False
		if commandName in commands:
			otherModule = commands[commandName]
			self.log(f"{otherModule.__file__} has an alias of {commandName} but a package by this name already exists!\n{module.__file__} will now replace this alias.", verbosity = -1, critical = True)
		if not (hasattr(module, 'info') and 'name' in module.info): 
			self.log(f"{module.__file__} is missing a dictionary entry module.info['name'].  Consider adding it.", verbosity = -1, critical = True)
		else:
			#Make sure this file is marked to be registered or not marked at all.
			if (hasattr(module, 'info') and 'register' in module.info and module.info['register'] == False):
				return
		commands[commandName] = module

		#We'll now try running either startup() or init() if they exist.
		try:
			if (startup and hasattr(module, 'startup')):
				self.log(f"Running {modulePath}.py startup().", verbosity = 1, critical = True)
				self.runFunction(module.startup, self)
			elif (hasattr(module, 'init')):		#Note this runs init on startup if startup doesn't exist.
				self.log(f"Running {modulePath}.py init().", verbosity = 1, critical = True)
				self.runFunction(module.init, self)
		except Exception as error:
			if (startup and hasattr(module, 'startup')):
				self.log(f"{modulePath}.py errored on startup(): {str(error)}", verbosity = -1, critical = True)
			else:
				self.log(f"{modulePath}.py errored on init(): {str(error)}", verbosity = -1, critical = True)
			del commands[commandName] #Remove the command after a setup error.

		# Check & add aliases.
		if ('aliases' in commands[commandName].info):	
			for alias in commands[commandName].info['aliases']:
				assert alias.isalnum(), "Aliases should be alphanumerical."
				alias = alias.lower()
				if not (alias in commands and commands[alias].__name__ != commands[commandName].__name__):	#Check to make sure there's not a different module here.
					commands[alias] = commands[commandName]
				else:
					self.log(f"{commandName}.py tried to impliment alias \"{alias}\" but it was already taken by {commands[alias].__name__}.py", verbosity = -1, critical = True)
		return True 
	def reloadCommands(self, *, overrides=True, startup = False):
		"""Iterates over ./Commands and ./CommandOverrides
		Finds all .py command files, and attempts to register them to the bot.
		Registering adds it to the Commands and CommandOverrides tables, which are retrieved by getCommand()
		"""
		#First we'll handle global commands.
		#Go over current direct message commands, delete them from the registry.
		for commandName in tuple(self.commands.keys()):	
			del self.commands[commandName]
		#Iterate over command files.
		for fileName in os.listdir('./Commands'):	
			if (fileName.endswith('.py') and fileName[0:-3].isalnum()): # Valid command should be an alphanumerical name followed by .py
				commandName = fileName[0:-3]
				self.registerCommand(commandName = commandName, modulePath = f'Commands.{commandName}', override = False, startup = startup)
		if (overrides):
			#Remove previous override commands.
			for ID in tuple(self.commandOverrides.keys()):
				del self.commandOverrides[ID]
			#Iterate over override folders.
			for folderName in os.listdir('./CommandOverrides'):					
				if (re.match(r'\d+', folderName) and not re.match(r'\.', folderName)):
					ID = re.match(r'\d+', folderName).group(0)
					#Iterate over override commands.
					for fileName in os.listdir('./CommandOverrides/' + folderName + '/'):	
						if (not ID in self.commandOverrides):
							self.commandOverrides[ID] = {}
						if (fileName.endswith('.py') and fileName[0:-3].isalnum()):
							commandName = fileName[0:-3]
							self.registerCommand(commandName = commandName, modulePath = f'CommandOverrides.{folderName}.{commandName}', override = ID, startup = startup)
	def getCommand(self, commandIdentifier, IDs, DMs):
		"""Grabs the highest priority command given the user, channel, and guild ID. 
		Also may choose commands for DMs.
		"""

		for ID in IDs:
			ID = str(ID)
			if ID in self.commandOverrides and commandIdentifier in self.commandOverrides[ID]:
				module = self.commandOverrides[ID][commandIdentifier]
				info = module.info if hasattr(module, 'info') else {}
				direct = info['direct'] if 'direct' in info else True
				directOnly = info['directOnly'] if 'directOnly' in info else False 
				if ((DMs and (directOnly or direct)) or (not DMs and not directOnly)):
					return module

		if (commandIdentifier in self.commands):
			module = self.commands[commandIdentifier]
			info = module.info if hasattr(module, 'info') else {}
			direct = info['direct'] if 'direct' in info else True
			directOnly = info['directOnly'] if 'directOnly' in info else False 
			if ((DMs and (directOnly or direct)) or (not DMs and not directOnly)):
				return module
			
		return None 
	def reloadAll(self, *, overrides = True, startup = False):
		"""Reloads all events and all commands, including overrides if {overrides} and dictates if it should run startup functions if {startup}."""
		self.reloadEvents(overrides = overrides, startup = startup)
		self.reloadCommands(overrides = overrides, startup = startup)
		self.interface = importlib.reload(interface).Interface
	##############################
	### Permissions & Security ###
	##############################
	def isOwner(self, ID, canBeSelf = False):
		"""Returns true if userID is one of the owners. {canBeSelf} dictates if it can be the bot."""
		return ID in self.state['owners'] or (ID == self.user.id and canBeSelf)
	def isAdmin(self, ID, canBeSelf = False):
		"""Returns true if userID is an admin or above. {canBeSelf} dictates if it can be the bot."""
		return ID in self.state['admins'] or self.isOwner(ID, canBeSelf)
	def isModerator(self, ID, canBeSelf = False):
		"""Returns true if userID is a moderator or above. {canBeSelf} dictates if it can be the bot."""
		return ID in self.state['moderators'] or self.isAdmin(ID, canBeSelf)
	def isBanned(self, ID):
		"""Returns true if a userID is banned."""
		return ID in self.state['banned']
	def addBanned(self, ID):
		"""Adds an ID to the banned list and the databse."""
		self.state['bannedUsers'].append(ID)
		#TODO:  Add to datastore
	def clearStaff(self, *, moderators = True, admins = True, owners = True):
		"""Wipes IDs for ranks from the state.  This is mostly a security feature."""
		if (admins):
			self.data['admins'] = []
		if (owners):
			self.data['owners'] = []
		if (moderators):
			self.data['moderators'] = []
	#############
	### Other ###
	#############
	def stringifyUser(self, user, withID = True):
		"""Turns a user into a string with the form:
		username#0000 <UID:00000000000000>
		Where 0's represent the discriminator and user ID (If {withID} is true)
		"""
		if (withID):
			return f"{user.name}#{str(user.discriminator)} <UID:{str(user.id)}>"
		return f"{user.name}#{str(user.discriminator)}"
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
			'prefix': None,
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
			'lastDM': 0,
			'lastMessage': 0,
			'lastCommand': 0,
		}
		return #Boop

if (__name__ == '__main__'):
	client = Feynbot(intents = discord.Intents.all(), chunk_guild_at_startup = False, allowed_mentions = discord.AllowedMentions(everyone = False, roles = False), activity = discord.Activity(name = "quantum collapse!", type = discord.ActivityType.watching))
	client.run(data['private']['bot']['token'])
