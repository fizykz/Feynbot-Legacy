import numpy
import os 
import asyncio

import pymongo
import discord

import dbUtils
import utils

data = utils.fileToJson('./data.json')

def serverSetup(bot, guild):
	if (dbUtils.getObject(guild.id)) :
		return
	#Check if server is already contained/setup/updated
	data = {
		'_id': guild.id,
		'prefix': '>',
		'roleData': {},
		'stats': {},
	}
	dbUtils.setObject(data)

def userSetup(bot, user):
	return #Boop





def onReady(bot):
	bot.log("Logged on and ready.", False, True)
	bot.reloadCommands()

def onMessage(bot, message):
	#Parse message 
	#Find command module, (Might be overridden)
	#Execute module function
	#Check if bot/exception/excluded or permissions are missing.
	#Check if command (Server prefix/global prefix)
	#Pass message/bot to command module.
	if (message.content.startswith('<@!806400496905748571> ') or message.content.startswith('<@806400496905748571> ') or message.content.lower().startswith('@feynbot ')):
		bot.reloadCommands()
		bot.log("@ Command: " + message.content)

def onGuildJoin(bot, guild):
	print("Join", guild.id)

def onGuildRemove(bot, guild):
	print("Remove", guild.id)

def onGuildAvailable(bot, guild):
	serverSetup(bot, guild)
	print("Available", guild.id)

def onGuildUnavailable(bot, guild):
	print("Unavailable", guild.id)