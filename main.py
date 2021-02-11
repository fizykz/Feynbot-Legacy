import numpy
import asyncio

import pymongo
import discord

import utils
import dbUtils
import discordUtils as dUtils


properties = utils.fileToJson("./properties.json")


class MyClient(discord.Client):
	admins = [
		395419912845393923, #Main
		802737417949151293, #Fizykz
		535697686532456448, #Alt
	]

	def __init__(self):
		#Construction

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

	def isAdmin(client, id):
		return id in client['admins']



	

client = MyClient()
client.run(properties['token'])