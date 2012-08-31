import datetime, sys
from codecs import open
# DEBUG AND INTERNAL HELP METHODS ==============================================================
# Eventually this should be all replaced by Django logging I presume...
DEBUG = False
ERROR_CACHE = u""
ERROR_LOG = None


def __init__():
    global DEBUG
    DEBUG = False
    global ERROR_CACHE
    ERROR_CACHE = u""
    global ERROR_LOG
    ERROR_LOG = None
    return None

def onscreen(error_str):
    "Basic optional debug function. Print the string if enabled"
    global DEBUG
    if DEBUG:
        sys.stderr.write(u'DEBUG:{0}\n'.format(unicode(error_str)))
    return None

def errorlog(error_str=u"",display=False):
    "Write errors to a log file cache"
    global ERROR_CACHE
    ERROR_CACHE += u'ERROR:{0}\n'.format(unicode(error_str))
    if display:
        sys.stderr.write((error_str + u'\n').encode('utf-8'))
    return None

def log(str=u"",display=False):
    "Write messages to a log file cache"
    global ERROR_CACHE
    ERROR_CACHE += u'{0}\n'.format(unicode(str))
    if display:
        sys.stdout.write((str + u'\n').encode('utf-8'))
    return None

def errorlog_start(path_to_file):
    global ERROR_LOG
    try:
        ERROR_LOG = open(path_to_file, mode='a', encoding='utf-8')
    except IOError:
        sys.stderr.write(u"WARNING: Could not open existing error file. New file being created")
        ERROR_LOG = open(path_to_file, mode='w', encoding='utf-8')

    errorlog(u"Log started at {0:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.utcnow()))
    sys.stderr.write(u"Writing errors to: {0}\n\n".format(unicode(path_to_file)))
    return None

def errorlog_save():
    "Write errors to a log file"
    global ERROR_CACHE, ERROR_LOG
    if ERROR_LOG:
        ERROR_LOG.write(ERROR_CACHE)
        ERROR_CACHE = u""
    else:
        sys.stderr.write(u"WARNING!! No Error Log file has been created\n\n{0}".format(unicode(ERROR_CACHE)))
    return None

def errorlog_stop():
    global ERROR_LOG
    if ERROR_LOG:
        errorlog(u"Log ended at {0:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.utcnow()))
        errorlog_save()
        ERROR_LOG.close()
    else:
        sys.stderr.write(u"WARNING!! No Error Log file has been created")
    return None
