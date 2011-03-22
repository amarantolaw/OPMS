# Perform Reverse DNS on stats.RDNS script
# Author: Carl Marshall
# Last Edited: 22-3-2011
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from opms.stats.models import *
import datetime, sys
from dns import resolver,reversename
from IPy import IP
from time import sleep

class Command(NoArgsCommand):
    help = 'Scan through stats.rdns entries and attempt to resolve the Unknown IP addresses to a domain name'
    #option_list = LabelCommand.option_list + (
    #    make_option('--startline', action='store', dest='start_at_line',
    #        default=1, help='Optional start line to allow resumption of large log files. Default is 1.'),
    #)
    
    def __init__(self):
        # datetime value for any rdns timeout problems
        self.rdns_timeout = 0
        # Toggle debug statements on/off
        self.debug = False
        # Record basic information about the import process for reporting
        self.update_stats = {}
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""        
        
        super(Command, self).__init__()


    def handle_noargs(self, **options):
        print "Update started at " + str(datetime.datetime.utcnow()) + "\n"

        # Create an error log
        self._errorlog_start('update_rdns.log')
     
        # Reset statistics
        self.update_stats['update_count'] = 0
        self.update_stats['update_timeoutskips'] = 0
        self.update_stats['update_starttime'] = datetime.datetime.utcnow()
        
        
        # Loop through stats.rdns entries that show as Unknown, attempt rdns lookup
        for record in Rdns.objects.filter(resolved_name='Unknown'):
            record.resolved_name = self._rdns_lookup(record.ip_address)
            self.update_stats['update_count'] += 1
            if record.resolved_name == 'Unknown':
                self.update_stats['update_timeoutskips'] += 1
            else:
                # Update the record!
                record.last_updated = datetime.datetime.utcnow()
                record.save()
            
            if (self.update_stats.get('update_count') % 10) == 0:
                # Output the status
                try:
                    self.update_stats['update_rate'] = float(self.update_stats.get('update_count')) /\
                        float((datetime.datetime.utcnow() - self.update_stats.get('update_starttime')).seconds)
                except ZeroDivisionError:
                    self.update_stats['update_rate'] = 0
                
                print str(datetime.datetime.utcnow()) + ": " +\
                    "Parsed " + str(self.update_stats.get('update_count')) + " IP Addresses. " +\
                    "Skipped " + str(self.update_stats.get('update_timeoutskips')) + " IP Addresses. " +\
                    "Rate: " + str(self.update_stats.get('update_rate'))[0:6] + " IP Addresses/sec. "
                    
                # Write the error cache to disk
                self._error_log_save()        
        
        # Final stats output at end of file
        try:
            self.update_stats['update_rate'] = float(self.update_stats.get('update_count')) /\
                float((datetime.datetime.utcnow() - self.update_stats.get('update_starttime')).seconds)
        except ZeroDivisionError:
            self.update_stats['update_rate'] = 0               
        
        print "\nUpdate finished at " + str(datetime.datetime.utcnow()) +\
            "\nSkipped " + str(self.update_stats.get('update_timeoutskips')) + " IP Addresses. " +\
            "\nIP addresses parsed: " + str(self.update_stats.get('update_count')) +\
            "\nImported at " + str(self.update_stats.get('update_rate'))[0:6] + " IP Addresses/sec\n"
        
        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()
            
        return None




    def _rdns_lookup(self, ipaddress):
        "Attempt an RDNS lookup for this ipaddress"
        # Default answer is the failure state of "Unknown"
        resolved_name = 'Unknown'

        # self._debug('_rdns_lookup('+str(ipaddress)+'): self.rdns_timeout=' + str(self.rdns_timeout))
        # Has a timeout occurred already? Was the timeout more than 30 seconds ago?
        if self.rdns_timeout == 0 or (datetime.datetime.utcnow() - self.rdns_timeout).seconds > 30:
            self.rdns_timeout = 0
            # Attempt an RDNS lookup, and remember to save this back to the object
            try:
                addr = reversename.from_address(ipaddress)
                resolved_name = str(resolver.query(addr,"PTR")[0])
                    
            except resolver.NXDOMAIN:
                self._errorlog('NXDOMAIN error trying to resolve:'+str(addr))
                resolved_name = 'No Resolved Name'
                    
            # Timeouts can be a problem with batch importing, use this to skip the issue for sorting later
            except resolver.Timeout:
                self.rdns_timeout = datetime.datetime.utcnow()
                self._errorlog('_rdns_lookup('+str(ipaddress)+') FAILED due to TIMEOUT at ' + str(self.rdns_timeout))
                
            except resolver.NoAnswer:
                self.rdns_timeout = datetime.datetime.utcnow() 
                self._errorlog('_rdns_lookup('+str(ipaddress)+') FAILED due to NO ANSWER at ' + str(self.rdns_timeout))
        else:
            self._errorlog('_rdns_lookup('+str(ipaddress)+') FAILED due to TIMEOUT at ' + str(self.rdns_timeout) + '. PAUSING for 30')
            if self.rdns_timeout != 0:
                sleep(30)
                
            
        # self._debug('_rdns_lookup('+str(ipaddress)+'): rdns='+resolved_name)
        
        return resolved_name




    # DEBUG AND INTERNAL HELP METHODS ==============================================================

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