from collections import defaultdict
from twisted.internet import protocol, reactor, ssl
from twisted.words.protocols import irc
import sys, os, time, re, random

# blatantly copied from http://eflorenzano.com/blog/2008/11/17/writing-markov-chain-irc-bot-twisted-and-python/
# running on python 3.6.1
# accepts one command line argument that is the channel it will join and speak on
# replace ?? with values
# edit username and password in MomBotFactory if needed
# edit twisted/words/protocol/irc.py:2637 and change "line = line.decode('utf-8')" to "line = line.decode('ascii', 'ignore')" if it complains about utf-8 encodings from other chatters... unknown how to catch error yet
# "brain" state is saved at "./training_file.txt" and is '\n' delimited per privmsg

markov = defaultdict(list)
STOP_WORD = "\n"

def add_to_brain(msg, chain_length, write_to_file=False):
	# ignore banned words, especially if they're already written into the training_file
	for word in configuration['banned_words']:
		if msg.startswith(word):
			return
		
	if write_to_file:
		f = open('training_text.txt', 'a')
		f.write(msg + '\n')
		f.close()
	buf = [STOP_WORD] * chain_length
	for word in msg.split():
		markov[tuple(buf)].append(word)
		del buf[0]
		buf.append(word)
	markov[tuple(buf)].append(STOP_WORD)
	
	
def generate_sentence(msg, chain_length, max_words=10000):
	# use part of the msg as the seed for the response
	buf = msg.split()[:chain_length]

	if len(msg.split()) > chain_length:
		message = buf[:]
	else:
		# fill with random words from the brain if the buffer is too short
		message = []
		for i in range(chain_length):
			message.append(
				random.choice(
					markov[
						random.choice(
							list(markov.keys())
						)
					]
				)
			)

	# use buffer as a key to randomly pick words out of the "brain"
	# the newly chosen words will then be used to pick new words
	# once the STOP_WORD shows up, the algo is done
	for i in range(max_words):
		try:
			next_word = random.choice(markov[tuple(buf)])
		except IndexError:
			continue
		if next_word == STOP_WORD:
			break
		message.append(next_word)
		del buf[0]
		buf.append(next_word)
	return ' '.join(message).replace(STOP_WORD, "") #.replace to clean up errant stop_words that somehow made it into the message


class MomBot(irc.IRCClient):
	def _get_nickname(self):
		return self.factory.nickname
	def _get_username(self):
		return self.factory.username
	def _get_password(self):
		return self.factory.password
	nickname = property(_get_nickname)
	username = property(_get_username)
	password = property(_get_password)

	def signedOn(self):
		self.join(self.factory.channel)
		print ("Signed on as {0!s}.".format(self.nickname))

	def joined(self, channel):
		print ("Joined {0!s}.".format(channel))
		
	def privmsg(self, user, channel, msg):
		if not user:
			return
		if self.nickname in msg:
			# get rid of this bot's nick in the highlighted message
			msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('', msg)
			prefix = "{0!s}: ".format(user.split('!', 1)[0])
		else:
			prefix = ''
		
		# ignore other bot commands, if you do not want to respond to them
		#if msg.startswith("!"):
		#	return
			
		print ("Recording line from", user, "at", channel)
		add_to_brain(msg, self.factory.chain_length, write_to_file=True)
		

		if not configuration['reply_to_private'] and channel == self.nickname:
			return # TODO patch private messaging outside of #channels to work

		# get the stored data from our configuration
		can_speak = False
		chan_store = None

		for chan in channels:
			if chan.name == channel:
				chan_store = chan
				break

		if chan.can_speak:
			# respond to nick who highlighted this bot
			if prefix:
				print ("Speaking to", user, "at", channel)
				self.speak(prefix, user, channel, msg, chan_store.chain_length)

			# randomly chat if somebody spoke
			elif random.random() <= chan.chattiness:
				print ("Randomly chatting at", channel)
				new_msg = self.speak(prefix, user, channel, msg, chan_store.chain_length)


	def speak(self, prefix, user, channel, msg, chain_length):
		time.sleep(0.5)
		sentence = generate_sentence(msg, chain_length, self.factory.max_words)
		if sentence:
			self.msg(channel, prefix + sentence)
		return sentence # can be used to generate a new response
			

class MomBotFactory(protocol.ClientFactory):
	protocol = MomBot

	def __init__(self):
		#self.channels = channels
		self.nickname = configuration['nickname']
		self.altnick = configuration['altnick']
		self.realname = configuration['realname']
		self.username = configuration['username']
		self.password = configuration['password']
		self.chain_length = configuration['chain_length']
		self.chattiness = configuration['chattiness']
		self.max_words = 10000
		
		# use only if needed

	def clientConnectionLost(self, connector, reason):
		print ("!! Lost connection ({0!s}) !!".format(reason))
		print ("!! REASON:", reason.value, "!!")
		# connection lost isn't that bad, just try to reconnect
		print (">> Reconnecting in 5 seconds ...")
		time.sleep(5)
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print ("!! Could not connect: {0!s} !!".format(reason))
		print ("!! REASON:", reason.value, "!!")
		# done, exit.  no error handling for failed connections yet
		reactor.stop()
	

if os.path.exists('training_text.txt'):
	f = open('training_text.txt', 'r')
	for line in f:
		add_to_brain(line, 2)
	print ('Brain Reloaded')
	f.close()
# connect using ssl
if configuration['use_ssl']:
	reactor.connectSSL(configuration['irc_server'], configuration['port'], MomBotFactory(), ssl.ClientContextFactory())
	reactor.run()
# connect using not-ssl
else: 
	reactor.connectTCP(configuration['irc_server'], configuration['port'], MomBotFactory())
	reactor.run()

print (">> Exiting...")
