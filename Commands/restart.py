#info = {
#	'name': "",
#	'aliases': [],
#	'arguments': [],	
#	'summary': "",
#	'hidden': True,
#}
#
#async def command(interface):
#	pass
#

import numpy

info = {
	'name': "Restart",
	'arguments': [("shutdownDelay", "Delay between the command and the bot shutting down."), ("startupDelay", "Delay between the bot shutting down and starting back up.")],
	'summary': "Restarts the bot; `>cancel` or similar can be used to cancel if there was a large enough delay.",
	'hidden': True
}

async def command(interface):
	if (interface.isAdmin()):
		shutdownDelay = interface.evaluateInteger(0) or 0
		startupDelay  = interface.evaluateInteger(1) or 0 
		if isinstance(shutdownDelay, Exception) or shutdownDelay < 0:
			interface.replyInvalid("Please make sure your first argument, `shutdownDelay`, is a positive number.")
			return
		elif isinstance(startupDelay, Exception) or startupDelay < 0:
			interface.replyInvalid("Please make sure your second argument, `startupDelay`, is a positive number.")
			return

		if shutdownDelay == 0:
			if startupDelay == 0:
				interface.reply(f"Restarting immediately!")
			else:
				interface.reply(f"Shutting down and restarting after a {startupDelay} pause!")
		else:
			if startupDelay == 0:
				interface.reply(f"Restarting in {shutdownDelay} second{interface.utils.isPlural(shutdownDelay)}!")
			else:
				interface.reply(f"Shutting down in {shutdownDelay} second{interface.utils.isPlural(shutdownDelay)} and rebooting after a {startupDelay} second delay.")

		await interface.notifySuccess()
		await interface.bot.restart(shutdownDelay , startupDelay)