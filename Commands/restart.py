#info = {
#	'arguments': [],	
#	'summary': ""
#}
#async def command(interface):
#	pass
#
#
import numpy

info = {
	'name': "Restart",
	'arguments': [("endDelay", "Delay between the command and the bot shutting down."), ("startDelay", "Delay between the bot shutting down and starting back up.")],
	'summary': "Restarts the bot; `>cancel` or similar can be used to cancel if there was a large enough delay.",
	'hidden': True
}

async def command(interface):
	if (interface.isAdmin()):
		endDelayStatement, start1DelayStatement, start2DelayStatement = None, None, None

		endDelay = interface.evaluateInteger(0) or 0
		startDelay = interface.evaluateInteger(1) or 0
		
		if (endDelay < 5):
			endDelayStatement = interface.bot.getBotEmoji('acceptedStatic') + " Closing bot program immediately.  "
		else:
			endDelayStatement = interface.bot.getBotEmoji('loading') + " Closing bot program in {} second{}.  ".format(endDelay, interface.utils.isPlural(endDelay))

		if (startDelay < 5):
			start1DelayStatement = "immediately after."
			start2DelayStatement = "immediately."
		else:
			start1DelayStatement = "in {} second{}.".format(startDelay + endDelay, interface.utils.isPlural(endDelay))
			start2DelayStatement = "in {} second{}.".format(startDelay, interface.utils.isPlural(endDelay))

		interface.alert(f"Restart ordered by {interface.stringifyUser()}, closing " + endDelayStatement + "Then restarting " + start1DelayStatement, True)
		message = await interface.reply(endDelayStatement + "Then restarting program " + start1DelayStatement)
		interface.notifySuccess()
		editTask = interface.delayEdit(message, numpy.clip(endDelay - 6, 0, endDelay), content = interface.bot.getBotEmoji('acceptedStatic') + f" Closing bot program.  " + "Restarting program " + start2DelayStatement)
		canceller = await interface.bot.restart(endDelay, startDelay)
		if (canceller):
			editTask.cancel()
			interface.alert(f"Restart cancelled by {interface.bot.stringifyUser(canceller)}.", True)
			await message.edit(content = interface.bot.getBotEmoji('deniedStatic') + f" Restart was cancelled by {interface.bot.stringifyUser(canceller)}.")

