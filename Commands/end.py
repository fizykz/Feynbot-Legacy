import numpy

async def command(cmd):
	if (cmd.isAdmin()):
		endDelayStatement = None

		endDelay = cmd.evaluateInteger(0) or 0
		
		if (endDelay < 5):
			endDelayStatement = cmd.bot.getFrequentEmoji('acceptedStatic') + " Closing bot program immediately."
		else:
			endDelayStatement = cmd.bot.getFrequentEmoji('loading') + " Closing bot program in {} second{}.  ".format(endDelay, cmd.utils.isPlural(endDelay))

		cmd.alert(f"Closure ordered by {cmd.getFullUsername()}, closing " + endDelayStatement, True)
		message = await cmd.reply(endDelayStatement)
		cmd.notifySuccess()
		editTask = cmd.delayEdit(message, numpy.clip(endDelay - 6, 0, endDelay), content = cmd.bot.getFrequentEmoji('acceptedStatic') + f" Closing bot program...")
		canceller = await cmd.bot.end(endDelay)
		if (canceller):
			editTask.cancel()
			cmd.alert(f"Closure cancelled by {cmd.bot.stringifyUser(canceller)}.", True)
			await message.edit(content = cmd.bot.getFrequentEmoji('deniedStatic') + f" Closure was cancelled by {cmd.bot.stringifyUser(canceller)}.")

info = {
	'name': "end",
	'aliases': ["close"],
	'arguments': [("endDelay", "Delay between the command and the bot shutting down.")],
	'summary': "Ends the program; `>cancel` or similar can be used to cancel if there was a large enough delay."
}