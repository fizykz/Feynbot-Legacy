import numpy

async def command(cmd):
	if (cmd.isAdmin()):
		endDelayStatement, start1DelayStatement, start2DelayStatement = None, None, None

		endDelay = cmd.evaluateInteger(0) or 0
		startDelay = cmd.evaluateInteger(1) or 0
		
		if (endDelay < 5):
			endDelayStatement = cmd.bot.getFrequentEmoji('acceptedStatic') + " Closing bot program immediately.  "
		else:
			endDelayStatement = cmd.bot.getFrequentEmoji('loading') + " Closing bot program in {} second{}.  ".format(endDelay, cmd.utils.isPlural(endDelay))

		if (startDelay < 5):
			start1DelayStatement = "immediately after."
			start2DelayStatement = "immediately."
		else:
			start1DelayStatement = "in {} second{}.".format(startDelay + endDelay, cmd.utils.isPlural(endDelay))
			start2DelayStatement = "in {} second{}.".format(startDelay, cmd.utils.isPlural(endDelay))

		cmd.alert(f"Restart ordered by {cmd.getFullUsername()}, closing " + endDelayStatement + "Then restarting " + start1DelayStatement, True)
		message = await cmd.reply(endDelayStatement + "Then restarting program " + start1DelayStatement)
		cmd.notifySuccess()
		editTask = cmd.delayEdit(message, numpy.clip(endDelay - 6, 0, endDelay), content = cmd.bot.getFrequentEmoji('acceptedStatic') + f" Closing bot program.  " + "Restarting program " + start2DelayStatement)
		canceller = await cmd.bot.restart(endDelay, startDelay)
		if (canceller):
			editTask.cancel()
			cmd.alert(f"Restart cancelled by {cmd.bot.stringifyUser(canceller)}.", True)
			await message.edit(content = cmd.bot.getFrequentEmoji('deniedStatic') + f" Restart was cancelled by {cmd.bot.stringifyUser(canceller)}.")

info = {
	'name': "Restart",
	'arguments': [("endDelay", "Delay between the command and the bot shutting down."), ("startDelay", "Delay between the bot shutting down and starting back up.")],
	'summary': "Restarts the bot; `>cancel` or similar can be used to cancel if there was a large enough delay.",
	'hidden': True
}