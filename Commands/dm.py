info = {
	'name': "Direct Message",
	'arguments': [("User", "The user or userID to DM"), ("Message", "The message to send the {user}.")],
	'aliases': ['message'],
	'summary': "Just a random command!",
	'hidden': True,
	'direct': False,
	'directOnly': False,
	'register': True,
}


async def command(self):
	print("Currently being worked on!!!")
	user = self.evaluateInteger(0) or self.evaluateMention(0)
	if user:
		user = self.getUser(user)
		if user:
			self.bot.DMUser(user, self.parsedArguments[1:])
