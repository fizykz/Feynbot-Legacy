#def command(bot, message, taskQueue, guildData=None):
#	return #whatever
#
#help = {
#	'arguments': [],	
#	'summary': ""
#}
#
import re
import asyncio

info = {
	'name': "Execute",
	'arguments': [],
	'aliases': ["exec"],
	'summary': "Executes a code block, a collection of globals [`bot`, `guild`, `channel`, `author`] are passed as well.",
	'hidden': True
}

async def command(interface):
	if (interface.isOwner()):	#Make sure the messenger is the owner.
		run = 0
		ourMessage = None
		results = []

		def asyncExec(code, Globals = None):
			modifiedCode = ""
			Locals = {}
			for l in code.split('\n'):
				modifiedCode = modifiedCode + f"\n\t{l}"
			exec('async def executable():' + modifiedCode, Globals, Locals)
			return Locals['executable']

		def customPrint(*args):	#define a custom print for our user executed code
			args = [*args]
			for index in range(len(args)):
				args[index] = str(args[index])
			string = ('\t').join(args)	#collect what our bot printed when the custom print runs
			results.append(string)
			interface.log("EXECUTION: \t" + string, -1, True, title = ">Execute", color = 12779530)

		def checkFunction(reaction, reactingUser): #our function to check if the user wanted to repeat later on
			return str(reaction.emoji) == interface.getBotEmoji('repeat') and interface.user == reactingUser and reaction.message == interface.message

		while True:	#Main code loop (for repeat running the code)
			results = []
			run = run + 1
			code = re.search(r'```p?y?\n(.+)```', interface.message.content, flags=re.S)	#search for Python/no highlighted code.
			if (code):	#Check if anything was found.
				code = code.groups(1)[0] #Select the right capture group.
			else:	
				return 	#TODO Otherwise we got no code, this'll need to be done later to have a message or prompt a file or something
			while (re.search(r'^\s{2}  ', code, flags=re.M)):	#Loop when there's still spaces instead of tabs.
				code = re.sub(r'^(\s*)[ ]{2}', r'\t\1', code, flags=re.M) #Replace two spaces (Discord default) with actual htab chars.

			interface.log(f"Attempting to run code by {interface.stringifyUser()}.", -1, True, True) #Log the user running code (just in case, 'cause this shit is important)
			try: #Catch an error if the code fails.
				await asyncExec(code, {	#Execute the code, passing in some Discord objects.
					"bot": interface.bot,
					"guild": interface.guild,
					"channel": interface.channel,
					"author": interface.user,
					"message": interface.message,
					"interface": interface,
					"print": customPrint,
				})()

			except Exception as error:	#If we threw an error.
				interface.notifyFailure()
				interface.log("An error was raised when executing:  " + repr(error), True)	#Print the error and reject it.
				interface.reply("Run Attempt: " + str(run) + "\nAn error was raised when executing: \n````>>>\n" + str(error) + "\n```")	#Send a message of the error.
			else:	#code ran fine
				interface.notifySuccess()
				if (not ourMessage): #if we haven't already sent a message.
					ourMessage = interface.reply(content = "Run Attempt: " + str(run) + "\n```>>>\n" + ('\n').join(results) + "\n```")
				else:
					if asyncio.isfuture(ourMessage):
						ourMessage = await ourMessage
					await ourMessage.edit(content = "Run Attempt: " + str(run) + "\n```>>>\n" + ('\n').join(results) + "\n```")

			try:
				interface.promptRepeat()	#Ask user if we want to repeat.
				await interface.bot.wait_for('reaction_add', timeout=60, check=checkFunction)	#wait until user reacts or a timeout of a minute
			except asyncio.TimeoutError: 
				interface.unreactWith(interface.bot.getBotEmoji('repeat'))	
				return
			else:
				interface.unreactUserWith(interface.bot.getBotEmoji('repeat'))	
	else:
		interface.log(f"{interface.stringifyUser()} tried running execute.")
		interface.reply("Lol, imagine allowing anyone to run unsupervised code on my computer, nerd.")

