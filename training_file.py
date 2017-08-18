## This file manages the text storage of the markovbot.
##
import sqlite3


def create_tables(connection):
	## Database metadata table
	# This table is meant to store at least one row of any number of columns
	# There is no guarantee the data will be in a sane or consistent state, but the program
	# itself should not be the cause of this.
	connection.execute("CREATE TABLE db (version INTEGER NOT NULL)")

	## Recorded messages
	# What the markov chain algorithm uses to create its chains.
	# Should not store duplicates, but keep a log of how often it has seen a message
	connection.execute("CREATE TABLE messages (message TEXT NOT NULL, seen INTEGER)")

	## Recorded responses
	# Contains generated chains the markov bot has spoken, and what the original message was in response to
	connection.execute("CREATE TABLE responses (message_id REFERENCES messages(rowid), response TEXT NOT NULL, seen INTEGER)")

	## User voting on recorded responses
	# TODO
	connection.execute("CREATE TABLE response_votes (response_id REFERENCES responses(rowid), user TEXT UNIQUE NOT NULL, tally INTEGER)")
	connection.commit()

def set_version(connection, version):
	connection.execute("INSERT INTO db (?)", version)
	connection.commit()


def add_message(connection, message):
	'''
	Add a message to the db or increment its counter if it already exists
	'''
	cursor = connection.execute("SELECT rowid, seen FROM messages WHERE message = ?", message)
	
	if cursor.rowcount > 0:
		# Increase the counter for a message that already exists
		row = cursor.fetchone()
		connection.execute("UPDATE messages SET seen = ? WHERE rowid = ?", (row[1], row[0]))
	else:
		# Add a new message
		connection.execute("INSERT INTO messages (?, ?)", [(message, 0)])
	connection.commit()

	
def get_messages(connection, word):
	'''
	Get all messages containing a word.
	'''
	cursor = connection.execute("SELECT message FROM messages WHERE message LIKE ?", word)
	
	# make an easier to use list from the cursor
	row = cursor.fetchone()
	messages = []
	while row != None:
		messages.append(row[0])

	return messages

	
def add_response(connection, message, response):
	'''
	Add something the bot said to the database, tying it to the message it is responding to.
	'''
	cursor = connection.execute("SELECT rowid FROM messages WHERE message = ?", message)
	if cursor.rowcount > 0:
		row = cursor.fetchone()
		cursor2 = connection.execute("SELECT rowid, seen FROM responses WHERE response = ?", response)
		if cursor2.rowcount > 0:
			row2 = cursor.fetchone()
			connection.execute("UPDATE responses SET seen = ? WHERE ", row2[1] + 1)
		else:
			connection.execute("INSERT INTO responses (?, ?, ?)", row[0], response, 0)
	connection.commit()


if __name__ == "__main__":
	# convert training file to sql
	import os.path
	if not path.exists("training_file.txt"):
		print("No training file to convert.  If you did not intend to convert training_file.txt to sqlite database, please run \"markovbot.py\" instead.")
	else
		print("Converting training_file.txt to sqlite database...")
		with file = open("training_file.txt"):
			# convert text to sqlite
			connection = connect()
			create_tables_1(connection)
			

			connection.close()
