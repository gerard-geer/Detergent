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
import CSHLDAP
import thread
import json

# The message logger.
print("Creating logger")
l = Logger(16)

# The debug local playlist.
localPlaylist = ['http://www.csh.rit.edu/~gman/soap/dbsrv-ashes-to-ashes.mp3', \
				'http://www.csh.rit.edu/~gman/soap/dbsrv-china-girl.mp3', \
				'http://www.csh.rit.edu/~gman/soap/dbsrv-what-in-the-world.mp3'];

# Whether or not audio is being played.
playing = False

# Redis server hostname and other parameters
redis_host = 'soap.csh.rit.edu'
redis_port = 6379
redis_pw = 'shitty_password'


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
	
def startSox(url):
	"""
	Starts the audio provided at the given URL, using Play, a
	SoX derivative.
	
	Parameters:
		-url (String): The URL of the audio file.
		
	Returns:
		-None
	"""
	system("sox -q "+url+" -d")
	
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
	
def getUsername(ibuttonID):
	"""
	Returns a user's username based on their iButton ID.
	
	Prerequisites:
		-The ibutton2uid script on totoro isn't dead.
		
	Parameters:
		-ibuttonID (String): 	The read iButtonID.
	
	Returns:
		The username, if the iButton ID is valid and found,
		or None otherwise.
	"""
	req = urllib2.Request("http://totoro.csh.rit.edu:56124/?ibutton="+ibuttonID)
	res = urllib2.urlopen(req)
	uid = res.read()
	try:
		uid = json.loads(uid)
		return uid['username']
	except:
		return None
	
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
	
	# If the user does not exist then the response will be null.
	if not response:
		return []
	
	# The response is a 'bytes' instance, in a 1-element list.
	responseBytes = response[0]
	
	return responseBytes.split(",")	
	
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
	
	# Iterate through every URL, pumping it through SoX.
	for i in range(len(url_list)):
		if not playing: return
		l.plog("--Starting song # "+str(i)+" of "+str(len(url_list)))
		l.plog("--URL: "+url_list[i])
		startSox(url)
		
	l.plog("--Finished playlist.")

def handleUser(username):
	"""
	The main function of the per-playlist-request worker thread.
	Fetches the user's playlist from the database and play it.
	
	Parameters:
		username(String):	The username of the current user.
	
	Prerequisites:
		The redis database is up.
		
	"""
	
	# State that we're playing the music!
	global playing
	playing = True
	
	# Create Redis handle.
	p.log("Creating Redis connection.")
	r = redis.StrictRedis(host=redis_host, port=redis_port, pw=redis_pw)
	if r == None:
		l.plog("Could not create Redis client.")
		playing = False
		return
	
	playlist = getUserPlaylist(user, r)
	playPlaylist(playlist, user)
	playing = False

def main():
	"""
	The main execution of the SOAP shower client.
	"""
	print("**************************************************************")
	print("*                    CSH SOAP Shower Client                  *")
	print("* Letting you scrub-a-dub-dub with a wub-wub-wub since 2014. *")
	print("* ---------------------------------------------------------- *")
	print("* Press q to exit the shower client.                         *")
	print("**************************************************************")
	
	# Register the exit clean-up callback.
	sys.exitfunc = exitFunction
	
	# Create a variable to store the serial-read id.
	id = ''
	
	# A string storing the current user.
	curUser = ''
	
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
		member = getUsername(id)
		if member == None or member == '':
			l.plog("Invalid iButton ID, or user is not in the system.")
		else:
			l.plog("Corresponding member: "+member)
		
		if not playing:
			# Update the current user.
			curUser = member
			l.plog(curUser+" is starting their playlist!!!")
			# Create the playlist thread for this user.
			l.plog("Spooling up playlist thread")
			thread.start_new_thread( handleUser, (user,) )
		
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


