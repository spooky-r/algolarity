## This file handles loading, verification, and storage of configuration options for the markovbot.
##
from configparser import ConfigParser

def str_to_bool(str):
	if str == "True":
		return True
	elif str == "False":
		return False
	raise ValueError("Cannot convert to bool: string is not \"True\" or \"False\".")


def load_configuration():
	# Bitch if there isn't a configuraiton file.
	# Produce an example file that must be edited and exit
	if os.path.exists('config.ini') == False:
		config_example = """# Edit this.  Replace ??'s with real values, and patch it up as you need it

[IRC]
server = ??
port = 6667
# make sure you use the right port
use_ssl = False
nickname = bot
altnick = bot_
realname = markov
# also known as ident
username = bot
# fill in only if needed
password =
# respond to somebody who chatted directly
reply_to_private = False

[MARKOV]
# through the power of science, 2 is the magic number.  make sure this value is above 0.
chain_length = 2
# range is [0,1] chance of chatting when another nick sends a privmsg
chattiness = 0.1
# do not record messages starting with these characters, words, phrases, literals.  delimited by new line and tab
do_not_record = 
	!
	?
	/

[CHANNEL1]
# put a channel here.  need at least one channel for the bot to function.  do not prepend '#' to the channel name
name = ??
# can override default from [MARKOV]
chattiness = 0.0
# can override default from [MARKOV]
chain_length = 2
# false is default
can_speak = True

[CHANNEL2]
# more than one channel!
# make new channels with the same syntax incrementing each channel's number
# [CHANNEL3], [CHANNEL4], ...
name = ??
"""
		with open('config.ini', 'w') as configfile:
			configfile.write(config_example)

		print ("!! No config.ini found.  Writing an example configuration file. !!")
		print ("!! Edit the new config.ini. !!")
		print (">> Exiting...")
		exit()

	## read the configuration and load all its values
	#
	config = ConfigParser()

	config.read('config.ini')

	# Annoy the user that they forget to change a config option
	if config['IRC']['server'] == "??":
		print ("!! irc_server option under [IRC] in config.ini is two question marks.  Fix it !!")
		print (">> Exiting...")
		exit()


	for word in config['MARKOV']['do_not_record']:
		configuration['banned_words'].append(word)

	# get all the channels
	channels = []
	for section in config.sections():
		if section.startswith("CHANNEL"): # TODO enforce channel number suffixes... or not, it may not ever matter. maybe "CHANNEL <whatever the user desires>" is a good thing?
			channel = {}

			if 'can_speak' in section:
			channel['can_speak'] = str_to_bool(section['can_speak'])

			if 'chattiness' in section:
				channel['chattiness'] = float(section['chattiness'])

			if 'chain_length' in section:
				channel['chain_length'] = int(section['chain_length'])

			if not 'name' in section:
				print ("!! Need a channel name for section '", section_name, "' !!")
				print (">> Exiting")
				exit()

			self.name = "#" + str(section['name'])

			channels.append(channel)

			if __debug__:
				print ("can_speak:", channel['can_speak'])
				print ("chattiness:", channel['chattiness'])
				print ("chain_length:", channel['chain_length'])
				print ("name:", channel['name'])


	return {  # TODO bomb on bad values, do some input validation
		'irc_server': str(config['IRC']['server']),
		'port': int(config['IRC']['port']),
		'use_ssl': str_to_bool(config['IRC']['use_ssl']),
		'nickname': str(config['IRC']['nickname']),
		'altnick': str(config['IRC']['altnick']),
		'realname': str(config['IRC']['realname']),
		'username': str(config['IRC']['username']),
		'password': str(config['IRC']['password']),
		'reply_to_private': str_to_bool(config['IRC']['reply_to_private']),
		'chain_length': int(config['MARKOV']['chain_length']), # 2 seems to give the right kind of markov weirdness without making too little sense
		'chattiness': float(config['MARKOV']['chattiness']), # how often the bot should randomly speak when others speak, 0 - 1
		'banned_words': []
		'channels': {}
	}


