import numpy
import asyncio
import importlib
import os
import re

import pymongo
import discord

import utils
import dbUtils
import discordUtils as dUtils


class MyClient(discord.Client):
	def __init__(self):
		super().__init__()
		self.commands = {}
		self.overrides = {}
		self.data = utils.fileToJson('./data.json')
		self.admins = self.data['admins']
		self.settings = {
			'verboseMessaging': True, 
			'overrideDiagnostics' : True
		}	

	def reloadCommands(self):
		self.log('Reloading commands...', True, True)			

		for fileName in os.listdir('./Commands'):				#Iterate over command files.
			if (fileName.endswith('.py') and fileName[0:-3].isalnum()):
				commandName = fileName[0:-3]
				self.commands[commandName] = importlib.import_module('Commands.' + commandName)
				importlib.reload(self.commands[commandName])	#Reload module just in case
		for commandName, module in self.commands.items():				#Go over current commands, see if any were removed
			if (not (commandName + '.py') in os.listdir('./Commands')):
				self.commands[commandName] = None

		for folderName in os.listdir('./Overrides'):						#Iterate over override folders.
			if (re.match(r'\d+', folderName) and not re.match(r'\.', folderName)):
				ID = re.match(r'\d+', folderName).group(0)
				for fileName in os.listdir('./Overrides/' + folderName + '/'):	#Iterate over override commands.
					if (not ID in self.overrides):
						self.overrides[ID] = {
							'__directory': './Overrides/' + folderName + '/',
						}
					if (fileName.endswith('.py') and fileName[0:-3].isalnum()):
						commandName = fileName[0:-3]
						self.overrides[ID][commandName] = importlib.import_module('Overrides.' + folderName + '.' + commandName) #Please dear God let | 'Overrides.' + folderName + '.' + commandName | work
						importlib.reload(self.overrides[ID][commandName])
						print(self.overrides[ID][commandName], self.overrides[ID][commandName].help)
		for ID, folder in self.overrides.items():				#Go over current commands, see if any were removed
				for commandName in tuple(folder.keys()):
					if (commandName != '__directory'):			#Make sure we're not iterating over the metadata
						if (not (commandName + '.py') in os.listdir(folder['__directory'])):
							del folder[commandName]

		self.log('Commands reloaded.', False, True)
		return #Iterate over folders, find modules, import.

	def getCommand(self, id, command):
		return #if overrides[id][command], else return commands[command] if plausible

	def isAdmin(self, id):
		return id in client['admins']

	def log(self, message, verbose=True, sendToDiagnostics=False):
		if (not (not self.settings['verboseMessaging'] and verbose)):   #Send all messages except verbose ones when verbose messaging is off.  Send_verbose nand Verbose
			print(message)
			if sendToDiagnostics or self.settings['overrideDiagnostics']:
				return #Send to channel

	def alert(self, message, sendToDiagnostics=False, major=False):
		return 1 #Insert here

	async def restart(self):
		await self.logout()
		await self.run(client.data['token'])

	def sendMessage():
		
		return



	async def on_ready(self):					#Bot ready to make API commands and is recieving events.
		dUtils.onReady(client)


	async def on_message(self, message):		#Message recieved: (self, message)
		dUtils.onMessage(client, message)


	async def on_guild_join(self, guild):
		dUtils.onGuildJoin(client, guild)

	async def on_guild_remove(self, guild):
		dUtils.onGuildRemove(client, guild)

	async def on_guild_available(self, guild):
		dUtils.onGuildAvailable(client, guild)

	async def on_guild_unavailable(self, guild):
		dUtils.onGuildUnavailable(client, guild)

client = MyClient()
client.run(client.data['token'])