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

async def command(bot, message, guildData=None):
	user = message.author
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
		return str(reaction.emoji) == bot.getFrequentEmoji('repeat') and user == newUser and reaction.message == message

	if (bot.isOwner(user.id)):	#Make sure the messenger is the owner.
		if not (not bot.settings['safelock'] and bot.settings['livingCode']):	#Make sure we're allowing code to run.
			bot.safelock()	#If we aren't safelock the bot because we should be knowing better.
			await bot.runConcurrently(#Message/react that no code was ran.
				bot.addReaction(message, bot.getFrequentEmoji('denied')),
				bot.sendMessage(message.channel, "Executing code has been disabled."),
				return_exceptions = True
			)
			return 
		
		while True:	#Main code loop (for repeat running the code)
			run = run + 1
			code = re.search(r'```p?y?\n(.+)```', message.content, flags=re.S)	#search for Python/no highlighted code.
			if (code):	#Check if anything was found.
				code = code.groups(1)[0] #Select the right capture group.
			else:	
				return 	#TODO Otherwise we got no code, this'll need to be done later to have a message or prompt a file or something
			while (re.search(r'^\s{2}  ', code, flags=re.M)):	#Loop when there's still spaces instead of tabs.
				code = re.sub(r'^(\s*)[ ]{2}', r'\t\1', code, flags=re.M) #Replace two spaces (Discord default) with actual htab chars.

			bot.alert(f"Attempting to run code by {bot.stringifyUser(user)}.", True) #Log the user running code (just in case, 'cause this shit is important)
			try: #Catch an error if the code fails.
				program = compile(code, 'userInput', 'exec')	#compile to code object.
				exec(program, {	#Execute the code, passing in some Discord objects.
					"bot": bot,
					"guild": message.guild,
					"channel": message.channel,
					"author": user,
					"message": message,
					"commands": bot.commands,
					"print": customPrint
				}, {})
			except Exception as error:	#If we threw an error.
				bot.addTask(message.add_reaction(bot.getFrequentEmoji('denied')))	
				bot.alert("An error was raised when executing:  " + str(error), True, error)	#Print the error and reject it.
				bot.sendMessage(message.channel, "Run Attempt: " + str(run) + "\nAn error was raised when executing: \n````>>>\n" + str(error) + "\n```")	#Send a message of the error.
			else:	#code ran fine
				bot.addReaction(message, bot.getFrequentEmoji('accepted'))
				if (not ourMessage): #if we haven't already sent a message.
					bot.sendMessage(message.channel, content = "Run Attempt: " + str(run) + "\n```>>>\n" + ('\n').join(results) + "\n```")
				else:
					#TODO check if ourMessage is a future???
					bot.editMessage(ourMessage, content = "Run Attempt: " + str(run) + "\n```>>>\n" + ('\n').join(results) + "\n```")

			try:
				bot.addReaction(message, bot.getFrequentEmoji('repeat'))	#Ask user if we want to repeat.
				await bot.wait_for('reaction_add', timeout=60.0, check=checkFunction)	#wait until user reacts or a timeout of a minute
			except asyncio.TimeoutError:
				bot.removeReaction(message, bot.getFrequentEmoji('repeat'))	#remove the reaction if they didn't
				return
			else:
				bot.removeReaction(message, bot.getFrequentEmoji('repeat'), user)	#remove their reaction (might error from no permission.)

help = {
	'arguments': [],
	'aliases': ["exec"],
	'summary': "Executes a code block, a collection of globals [`bot`, `guild`, `channel`, `author`] are passed as well.",
	'hidden': True
}