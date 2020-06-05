from pythreader import TaskQueue, Task, DEQueue, PyThread, synchronized
import re
import subprocess, time
from partition import part

from config import Config

def runCommand(cmd, timeout=None, debug=None):
    return p.returncode, out

class Killer(PyThread):

    def __init__(self, scanner, timeout):
	PyThread.__init__(self)
	self.Scanner = scanner
	self.Timeout = timeout
	self.Stop = False

    def stop(self):
	self.Stop = True

    def run(self):
	t1 = time.time() + self.Timeout
	while not self.Stop and time.time() < t1:
		time.sleep(0.5)
	if not self.Stop:
		self.Scanner.killme()
		self.Scanner = None
    
class Scanner(Task):
    
    def __init__(self, master, server, location, use_recursive, timeout):
        Task.__init__(self)
        self.Server = server
        self.Master = master
        self.Location = location
        self.Timeout = timeout
        self.UseRecursive = use_recursive
	self.Subprocess = None
	self.Done = False
	self.Killed = False

    def __str__(self):
        return "Scanner(%s)" % (self.Location,)

    @synchronized
    def killme(self):
	if self.Subprocess is not None:
		self.Killed = True
		self.Subprocess.terminate()
		print("Terminated: %s" % (self.Location,))
        
    def run(self):
        t0 = time.time()
	sys.stderr.write("Start %sscan of %s\n" % ("recursive " if self.UseRecursive else "", self.Location))
        location = self.Location
        lscommand = "xrdfs %s ls %s %s" % (self.Server, "-R" if self.UseRecursive else "", self.Location)

	killer = Killer(self, self.Timeout)

	with self:
		# the killer process will wait for self.Subprocess to become not None or Done to become True
		self.Subprocess = subprocess.Popen(lscommand, shell=True, 
			stderr=subprocess.PIPE,
			stdout=subprocess.PIPE)
		killer.start()		# do not start killer until self.Subprocess is set

        out, err = self.Subprocess.communicate()

	with self:
		# make this a critical section so the killer process does not intercept us
		killer.stop()
		retcode = self.Subprocess.returncode
        	self.Subprocess = None

        if retcode or self.Killed:
            self.Master.scanner_failed(self, err)
        else:
            files = []
            ndirs = 0
            lines = [x.strip() for x in out.split("\n")]
            for l in lines:
                l = l.strip()
                if l:
		    last_word = l.rsplit("/",1)[-1]
                    if '.' in last_word:
                        path = l
                        path = path if path.startswith(location) else location + "/" + path
                        if not path.endswith("/."):
				files.append(path)
                    else:
			if not self.UseRecursive:
                                ndirs += 1
				path = l
				path = path if path.startswith(location) else location + "/" + path
				self.Master.addDirectory(path)
            print("Found %d files %d directories under %s" % (len(files), ndirs, self.Location))
            if files:
                self.Master.addFiles(files)

class ScannerMaster(PyThread):
    
    def __init__(self, server, root, recursive_threshold, max_scanners, timeout):
        PyThread.__init__(self)
        self.RecursiveThreshold = recursive_threshold
        self.Server = server
        self.Root = self.canonic(root)
        self.MaxScanners = max_scanners
        self.Results = DEQueue(10)
        self.ScannerQueue = TaskQueue(max_scanners)
        self.Timeout = timeout
        self.Done = False
        self.Error = None
        self.Failed = False
        self.Directories = set()

    def run(self):
        self.addDirectory(self.Root)
        self.ScannerQueue.waitUntilEmpty()
        self.Results.close()
        self.Done = True
        
    def addFiles(self, files):
        if not self.Failed:
	    self.Results.append(files)

    def canonic(self, path):
	while path and "//" in path:
		path = path.replace("//", "/")
	return path
      
    def addDirectory(self, path):
        if not self.Failed:
	    path = self.canonic(path)
	    self.Directories.add(path)
            assert path.startswith(self.Root)
            relpath = path[len(self.Root):]
            while relpath and relpath[0] == '/':
                relpath = relpath[1:]
            while relpath and relpath[-1] == '/':
                relpath = relpath[:-1]
            reldepth = 0 if not relpath else len(relpath.split('/'))
            use_recursive = self.RecursiveThreshold is not None and reldepth >= self.RecursiveThreshold
            #if use_recursive:
            #    print("Use recursive for %s" % (path,))
            self.ScannerQueue.addTask(
                Scanner(self, self.Server, path, use_recursive, self.Timeout)
            )
    
    def scanner_failed(self, scanner, error):
	    sys.stderr.write("Error scanning %s: %s -- retrying\n" % (scanner.Location, error))
            self.ScannerQueue.addTask(
                Scanner(self, self.Server, scanner.Location, False, self.Timeout)
            )

    def files(self):
        while not (self.Done and len(self.Results) == 0):
            lst = self.Results.pop()
            if lst:
		    for path in lst:
			yield self.canonic(path)
    
            
Usage = """
python xrootd_scanner.py [options] <rse>
    Options:
    -c <config.json>         	- config file, required
    -o <output file prefix>  	- output will be sent to <output>.00000, <output>.00001, ...
    -t <timeout>       		- xrdfs ls operation timeout (default 30 seconds)
    -m <max workers>		- default 5
    -R <recursion depth>	- start using -R at or below this depth (dfault 3)
"""
        
if __name__ == "__main__":
    import getopt, sys, time
    
    opts, args = getopt.getopt(sys.argv[1:], "t:m:o:R:n:c:")
    opts = dict(opts)
    
    if len(args) != 1 or not "-c" in opts:
        print(Usage)
        sys.exit(2)

    rse = args[0]
    config = Config(opts.get("-c"))

    root = config.scanner_root(rse)
    server = config.scanner_server(rse)
    remove_prefix = config.scanner_remove_prefix(rse) or root
    add_prefix = config.scanner_add_prefix(rse)
    max_scanners = config.scanner_workers(rse) or int(opts.get("-m", 5))
    recursive_threshold = config.scanner_recursion_threshold(rse) or int(opts.get("-R", 3))
    timeout = config.scanner_timeout(rse) or int(opts.get("-t", 30))
    nparts = config.nparts(rse)

    output = opts.get("-o")
    if nparts > 1:
        if not output:
            print ("Output prefix is required for partitioned output")
            print (Usage)
            sys.exit(2)
    
    if not output:
        outputs = [sys.stdout]
    else:
        outputs = [open("%s.%05d" % (output, i), "w") for i in range(nparts)]
       
    t0 = time.time()
 
    master = ScannerMaster(server, root, recursive_threshold, max_scanners, timeout)
    master.start()
    n = 0
    for path in master.files():

        if remove_prefix and path.startswith(remove_prefix):
            path = path[len(remove_prefix):]
            
        if add_prefix:
            path = add_prefix + path
            
        i = 0 if nparts == 1 else part(nparts, path)
        outputs[i].write("%s\n" % (path,))

        n += 1
        if False and (n % 100 == 0):
            scanners = list(master.ScannerQueue.activeTasks())
            print ("[Active scanners: %d]" % (len(scanners),))
            for s in scanners:
                print "    %s" % (s,)

    if master.Failed:
        print("Scanner failed:", master.Error)

    t = int(time.time() - t0)
    sys.stderr.write("Found %d files in %d directories\n" % (n, len(master.Directories)))
    sys.stderr.write("Elapsed time: %dm%ds\n" % (t//60, t%60))

    [out.close() for out in outputs]
    
    
        