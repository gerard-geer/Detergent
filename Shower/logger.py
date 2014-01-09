from datetime import datetime

class Logger:
	
	__slots__ = ('filename', 'buffer', 'maxBufferSize')
	def __init__(maxBufferSize):
		"""
		Creates an instance of Logger. The output file will be named
		the date and time of this instance's creation.
		
		Parameters: 
			-maxBufferSize(Integer):	The maximum number of messages
										to accrue before writing to 
										file.
		"""
		
		# Create a file name based on the current date.
		self.filename = "shower_"+datetime.month+'_'+datetime.day+'_'+ \
					datetime.year+'_'+datetime.hour+":"+datetime.minute+ \
					":"+datetime.second+".log"
					
		# Instantiate the message buffer
		self.buffer = []
		
		# Store the maximum buffer size.
		self.maxBufferSize = maxBufferSize
	
	def log(message):
		"""
		Logs a message to the buffer that will eventually be written 
		to file.
		
		Parameters:
			-message(String):	The message to log.
		
		Returns:
			-None
		"""
		self.buffer.append(message)
		self.checkWrite()
		
	def plog(message):
		"""
		Logs a message to the buffer through log(), but also prints it
		to the screen.
		
		Parameters:
			-message(String): The message to log.
		"""
		print(message)
		log(message)
		
	def checkWrite():
		"""
		Checks to see if the buffer is full and a write out to file is necessary.
		If so, the buffer contents are written out to the log file, and the 
		buffer is cleared.
		
		Parameters:
			-None
			
		Returns:
			-None
		"""
		if len(self.buffer) > self.maxBufferSize:
			file = open(filename, 'a')
			if file != None:
				for message in buffer:
					f.write(str(message))
				f.close()
				buffer = []
			else:
				print("Could not write out buffer to file. Perhaps the log file is being used by another program?")
			
				
				
	