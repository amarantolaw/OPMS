import datetime, sys

# DEBUG AND INTERNAL HELP METHODS ==============================================================
# TODO: Work out how to make these into generic functions that can be called from anywhere

def _debug(self,error_str):
    "Basic optional debug function. Print the string if enabled"
    if self.debug:
        print 'DEBUG:' + str(error_str) + '\n'
    return None


def _errorlog(self,error_str):
    "Write errors to a log file"
    # sys.stderr.write('ERROR:' + str(error_str) + '\n')
    #self.error_log.write('ERROR:' + str(error_str) + '\n')
    self.error_cache += 'ERROR:' + str(error_str) + '\n'
    return None


def _errorlog_start(self, path_to_file):
    try:
        self.error_log = open(path_to_file,'a')
    except IOError:
        sys.stderr.write("WARNING: Could not open existing error file. New file being created")
        self.error_log = open(path_to_file,'w')

    self.error_log.write("Log started at " + str(datetime.datetime.utcnow()) + "\n")
    print "Writing errors to: " + path_to_file
    return None

def _error_log_save(self):
    "Write errors to a log file"
    self.error_log.write(self.error_cache)
    self.error_cache = ""
    return None


def _errorlog_stop(self):
    self.error_log.write("Log ended at " + str(datetime.datetime.utcnow()) + "\n")
    self.error_log.close()
    return None