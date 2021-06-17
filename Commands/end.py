import numpy

async def command(interface):
	if (interface.isAdmin()):
		endDelayStatement = None

		endDelay = interface.evaluateInteger(0) or 0
		
		if (endDelay < 5):
			endDelayStatement = interface.bot.getFrequentEmoji('acceptedStatic') + " Closing bot program immediately."
		else:
			endDelayStatement = interface.bot.getFrequentEmoji('loading') + " Closing bot program in {} second{}.  ".format(endDelay, interface.utils.isPlural(endDelay))

		interface.alert(f"Closure ordered by {interface.getFullUsername()}, closing " + endDelayStatement, True)
		message = await interface.reply(endDelayStatement)
		interface.notifySuccess()
		editTask = interface.delayEdit(message, numpy.clip(endDelay - 6, 0, endDelay), content = interface.bot.getFrequentEmoji('acceptedStatic') + f" Closing bot program...")
		canceller = await interface.bot.end(endDelay)
		if (canceller):
			editTask.cancel()
			interface.alert(f"Closure cancelled by {interface.bot.stringifyUser(canceller)}.", True)
			await message.edit(content = interface.bot.getFrequentEmoji('deniedStatic') + f" Closure was cancelled by {interface.bot.stringifyUser(canceller)}.")

info = {
	'name': "end",
	'aliases': ["close"],
	'arguments': [("endDelay", "Delay between the command and the bot shutting down.")],
	'summary': "Ends the program; `>cancel` or similar can be used to cancel if there was a large enough delay."
}