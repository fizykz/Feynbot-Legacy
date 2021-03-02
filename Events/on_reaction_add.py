def process(bot, reaction, user):
	return [reaction.message.channel.id, reaction.message.guild and reaction.message.guild.id or 0, user.id]


async def event(bot, reaction, user):
	if (user == bot.user):
		return 
	bot.addReaction(reaction.message, bot.getFrequentEmoji('accepted'))
	bot.alert(f"Reload ordered by reaction from {user}.", True)
	bot.reloadEvents()
	bot.reloadCommands()
	bot.reloadLibraries()
