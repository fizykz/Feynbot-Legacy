import numpy
import asyncio
import importlib
import os
import re
import subprocess
import sys
import warnings

import pymongo
import discord

import utils
import dbUtils
import discordUtils as dUtils


class MyClient(discord.Client):
	def __init__(self):
		super().__init__()
		self.commands = {}
		self.commandOverrides = {}
		self.events = {}
		self.eventOverrides = {}
		self.data = utils.fileToJson('./data.json')
		self.admins = self.data['admins']
		self.dUtils = dUtils
		self.utils = utils
		self.settings = {
			'verboseMessaging': True, 
			'overrideDiagnostics' : True
		}

	def handleEvent(self, eventName):
		async def handler(*args):
			IDs = [] #List of IDs to check for when looking for an event override.
			if (eventName in self.commands and hasattr(self.commands[eventName], 'process')):
				IDs = self.commands[eventName].process(bot, *args)
			utils.functionize(self.getEvent(eventName, IDs))(self, *args) #Get and run the needed event.

		handler.__name__ = eventName #Rename the handler to the event name (Discord.py needs this).
		self.event(handler)	#Use Discord library to hook the event.

	def reloadCommands(self, overrides=True):
		self.log('Reloading commands...', True, True)			

		for fileName in os.listdir('./Commands'):				#Iterate over command files.
			if (fileName.endswith('.py') and fileName[0:-3].isalnum()):
				commandName = fileName[0:-3]
				try:
					self.commands[commandName] = importlib.import_module('Commands.' + commandName)
					importlib.reload(self.commands[commandName])	#Reload module just in case
				except SyntaxError as error:
					self.alert(commandName + ".py errored: " + str(error), SyntaxError)

		for commandName, module in self.commands.items():				#Go over current commands, see if any were removed
			if (not (commandName + '.py') in os.listdir('./Commands')):
				self.commands[commandName] = None

		if (overrides):
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
							except SyntaxError as error:
								self.alert(commandName + ".py errored: " + str(error), SyntaxError)

			for ID, folder in self.commandOverrides.items():				#Go over current commands, see if any were removed
					for commandName in tuple(folder.keys()):
						if (commandName != '__directory'):			#Make sure we're not iterating over the metadata
							if (not (commandName + '.py') in os.listdir(folder['__directory'])):
								del folder[commandName]

		self.log('Commands reloaded.', False, True)
		return #Iterate over folders, find modules, import.

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
					self.alert(eventName + ".py errored: " + str(error), SyntaxError)	#Warn us about import errors.
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
								self.alert(eventName + ".py errored: " + str(error), SyntaxError)	#Warn if an error was thrown.
			for ID, folder in self.eventOverrides.items():	#Go over current override collections, see if any were removed
				for eventName in tuple(folder.keys()):	#Go over events in the collections.
					if (eventName != '__directory'):	#Make sure we're not iterating over the metadata
						if (not (eventName + '.py') in os.listdir(folder['__directory'])):
							del folder[eventName]	#Delete any override we don't have anymore

		self.log('Events reloaded.', False, True)
		return #Iterate over folders, find modules, import.

	def getCommand(self, message, command, returnModule = False):
		if (message.channel.id in self.commandOverrides and command in self.commandOverrides[message.channel.id]):
			module = self.commandOverrides[message.channel.id][command]
			if (returnModule):
				return module
			else:
				return module.command
		if (message.guild.id in self.commandOverrides and command in self.commandOverrides[message.guild.id]):
			module = self.commandOverrides[message.guild.id][command]
			if (returnModule):
				return module
			else:
				return module.command
		if (command in self.commands):
			module = self.commands[command]
			if (returnModule):
				return module
			else:
				return module.command
		return None

	def getEvent(self, event, IDs, returnModule = False):
		print("!!!", event, IDs)
		for ID in IDs:
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

	def isAdmin(self, id):
		return id in self.admins

	def log(self, message, verbose=True, sendToDiagnostics=False):
		if (not (not self.settings['verboseMessaging'] and verbose)):   #Send all messages except verbose ones when verbose messaging is off.  Send_verbose nand Verbose
			print(message)
			if sendToDiagnostics or self.settings['overrideDiagnostics']:
				return #Send to channel

	def alert(self, message, warning=UserWarning, sendToDiagnostics=False, major=False):
		warnings.warn(message)
		if sendToDiagnostics or self.settings['overrideDiagnostics']:
			#send to major or minor depending on the argument 
			return #Send to channel

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


	def sendMessage():
		return

	async def on_ready(self): #Bot ready to make API commands and is recieving events.
		self.log("Logged on and ready.", False, True)
		self.reloadCommands()
		self.reloadEvents()

	def getObjectByID(self, ID, forceOverride=False):
		dbUtils.getObject('_id', ID, forceOverride)

	def getObject(*args):
		dbUtils.getObject(*args)

client = MyClient()
client.run(client.data['token'])