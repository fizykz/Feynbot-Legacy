import numpy
import os 
import asyncio
import re

import pymongo
import discord

import dbUtils
import utils

data = utils.fileToJson('./data.json')







#!!!!!!!!!!!!
def onGuildAvailable(bot, guild):
	serverSetup(bot, guild)
	print("Available", guild.id)

