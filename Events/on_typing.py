#The name of this file needs to match the event you're trying to match on the Discord.py API reference.

def process(self, channel, user, when): #needs to be named process.
	#Needs to return an array which provides an order of IDs to check for overrides, first ID has priority.  
	#So if you returned the channel ID followed by the guild ID, if the channel had an override, it'd run instead of the guild override, or the general command one.
	return [user.id, channel.id]


async def event(self, channel, user, when):	#Needs to be named event, but is called by the same arguments that are passed to the Discord.py API reference.
	if isinstance(channel, self.discord.abc.PrivateChannel):
		pass #interface = self.interface(self, channel, None)
	else:
		pass #guild typing.
	
