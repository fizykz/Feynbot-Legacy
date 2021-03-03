async def command(cmd):
	if (cmd.isAdmin()):
		cmd.notifySuccess()
		cmd.alert(f"Reload ordered by {cmd.getFullUsername()}.", True)
		cmd.bot.reloadCommands()
		cmd.bot.reloadEvents()
		cmd.bot.reloadLibraries()

info = {
	'name': "Reload",
	'arguments': [],
	'summary': "Reloads all commands.",
	'hidden': True
}