import json 
import numpy
import os 
import asyncio

import pymongo
import discord

import utils

data = utils.fileToJson("./data.json")

dbClient = pymongo.MongoClient('localhost', 27017)
db = dbClient[data['database']['name']]
discordObjects = db['discordObjects']

def setObject(data):
	discordObjects.insert_one(data)

def getObject(ID, forceOverride=False):
	return discordObjects.find_one({"_id": ID})