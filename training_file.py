## This file manages the text storage of the markovbot.
##
import sqlite3


def create_tables(connection):
	connection.execute("CREATE TABLE db (version INTEGER NOT NULL)")
	connection.execute("CREATE TABLE messages (message TEXT NOT NULL, seen INTEGER)")
	connection.execute("CREATE TABLE responses (message_id REFERENCES messages(rowid), response TEXT NOT NULL, seen INTEGER)")
	connection.execute("CREATE TABLE response_votes (response_id REFERENCES responses(rowid), user TEXT UNIQUE NOT NULL, vote INTEGER)")
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
			connection.execute("UPDATE responses SET seen = ? WHERE 
		else:
			connection.execute("INSERT INTO responses (?, ?, ?)")


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
