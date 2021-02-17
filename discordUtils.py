import numpy
import os 
import asyncio

import pymongo
import discord

import dbUtils
import utils

properties = utils.fileToJson("./properties.json")



def sendMessage():
	#Check if bot/exception/exclused
	#Check if command (Server prefix/global prefix)
	#Pass message/bot to command module.

def onReady(bot):
	bot.log("Logged on and ready.", True, True)

def onMessage(bot, message):
	print(message.content)
	#Parse message
	#Find command module, (Might be overridden)
	#Execute module function

def onGuildRemove(bot, guild):
	print("Remove", guild.id)

def onGuildAvailable(bot, guild):
	print("Available", guild.id)

def onGuildUnavailable(bot, guild):
	print("Unavailable", guild.id)