import numpy
import os 
import asyncio

import pymongo
import discord

import dbUtils
import utils
def sendMessage():
	#Insert here
def log(sendToDiagnostics):
	#Insert here

def alert(sendToDiagnostics, major):
	#Insert here

def onReady(client):
	print("Client ready.")

def onMessage(client, message):
	print(message.content)
	#Parse message
	#Find command module, (Might be overridden)
	#Execute module function

def serverSetup(client, guild):
	#Check if server 
	print(client, guild.id)
	data = {
		"_id": guild.id,
	}
	dbUtils.setDiscordObject(data)

def onGuildRemove(client, guild):
	print("Remove", guild.id)

def onGuildAvailable(client, guild):
	print("Available", guild.id)

def onGuildUnavailable(client, guild):
	print("Unavailable", guild.id)