Minblox - sample set minimization tool

Minblox tool is comprised of two parts. 
 - A DynamoRIO instrumentation part (libbbcoverage) tasked with recording
all basic block executed during application execution.
 - minblox.py - Python script that runs the DynamoRIO instrumentation
 and analyzes the log files to minimize the sample set. 
 
Currently, it's tested on Linux, but should run on Windows with small
modifications too. 
 
To compile the bbcoverage tool, place the bbcoverage directory inside
DynamoRIO distribution directory. Run:
	* # cmake . (create makefiles)
	* # make    (build the tool)
 
Copy the built tool from bbcoverage/bin directory to minblox directory.
If needed, adjust DR_RUN_PATH and BBCOVERAGE_PATH variables in minblox.py
to point to required binaries. 
 
If necessary, modify the HOST and PORT variables for HTTP server to listen
on. 
 
The tool has a couple of options:
 
 * --samples - Directory containing file sample set to minimize. It is 
required during the coverage phase.
 
 * --application - Path to the application to instrument. Required during
coverage phase.
 
 * --server - If specified, sample files will be served to the application
over HTTP server. For some file types, browsers exhibit different behavior 
when files are opened from disk rather than from server.
 
 * --timeout - Specifies the amount of time (in seconds) that the coverage
will run. Can be unspecified if application exists by itself , otherwise
it is required.
 
 * --logs - Specifies the directory in which basic block coverage files will
be saved.
 
 * --extension - If set , files found under samples directory will be filtered
by specified extension. 
 
 * --output - Specifies the directory in which to save the minimal sample set.
Required during minimization phase.
 
 * --cover - If set, minblox.py will run the basic block coverage phase.
 
 * --minimize - If set, minblox.py will run the minimization phase.
 
 Lots of place for improvements!
 
 IMPORTANT: Prior to running the minimization, ASLR needs to be disabled.
