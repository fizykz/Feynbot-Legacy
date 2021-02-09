import json 
import numpy
import os 
import asyncio

import pymongo
import discord

import utils

properties = utils.fileToJson("./properties.json")

dbClient = pymongo.MongoClient('localhost', 27017)
db = dbClient[properties['database']['name']]
discordObjects = db['discordObjects']

def setDiscordObject(data):
	discordObjects.insert_one(data)