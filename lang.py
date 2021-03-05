import re

def diagnosticMessage(*args, **kwargs):
	return

def englishRestart(end, start):
	return

languages = {
	'english': {
		'onReady': [
			"Logged on and ready.",
			"Please type the administrative PIN.",
			"Safelocking the bot after an incorrect PIN attempt.",
			"You can now delete your PIN from this channel.\nPlease type the random 2FA SMS just sent to your phone number.",
			"Here is your 2FA SMS key: ",
			"An error occured while sending the SMS.",
			"An error occured with an SMS while undergoing {}unlock, the bot has safelocked as a precaution.",
			"The bot has been unlocked and code execution will be available until end of session or a safelock.",
			"Safelocking the bot after an incorrect SMS Key attempt.",
			"Safelocking the bot after a timeout of {}unlock.",
			"Safelocking the bot after a startup cooldown."
		],
		'diagnosticMessage': diagnosticMessage,
		'restart': englishRestart,
	}
}

def getContent(collection, *args, language = 'english', **kwargs):
	assert language in language, "The specified language '" + str(language) + "' was not found."
	assert collection in languages[language], "The specfiied collection '" + str(collection) + "' was not found."
	target = languages[language][collection]
	if (callable(target)):
		return languages[language][collection](*args, **kwargs)
	else:
		return languages[language][collection]
