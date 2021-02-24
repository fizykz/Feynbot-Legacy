import numpy
import os 
import asyncio

import pymongo
import discord

import dbUtils
import utils

data = utils.fileToJson('./data.json')



def sendMessage():
	#Check if bot/exception/exclused
	#Check if command (Server prefix/global prefix)
	#Pass message/bot to command module.
	return

def onReady(bot):
	bot.log("Logged on and ready.", True, True)

def onMessage(bot, message):
	bot.log("Message sent.")
	#Parse message
	#Find command module, (Might be overridden)
	#Execute module function

def onGuildJoin(bot, guild):
	print("Join", guild.id)

def onGuildRemove(bot, guild):
	print("Remove", guild.id)

def onGuildAvailable(bot, guild):
	bot.serverSetup(guild)
	print("Available", guild.id)

def onGuildUnavailable(bot, guild):
	print("Unavailable", guild.id)