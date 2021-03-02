import json 
import numpy
import os 
import asyncio

import pymongo
import discord

import utils

DBData = utils.fileToJson("./private.json")

dbClient = pymongo.MongoClient(DBData['database']['location'], DBData['database']['port'])
db = dbClient[DBData['database']['name']]
discordObjects = db['discordObjects']

def setObject(data):
	return discordObjects.insert_one(data)

def getObject(attribute, value, forceOverride=False):
	return discordObjects.find_one({attribute: value})

def getObjectByID(ID, forceOverride = False):
	return getObject('_id', ID, forceOverride)