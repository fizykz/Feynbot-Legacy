import json 
import numpy
import os 
import asyncio
import inspect
import re

import pymongo
import discord


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
	string = re.sub(r' .*', ' ', string)
	string = re.sub(r'[^A-Za-z0-9 ]', '', string)

	accepted = re.match(r'y[a-z]*\s*$', string) or re.search(r'enabl[a-z]*\s*$', string) or re.search(r'true\s*$', string) or re.search(r'on\s*$', string) or re.search(r't\s*$', string)
	denied = re.match(r'n[a-z]*\s*$', string) or re.search(r'disabl[a-z]*\s*$', string) or re.search(r'false\s*$', string) or re.search(r'off\s*$', string) or re.search(r'f\s*$', string)
	
	if (accepted and denied):
		return None
	elif (accepted):
		return True
	elif (denied):
		return False
	return None

def fileToJson(path):
	"""Converts a JSON file and returns the table"""
	jsonObj = None
	with open(path, 'r') as file:
		jsonObj = json.load(file)
	return jsonObj

def functionize(coroutine):
	function = None 
	if (inspect.iscoroutinefunction(coroutine)):
		def function(*args):
			return asyncio.create_task(coroutine(*args))
	else:
		return coroutine
	return function 

def stringifyUser(author):
	return author.display_name + '#' + str(author.discriminator) + '(' + str(author.id) + ')'