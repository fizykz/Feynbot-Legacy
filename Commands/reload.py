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
		interface.log(f"Reload issued by {interface.stringifyUser()}.", -1, True, color = 16744202, title = 'Reloading Libraries')
		interface.bot.reloadAll()
		interface.notifySuccess()

info = {
	'name': "Reload",
	'arguments': [],
	'summary': "Reloads all commands.",
	'hidden': True
}