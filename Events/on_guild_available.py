def process(bot, guild):
	return [message.guild.id]


async def event(bot, guild):
	bot.serverSetup(guild)
	bot.log(guild.name + " now available")