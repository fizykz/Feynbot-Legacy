import numpy
import asyncio

import pymongo
import discord

import utils
import dbUtils
import discordUtils as dUtils


class MyClient(discord.Client):
	def __init__(self):
		super().__init__()
		self.commands = []
		self.overrides = []
		self.data = utils.fileToJson('./data.json')
		self.admins = self.data['admins']
		self.settings = {
			'verbose': True, 
			'overrideDiagnostics' : True
		}	

	def refreshCommands(self):
		return #Iterate over folders, find modules, import.

	def getCommand(self, id, command):
		return #if overrides[id][command], else return commands[command] if plausible

	def isAdmin(self, id):
		return id in client['admins']

	def log(self, message, necessary, sendToDiagnostics):
		if (not (not self.settings['verbose'] and not necessary)):   #Send all messages except verbose ones when verbose messaging is off.
			print(message)
			if sendToDiagnostics or settings['overrideDiagnostics']:
				return #Send to channel

	def alert(self, message, sendToDiagnostics, major):
		return 1 #Insert here


	def serverSetup(self, guild):
		#Check if server is already contained/setup/updated
		print(self, guild.id)
		data = {
			'_id': guild.id,
			'prefix': '>',
			'roleData': {},
			'stats': {},
		}
		dbUtils.setDiscordObject(data)

	def userSetup(self, user):
		#Boop


	async def on_ready(self):					#Bot ready to make API commands and is recieving events.
		dUtils.onReady(client)

	async def on_message(self, message):		#Message recieved: (self, message)
		dUtils.onMessage(client, message)

	async def on_guild_remove(self, guild):
		dUtils.onGuildRemove(client, guild)

	async def on_guild_join(self, guild):
		dUtils.serverSetup(client, guild)

	async def on_guild_available(self, guild):
		dUtils.serverSetup(client, guild)
		dUtils.onGuildAvailable(client, guild)

	async def on_guild_unavailable(self, guild):
		dUtils.onGuildUnavailable(client, guild)





	

client = MyClient()
client.run(properties['token'])