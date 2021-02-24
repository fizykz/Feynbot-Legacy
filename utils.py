import json 
import numpy
import os 
import asyncio
import inspect

import pymongo
import discord


class TaskQueue():
	def __init__(self):
		self.tasks = []

	def addTask(self, function):
		task = None
		if (inspect.iscoroutinefunction(function)):		#Is this function when called a coroutine?
			task = asyncio.create_task(function())
		else:
			async def cofunction():					#Have the function be wrapped in an asynchronus function to make it return a coroutine.
				return function()
			task = asyncio.create_task(cofunction())
		self.tasks.append(task)

	async def __call__(self):
		for i in range(len(self.tasks)):
			self.tasks[i] = await self.tasks[i]		#Wait for each task to complete and store what it returns instead.


def fileToJson(path):
	"""Converts a JSON file and returns the table"""
	jsonObj = None
	with open(path, 'r') as file:
		jsonObj = json.load(file)
	return jsonObj

