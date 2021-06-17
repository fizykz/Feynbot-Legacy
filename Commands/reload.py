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



async def command(interface):
	if (interface.isAdmin()):
		interface.notifySuccess()
		interface.log(f"Reload ordered by {interface.stringifyUser()}.", True)
		interface.bot.reloadAll()

info = {
	'name': "Reload",
	'arguments': [],
	'summary': "Reloads all commands.",
	'hidden': True
}