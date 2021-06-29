info = {
	'name': "Submit",
	'arguments': [],
	'aliases': [],
	'summary': "Allows you to submit a video for the S&T Contest.",
	'hidden': True,
	'direct': True,
	'directOnly': True,
	'register': True,
}

state = {}

async def command(self):
	
	attachments = self.message.attachments
	urls = []
	for attachment in attachments:
		urls.append(attachment.url)
	urls = ('\n').join(urls)
	channel = (await self.bot.getChannels(858776085780234271))[0]
	self.bot.send(channel, f"<@!{self.user.id}\\>:\n{(' '.join(self.parsedArguments[0:]))} \n{urls}")
	self.reply("")
	if len(urls) == 0:
		self.reply("I've submitted your message!  Did you mean to attach something though?  If not you're done!\nRemember though not to delete any linked files, otherwise your submission may become invalid.")
	else:
		self.reply("I've submitted your attachments & message!\nRemember to not delete any linked files, otherwise your submission may become invalid.")