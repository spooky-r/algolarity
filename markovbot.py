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

default_channel = ??
irc_server = ??
port = ??
use_ssl = True
nick = ??
chain_length = 2 # 2 seems to give the right kind of markov weirdness without making too little sense
chattiness = 0.15 # how often the bot should randomly speak when others speak, 0 - 1

markov = defaultdict(list)
STOP_WORD = "\n"


def add_to_brain(msg, chain_length, write_to_file=False):
	# ignore other bot commands
	if msg.startswith("!"):
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
	def _get_channel(self):
		return self.factory.channel
	nickname = property(_get_nickname)
	username = property(_get_username)
	password = property(_get_password)
	allowed_channel = property(_get_channel)

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
		
		if channel == self.allowed_channel:
			# respond to nick who highlighted this bot
			if prefix:
				print ("Speaking to", user, "at", channel)
				self.speak(prefix, user, channel, msg)

			# randomly chat if somebody spoke
			elif random.random() <= self.factory.chattiness:
				print ("Randomly chatting at", channel)
				new_msg = self.speak(prefix, user, channel, msg)
					
	def speak(self, prefix, user, channel, msg):
		time.sleep(0.5)
		sentence = generate_sentence(msg, self.factory.chain_length, self.factory.max_words)
		if sentence:
			self.msg(self.factory.channel, prefix + sentence)
		return sentence # can be used to generate a new response
			

class MomBotFactory(protocol.ClientFactory):
	protocol = MomBot

	def __init__(self, channel, nickname='bot', chain_length=3,
		chattiness=1.0, max_words=10000):
		self.channel = channel
		self.nickname = nickname
		self.chain_length = chain_length 
		self.chattiness = chattiness
		self.max_words = max_words
		
		# use only if needed
		#self.username = 
		#self.password = 

	def clientConnectionLost(self, connector, reason):
		print ("Lost connection ({0!s}), reconnecting.".format(reason))
		print("BAD:", reason.value)
		time.sleep(5)
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print ("Could not connect: {0!s}".format(reason))
		print("BAD:", reason.value)
	
	
try:
	chan = sys.argv[1]
except IndexError:
	chan = default_channel
	print ("Running default channel:", chan)

if os.path.exists('training_text.txt'):
	f = open('training_text.txt', 'r')
	for line in f:
		add_to_brain(line, 2)
	print ('Brain Reloaded')
	f.close()
# connect using ssl
if use_ssl:
	reactor.connectSSL(irc_server, port, MomBotFactory('#' + chan,
			nick, chain_length, chattiness=chattiness), ssl.ClientContextFactory())
	reactor.run()
# connect using not-ssl
else: 
	reactor.connectTCP(irc_server, port, MomBotFactory('#' + chan,
			nick, chain_length, chattiness=chattiness))
		reactor.run()
