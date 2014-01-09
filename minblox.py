#!/usr/bin/python
from optparse import OptionParser
import sys
import os
import shutil
import socket
import threading
import SocketServer
import SimpleHTTPServer

DR_RUN_PATH = "./DynamoRIO-Linux-4.1.0-8/bin64/drrun"
BBCOVERAGE_PATH = "./libbbcoverage.so" # path to dynamoRIO coverage lib
HOST, PORT = "localhost", 8081 # host and port for simple http server

def readfiles(directory,ext):
	'''
	Recursively go trough the directory tree and enumerate all the files.
	If given, filter by extension. 	
	'''
	files = []
	for dirpath,dirnames,filenames in os.walk(directory):
		for filename in [f for f in filenames]:
			file_path = os.path.join(dirpath,filename)
			if os.path.isfile(file_path):
				if options.extension != None:
					if file_path.find("."+ext) == -1:
						continue
				files.append(file_path)
	return files

# Simple threaded TCP server for handling HTTP connections
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class Minblox:
	'''
	Small class containing coverage and minimization methods.
	'''
	def cover(self,app,samples,serve,timeout,logs):
		'''
		Method runs the target application trough the sample set with
		under DynamoRIO basic block coverage tool. Coverage logs are 
		saved under logs directory. If serve option is set, serve sample
		files over HTTP server. If timeout is given, stop application
		execution after timeout. 
		'''
		
		#build the command
		cmd = DR_RUN_PATH
		if timeout != None:
			cmd += " -s " + str(timeout)
		cmd += " -logdir ."
		cmd += " -c " + BBCOVERAGE_PATH
		cmd += " -- " + app
		try:
			os.mkdir(logs)
		except:
			pass
		i = 0
		server = None
		if serve: #start the HTTP server if serve option specified
			Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
			server = ThreadedTCPServer((HOST, PORT), Handler)
			server_thread = threading.Thread(target=server.serve_forever)
			server_thread.daemon = True
			server_thread.start()				
		for sample in samples: # instrument application for each sample
			command = cmd + " "
			if serve:
				command += "http://"+HOST+":"+str(PORT) + "/"
			command += sample
			print "[+] Running trace on sample %d out of %d"%(i+1,len(samples))
			i+=1
			os.system(command + " > /dev/null") #don't want app stdout 
			f = open("bbcov.log","a")
			f.write(sample) # record the sample path so we can retrive it later
			f.close()
			log_path = logs + "/" + sample.replace("/","_").strip(".")
			shutil.move("bbcov.log",log_path) # save coverage log for analysis
		if server != None:
			server.shutdown()
	
	def find_largest(self,logs):
		'''
		Find log file with most basic blocks covered. 
		That log file is used as a starting point in sample set 
		minimization. Returns file name and set of basic blocks.
		'''
		largest = ""
		most_blocks = set() # use sets so we have unique blocks 
		for log in logs:
			log_file = open(log,"r")
			basic_blocks = set(log_file.readlines()[:-1]) # ignore last line
			log_file.close()
			if len(basic_blocks) > len(most_blocks):
				largest = log
				most_blocks = basic_blocks
		return largest,most_blocks
		
	def minimize(self,logs,output):
		'''
		Minimize the sample set by analyzing the coverage logs.
		Copy minimal sample set to output directory.
		'''
		try:
			os.mkdir(output)
		except:
			pass
		min_files = []
		largest,min_list_bb = self.find_largest(logs) #find starting sample
		print "Biggest coverage achieved in %s with %d basic blocks"%(largest,len(min_list_bb))
		min_files.append(largest)
		for log in logs:
			if log == largest: # don't process the largest one again
				continue
			log_file = open(log,"r")
			log_bb = set(log_file.readlines()[:-1]) # skip last line 
			log_file.close()
			if not log_bb.issubset(min_list_bb): # if it's true subset, it has no new basic blocks
				size_before = len(min_list_bb)
				min_list_bb.update(log_bb)
				min_files.append(log)
				print "Added %d basic blocks to the superset from %s"%(len(min_list_bb)-size_before,log)
		print "Copying minimal set of %d samples to %s."%(len(min_files),output)
		for log in min_files: 
			log_file = open(log,"r")
			file_path = log_file.readlines()[-1].strip()
			shutil.copy(file_path,output + "/" + "".join(file_path.split("/")[1:]))
		print "Done!"
		

print "\n\tMinblox - sample set minimizer\n"


parser = OptionParser()

parser.add_option("-s", "--samples",action="store",
				                    dest="samples",
				                    help="Directory containing file samples. Required with --cover.")
parser.add_option("-a", "--application",action="store",
				                    dest="application",
				                    help="Path to the application to cover. Required with --cover.")
parser.add_option("-S", "--server", action="store_true",
								    dest="http",
								    help="Serve files for coverage over HTTP server .")
parser.add_option("-t", "--timeout", action="store",
								    dest="timeout",
								    type="int",
								    help="Kill application after timeout in seconds.")
parser.add_option("-l", "--logs", action="store",
								    dest="logs",
								    help="Directory containing coverage log files. Required with --minimize and --cover.")
parser.add_option("-e", "--extension", action="store",
									dest="extension",
									help="Filter samples by extension.")		
parser.add_option("-o","--output",action="store",
									dest="output",
									help="Minimal sample set destination directory.")
parser.add_option("-c", "--cover", action="store_true", dest="cover")
parser.add_option("-m", "--minimize", action="store_true", dest="minimize")



(options, args) = parser.parse_args()
minblox = Minblox()

if (options.cover != None or options.minimize != None) == False:
	print "Choose either coverage or minimization!\n"
	parser.print_help()
	sys.exit(0)

if options.cover and options.minimize:
	print "\tChoose either coverage or minimization\n"
	parser.print_help()
	sys.exit(0)
samples = []	
if options.cover:
	if options.samples == None or options.logs == None:
		print "\n\t-c requires samples directory (-s) and logging directory (-l)"
		sys.exit(0)
	else:
		samples = readfiles(options.samples,options.extension)
		print "[+] Running basic block tracing on %d files"%(len(samples))
		minblox.cover(options.application, samples, options.http , options.timeout,options.logs)
		sys.exit(0)
logs = []
if options.minimize and (options.logs == None or options.output == None):
	print "\n\y-m requres both logs directory (-l) and output directory (-o)"
else:
	print "RUNNING MINIMIZATION"
	logs = readfiles(options.logs,None)
	minblox.minimize(logs,options.output)
	sys.exit(0)



