import json 
import numpy
import os 
import asyncio
import inspect
import re
import smtplib
import random

import pymongo
import discord

def fileToJson(path):
	"""Converts a JSON file and returns the table"""
	jsonObj = None
	with open(path, 'r') as file:
		jsonObj = json.load(file)
	return jsonObj

privateData = fileToJson('./private.json')

class TaskQueue():
	def __init__(self):
		self.tasks = []

	def addTask(self, function, *args):
		task = None
		if (inspect.iscoroutinefunction(function)):		#Is this function when called a coroutine?
			task = asyncio.create_task(function(*args))
		else:
			async def cofunction():					#Have the function be wrapped in an asynchronus function to make it return a coroutine.
				return function(*args)
			task = asyncio.create_task(cofunction())
		self.tasks.append(task)

	async def __call__(self):
		for i in range(len(self.tasks)):
			self.tasks[i] = await self.tasks[i]		#Wait for each task to complete and store what it returns instead.

def resolveBooleanPrompt(string):
	string = string.lower()
	#string = re.sub(r' .*', ' ', string) #What the fuck was I writing?????
	#string = re.sub(r'[^A-Za-z0-9 ]', '', string)
	if (not string.isalnum()):
		return None 
		
	accepted = re.match(r'y[a-z]*\s*$', string) or re.search(r'enabl[a-z]*\s*$', string) or re.search(r'true\s*$', string) or re.search(r'on\s*$', string) or re.search(r't\s*$', string)
	denied = re.match(r'n[a-z]*\s*$', string) or re.search(r'disabl[a-z]*\s*$', string) or re.search(r'false\s*$', string) or re.search(r'off\s*$', string) or re.search(r'f\s*$', string)

	if (accepted and denied):
		return None
	elif (accepted):
		return True
	elif (denied):
		return False
	return None

def getRangeList(*args):
	return list(range(*args))

def getRandomString(length):
	characters = getRangeList(65, 91) + getRangeList(97, 123)
	string = ''
	for I in range(length):
		string = string + chr(random.choice(characters))
	return string 

def substringIfStartsWith(string, substring):
	if string.startswith(substring):
		return string[len(substring):]
	return None

def isPlural(number):
	if (number == 1):
		return ''
	return 's'

def isVerbPlural(number):
	if (number == 1):
		return 's'
	return ''

def formatPhoneNumber(number):
	assert (int(number) == number and 0 <= number <= 9999999999), "Should be an integer between 0 and 9999999999."
	number = str(number) 
	number = number[:3] + '-' + number[3:6] + '-' + number[6:]
	return number

def updateOverIterable(iterable, function):
	if (isinstance(iterable, collections.abc.Mapping)):
		for index in iterable.keys():
			iterable[index] = function(iterable[index])
	elif (isinstance(iterable), list):
		for index in range(len(list)):
			iterable[index] = function(iterable[index])
	else:
		raise TypeError("An iterable was given that wasn't a dictionary nor an array.")

