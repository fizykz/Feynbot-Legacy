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

info = {
	'name': "end",
	'aliases': ["close"],
	'arguments': [("endDelay", "Delay between the command and the bot shutting down.")],
	'summary': "Ends the program; `>cancel` or similar can be used to cancel such.",
	'hidden': True
}

import numpy

async def command(interface):
	if (interface.isAdmin()):
		shutdownDelay = interface.evaluateInteger(0) or 0
		if isinstance(shutdownDelay, Exception) or shutdownDelay < 0:
			interface.replyInvalid("Please make sure your first argument, `shutdownDelay`, is a positive number.")
			return
		interface.reply(f"Shutting down in {shutdownDelay} second(s).")
		await interface.notifySuccess()
		await interface.bot.end(shutdownDelay)

