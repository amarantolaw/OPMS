'''
1) Script to import/update GeoIP data
2) Reverse DNS get or create type method
3) Method for parsing User Agent Strings
'''

# Import script for Maxmind GeoIP data to the stats_iplocation table
# Author: Carl Marshall
# Last Edited: 4-2-2011

from django.core.management.base import BaseCommand, CommandError
from opms.stats.models import *
import time, sys
        
class Command(BaseCommand):
    args = '<spreadsheet.xls>'
    help = 'Imports the contents of the specified spreadsheet into the database'

    def handle(self, *args, **options):
        print "Import simulated\n\n"