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

async def command(cmd):
	run = 0
	ourMessage = None
	results = []

	def customPrint(*args):	#define a custom print for our user executed code
		print("EXECUTION:", *args)
		args = [*args]
		for index in range(len(args)):
			args[index] = str(args[index])
		results.append(('\t').join(args))	#collect what our bot printed when the customprint runs

	def checkFunction(reaction, newUser): #our function to check if the user wanted to repeat later on
		return str(reaction.emoji) == cmd.bot.getFrequentEmoji('repeat') and cmd.user == newUser and reaction.message == cmd.message

	if (cmd.isOwner()):	#Make sure the messenger is the owner.
		if not (not cmd.bot.getSetting('safelock') and cmd.bot.getSetting('livingCode')):	#Make sure we're allowing code to run.
			cmd.bot.safelock()	#If we aren't safelock the bot because WE should be knowing better.
			cmd.notifyFailure()
			cmd.reply("Executing code has been disabled.")
			return 
		
		while True:	#Main code loop (for repeat running the code)
			results = []
			run = run + 1
			code = re.search(r'```p?y?\n(.+)```', cmd.message.content, flags=re.S)	#search for Python/no highlighted code.
			if (code):	#Check if anything was found.
				code = code.groups(1)[0] #Select the right capture group.
			else:	
				return 	#TODO Otherwise we got no code, this'll need to be done later to have a message or prompt a file or something
			while (re.search(r'^\s{2}  ', code, flags=re.M)):	#Loop when there's still spaces instead of tabs.
				code = re.sub(r'^(\s*)[ ]{2}', r'\t\1', code, flags=re.M) #Replace two spaces (Discord default) with actual htab chars.

			cmd.alert(f"Attempting to run code by {cmd.getFullUsername()}.", True) #Log the user running code (just in case, 'cause this shit is important)
			try: #Catch an error if the code fails.
				program = compile(code, 'userInput', 'exec')	#compile to code object.
				exec(program, {	#Execute the code, passing in some Discord objects.
					"bot": cmd.bot,
					"guild": cmd.guild,
					"channel": cmd.channel,
					"author": cmd.user,
					"message": cmd.message,
					"commands": cmd.bot.commands,
					"print": customPrint,
					"commandInstance": cmd
				}, {})
			except Exception as error:	#If we threw an error.
				cmd.notifyFailure()
				cmd.alert("An error was raised when executing:  " + str(error), True)	#Print the error and reject it.
				cmd.reply("Run Attempt: " + str(run) + "\nAn error was raised when executing: \n````>>>\n" + str(error) + "\n```")	#Send a message of the error.
			else:	#code ran fine
				cmd.notifySuccess()
				if (not ourMessage): #if we haven't already sent a message.
					ourMessage = cmd.reply(content = "Run Attempt: " + str(run) + "\n```>>>\n" + ('\n').join(results) + "\n```")
				else:
					if asyncio.isfuture(ourMessage):
						ourMessage = await ourMessage
					cmd.bot.editMessage(ourMessage, content = "Run Attempt: " + str(run) + "\n```>>>\n" + ('\n').join(results) + "\n```")

			try:
				cmd.promptRepeat()	#Ask user if we want to repeat.
				await cmd.bot.wait_for('reaction_add', timeout=60.0, check=checkFunction)	#wait until user reacts or a timeout of a minute
			except asyncio.TimeoutError as error:
				cmd.bot.removeReaction(cmd.message, cmd.bot.getFrequentEmoji('repeat'))	#remove the reaction if they didn't
				return
			else:
				cmd.bot.removeReaction(cmd.message, cmd.bot.getFrequentEmoji('repeat'), cmd.user)	#remove their reaction (might error from no permission.)

info = {
	'name': "Execute",
	'arguments': [],
	'aliases': ["exec"],
	'summary': "Executes a code block, a collection of globals [`bot`, `guild`, `channel`, `author`] are passed as well.",
	'hidden': True
}