#!/usr/bin/python
"""
	The S.O.A.P. Shower Basin Client
	
	How it works:
	The client waits for users to scan their iButtons,
	and upon a successful scan queries the user's
	playlist in the SOAP Redis database. This playlist,
	which is a mere list of URLs, is then used in a spawn
	worker thread which iterates through the list making
	for each a system call to SoX--a CLI audio player.
	
	Such a system call blocks the thread, making it stupid
	simple to play a playlist. If the URL or audio data
	is bad, SoX returns immediately, effectively skipping
	the song.
	
	Another thread is used to handle debugging input.
	It simply waits for input and upon such an occasion
	simulates an iButton press.
	
	Dependencies:
	-SoX, CLI audio software
	-Redis-py Python Redis Client module
	-CSHLDAP and associated dependencies
	-Logger (included)
	
	
	
"""

print("Loading dependencies")
import redis
import serial
import logger
from os import system
import sys
from CSHLDAP import CSHLDAP
import thread

# The message logger.
print("Creating logger")
l = Logger(16)

# The debug local playlist.
localPlaylist = ['http://www.csh.rit.edu/~gman/soap/dbsrv-ashes-to-ashes.mp3', \
				'http://www.csh.rit.edu/~gman/soap/dbsrv-china-girl.mp3', \
				'http://www.csh.rit.edu/~gman/soap/dbsrv-what-in-the-world.mp3'];

# Whether or not audio is being played.
playing = False

# Whether or not to continue the debug input loop.
debug = True


# Redis server hostname and other parameters
redis_host = '120.0.0.7'
redis_port = 6379
redis_db = 0
redis_pw = 'shitty_password'

# Global Redis handle.
p.log("Creating Redis connection.")
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, pw=redis_pw)
if r == None:
	l.plog("Could not create Redis client.")
	input("Press any key to exit")
	sys.exit()

# LDAP credentials
ldap_username = 'username'
ldap_password = 'password'

# Global serial connection
p.log("Creating serial connection...")
ser = serial.Serial(port='/dev/ttyUSB0', baudrate=4800)
if ser == None:
	l.plog("  Could not create serial connection.")
	input("Press any key to exit.")
	sys.exit()

def getUserInput():
	"""
	The main execution function of the user input thread. It just quietly
	waits until the user enters a valid choice. By setting the global
	variable 'debug' to False, you can exit this thread.
	
	Parameters:
		-None
		
	Returns:
		-None
	"""
	# Flag that we are referring to the global 'debug' variable.
	global debug
	
	# As long as the debug input flag is set we'll wait for user input.
	while debug:
	
		# We can't just let the user press enter. That will give us invalid input.
		while choice == None or len(choice)<1:
			choice = raw_input()
		
		# Check for the local playlist option. (The letter 'l' for "local")
		if(choice[0] == 'l' or choice[0] == 'L'): 
		
			if not playing:
			
				l.plog("Playing default local playlist!!!")
				
				l.plog("Spooling up playlist thread")
				thread.start_new_thread( playPlaylist, (localPlaylist, 'default') )
				
			else:
			
				killPlaylistThread()
				
		# Check for the Redis playlist option. (The letter 'r' for "Redis")
		if(choice[0] == 'r' or choice [0] == 'R'):
		
			if not playing:
			
				l.plog("Getting and playing default Redid playlist!!!")
				playlist = getUserPlaylist('default', r)
				
				l.plog("Spooling up playlist thread")
				thread.start_new_thread( playPlaylist, (playlist, 'default') )
				
			else:
			
				killPlaylistThread()
		
		# Check for the option that quits debug input. ('d' for 'debug')
		if(choice[0] == 'd' or choice[0] == 'd'):
			debug = False
		
		# Check for the option that quits altogether. ('q' for 'quit')
		if(choice[0] == 'q' or choice[0] == 'Q'):
			sys.exit()
			
	
def startSox(url):
	"""
	Starts the audio provided at the given URL, using Play, a
	SoX derivative.
	
	Parameters:
		-url (String): The URL of the audio file.
		
	Returns:
		-None
	"""
	system("sox -q "+url+" -d");

def playPlaylist(url_list, user):
	"""
	Iterates through a given playlist of audio URLs,
	playing each.
	
	This function is meant to be run in its own thread.
	
	Parameters:
		-url_list (Set of Strings):	A list of audio URLs.
		
		-user (String):	The current user, for logging purposes.
		
	Returns:
		-None
	"""
	l.plog("--Starting "+user+"'s playlist.")
	l.plog("--Length: "+len(url_list)+" songs")
	
	# State that we're playing the music!
	global playing
	playing = True
	
	# Iterate through every URL, pumping it through SoX.
	for i in range(len(url_list)):
		if not playing: return
		l.plog("--Starting song # "+str(i)+" of "+str(len(url_list)))
		l.plog("--URL: "+url_list[i])
		startSox(url)
		
	l.plog("--Finished playlist.")
	
	playing = False

