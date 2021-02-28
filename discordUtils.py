import numpy
import os 
import asyncio
import re

import pymongo
import discord

import dbUtils
import utils

data = utils.fileToJson('./data.json')

def serverSetup(bot, guild):
	if (dbUtils.getObjectByID(guild.id)) :
		return
	#Check if server is already contained/setup/updated
	data = {
		'_id': guild.id,
		'prefix': '>',
		'roleData': {},
		'stats': {},
	}
	dbUtils.setObject(data)

def stringifyUser(author):
	return author.display_name + '#' + str(author.discriminator) + '(' + str(author.id) + ')'

def userSetup(bot, user):
	return #Boop



	



def onGuildJoin(bot, guild):
	print("Join", guild.id)

def onGuildRemove(bot, guild):
	print("Remove", guild.id)

def onGuildAvailable(bot, guild):
	serverSetup(bot, guild)
	print("Available", guild.id)

def onGuildUnavailable(bot, guild):
	print("Unavailable", guild.id)