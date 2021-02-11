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

def setObject(data, forceOverride):
	discordObjects.insert_one(data)

def getObject(data, forceOverride):
	discordObjects.insert_one(data)