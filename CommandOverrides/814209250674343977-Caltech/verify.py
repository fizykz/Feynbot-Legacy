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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from validate_email import validate_email_or_fail

info = {
	'name': "Caltech Email Verify",
	'aliases': ['verifyemail'],
	'arguments': [("CaltechEmail", "Your email in the form `Username@Caltech.edu`.")],
	'summary': "Prompts an email verification for Caltech members.",
	'init': True,
	'hidden': False,
}

State = {
	'emailConnection': None, 
	'feynbotEmail': None, 
	'feynbotPassword': None, 
}

def init(bot):		#This all seriously needs to be redone.  Ideally email code should be seperate from verify.py alltogether and all verify does is use a library to tell it what to send exactly.
	State['feynbotEmail'] = bot.state.credentials.email['email']
	State['feynbotPassword'] = bot.state.credentials.email['password']
	try:
		State['emailConnection'] = smtplib.SMTP(host = 'smtp.gmail.com', port = 587)
		State['emailConnection'].ehlo()
		State['emailConnection'].starttls()
		State['emailConnection'].login(State['feynbotEmail'], State['feynbotPassword'])
	except Exception as error:
		print(error)

def sendEmail(emailaddress):
	content = MIMEMultipart()
	content['From'] = State['feynbotEmail']
	content['To'] = emailaddress 
	content['Subject'] = "Feynbot Email Verification"

	content.attach(MIMEText("""
		Greetings!  

		I have come surfing across the web and quantum waves to give you this email verification link!
		If you think this is a mistake please contact thomas@caltech.edu.

		-Feynbot, a Discord bot
		"""))

	try:
		State['emailConnection'].send_message(content)
	except Exception as error:
		print(error)

def validEmail(string):
	if string and isinstance(string, str) and string.endswith('@caltech.edu'):
		return not (validate_email_or_fail(email_address = string, check_smtp = False) == False)

async def command(interface):
	email = None 
	if interface.getArgumentLength() == 1 and validEmail(interface.getArgument(0)):
		interface.reply("Attempting to email you now!")
		email = interface.getArgument(0)
	elif interface.getArgumentLength() == 0:
		interface.reply("Please type your Caltech email.")
		interface2 = await interface.prompt(DMs = True, checkFunction = lambda x: x.getPartLength() == 1 and validEmail(x.getPart(0)))
		if interface2:
			interface2.reply("Attempting to email you now!")
			email = interface.getPart(0)
		else:
			interface.replyTimedOut("You didn't seem to enter a valid Caltech email and I timed out.")
			return 
	elif interface.getArgumentLength() != 1:
		interface.notifyFailure()
		interface.replyInvalid("This doesn't seem to be a valid Caltech email.  Make sure you're only sending one argument.")
		return 
	else:
		interface.notifyFailure()
		interface.replyInvalid("This doesn't seem to be a valid Caltech email.")
		return 
	sendEmail(email)