def killPlaylistThread():
	"""
	Kills off a playlist thread, and all spawned processes of
	SoX with it.
	
	Parameters:
		-None
		
	Returns:
		-None
	"""
	l.plog("Killing SoX processes and exiting playlist thread")
	# Kill all Play processes.
	system("killall -q sox")
	
	# Set the audio to stop.
	global playing
	playing = False
	
	
def getUserDictionary():
	"""
	Creates a dictionary of user names indexed by user ID.
	
	Prerequisites:
		-Able to log into LDAP, and the LDAP database contains 
		userID attributes.
	
	Parameters:
		-None
	
	Returns:
		-A dictionary whose keys are userIDs (iButtonIDs) and 
		values are user-names.
	"""
	# Open up a connection to LDAP.
	l.plog("Opening LDAP connection...")
	ldap = CSHLDAP('mickey', 'mcdick')
	if ldap == None:
		l.plog("Could not establish LDAP connection.")
		input("Press any key to exit.")
		sys.exit()
	
	# Get all them members.
	members = ldap.members()
	
	# Create an empty dictionary to store all the pairs.
	memberDict = {}
	
	# Go through each member returned and give them an entry 
	# into the dictionary.
	for member in members:
		memberDict[ member[1]["ibutton"] ] = member[1]["uid"]
	
	# Return the dictionary.
	return memberDict
	
def getUserPlaylist(user, rHandle):
	"""
	Queries the Redis database for the selected user's playlist.
	
	Parameters:
		-user(String):		The current user.
		
		-rHandle(redis):	A handle to a Redis client instance.
	
	Returns:
		A list of the URLs of the current user's songs.
	
	"""
	# Get the user's Song list, which is really just a list of URLs.
	print("Querying for "+user+"'s playlist on the Redis database.")
	
	response =rHandle.lrange(user+"-playlist", 0, -1)
	
	# The response is a 'bytes' instance.
	responseBytes = response[0]
	responseString = ''
	for b in responseBytes:
		responseString += chr(b)
	
	return responseString.split(",")
	
def exitFunction():
	"""
	A callback for when the program exits. It cleans up threads, etc.
	
	Parameters:
		-None
		
	Returns:
		-None
	"""
	print("Exiting program. Cleaning up threads.")
	killPlaylistThread()
	global debug
	debug = False
	

def main():
	"""
	The main execution of the SOAP shower client.
	"""
	print("**************************************************************")
	print("*                    CSH SOAP Shower Client                  *")
	print("* Letting you scrub-a-dub-dub with a wub-wub-wub since 2014. *")
	print("* ---------------------------------------------------------- *")
	print("* Press r to pull and play a debug playlist from Redis       *")
	print("* Press l to play the local debug playlist (no use of Redis) *")
	print("* Press d to kill the debug input thread                     *")
	print("* Press q to exit the shower client completely.              *")
	print("**************************************************************")
	
	# Register the exit clean-up callback.
	sys.exitfunc = exitFunction
	
	# Create a variable to store the serial-read id.
	id = ''
	
	# A string storing the current user.
	curUser = ''

	# A dictionary that serves as a LUT for
	# user iButton IDs to user names.
	idLUT  = getUserDictionary();
	
	# Start up the debug input thread.
	l.plog("Starting debug input thread...");
	thread.start_new_thread( getUserInput, None )
	
	# Open and verify serial port.
	l.plog("Opening serial connection...")
	ser.open()

	if( ser.isOpen() ):
		l.plog("Serial port is open and ready for use.")
	else:
		l.plog("Serial port was not opened correctly.")
		input("Press any key to exit.")
		sys.exit()

	# Clear existing data.
	l.plog("Flushing pre-existing serial data.")
	ser.flushInput()
	
	# Enter serial waiting loop.
	while True:

		# read serial number.
		l.plog("Waiting for iButton...")
		id = ser.readline()
		id = id[1:] # trim first character.
		id = id.rstrip() # remove leading and trailing white space.
		l.plog("iButton read: "+id)
		
		# plug it in to the dictionary so that we can the the user-name.
		member = members[id]
		if member == None:
			l.plog("Invalid iButton ID, or user is not in the system.")
		else:
			l.plog("Corresponding member: "+member)
		
		if not playing:
			# Update the current user.
			curUser = member
			l.plog(curUser+" is starting their playlist!!!")
			
			#Get the current user's playlist.
			l.plog("Getting "+curUser+"'s playlist from Redis")
			playlist = getUserPlaylist(curUser, r);
			
			# Create the playlist thread for this user.
			l.plog("Spooling up playlist thread")
			thread.start_new_thread( playPlaylist, (playlist, user) )
		
		else:
			# If the current user is re-accessing the system it means
			# that they want to stop the audio, and we do that cordially.
			if member == curUser:
				print(curUser+" is stopping their playlist.")
				killPlaylistThread(playlistThread)
				
			# Otherwise it's some asshole prick who's interrupting the 
			# flow of music.
			else:
				l.plog(member+" is not the current user ("+curUser+") and cannot stop the music.")
		
		
		# Clear serial input so stacking doesn't occur.
		l.plog("Clearing existing serial input... ")
		ser.flushInput()


