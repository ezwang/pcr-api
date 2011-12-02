# Script to regenerate the Penn Course Review site cache.
#
# Before running this, make sure the symlink at 
#   penncoursereview.com:~pcr/projects/pcrsite/staticgenerator_output/write
# points to a fresh cache directory. (Also, all cache directories and symlinks
# should be owned by the Apache user "www-data".) When finished, remove the
# previous read symlink and point a new read symlink to the new cache
# directory. Remove dead directories as necessary (it's usually a good idea to
# keep 1 old one around.)
#
# This should definitely be run on a Penn (i.e. not off-campus) internet
# connection (since STWing's connection is much faster on-campus). Running
# it directly on the PCR server may or may not be a good idea.
#
# Known bugs: Many. In particular, watch out for:
#  - running out of disk space
#  - going over the maximum number of folders in the API cache
#
# If it breaks in the middle, don't worry about it, just rerun it. It'll
# go through the pages it's already cached really quickly.
# Note that many of the errors you'll get are just due to server overload,
# so it's probably a good idea to run the script twice (the pages that were
# overloaded before will [hopefully] work this time, and [theoretically]
# the only pages that fail on the second run are the ones with real errors)

import urllib2
import json
from pprint import pformat

from twisted.internet import reactor
import twisted.internet.defer
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

URL_PREFIX = 'http://api.penncoursereview.com/cachegen__access/'
N_CONCURRENT_ACCESSES = 15
SUCCESS_DISPLAY_LEN = 80

class PrinterClient(Protocol):
    def __init__(self, whenFinished, displayMax=80, displayFinished=True):
        self.whenFinished = whenFinished
        self.firstPart = True
        self.displayMax = displayMax
        self.displayFinished = displayFinished

    def dataReceived(self, bytes):
        if self.firstPart:
            self.firstPart = False
            print repr(bytes)[1:(1+self.displayMax)]

    def connectionLost(self, reason):
        if self.displayFinished:
            print 'Finished:', reason.getErrorMessage()
        self.whenFinished.callback(None)

def handleResponse(r, url, num, lenurls):
    isError = r.code != 200
    print "%c %6.2f%% (%6d) %50s  " % ('X' if isError else ' ', num*100.0/lenurls, num, url),
    if isError:
        print
        print "##### HTTP Error %d: %s" % (r.code, r.phrase)
        for k, v in r.headers.getAllRawHeaders():
            print "%s: %s" % (k, '\n  '.join(v))
    whenFinished = twisted.internet.defer.Deferred()
    r.deliverBody(PrinterClient(whenFinished, 400 if isError else SUCCESS_DISPLAY_LEN, isError))
    return whenFinished

def handleError(reason, url, num, lenurls):
    print "X %6.2f%% (%6d) %50s" % (num*100.0/lenurls, num, url)
    print "##### Script Error"
    reason.printTraceback()
    reactor.stop()

def getPage(url, num, lenurls):
    args = [url, num, lenurls]
    d = Agent(reactor).request('GET', URL_PREFIX + url, Headers({'User-Agent': ['twisted']}), None)
    d.addCallbacks(handleResponse, handleError, args, None, args, None)
    return d


d = urllib2.urlopen(URL_PREFIX + "autocomplete_data.json")
d_data = d.read()
print '!'
j = json.loads(d_data)
print '!'
#urls = ["course/AAMW-401"]*7 +["course/foo", "autocomplete_data.json"]
urls = [str(it['url']) for bla in j.values() for it in bla] 


semaphore = twisted.internet.defer.DeferredSemaphore(N_CONCURRENT_ACCESSES)
dl = list()

print "Loading %d URLS..." % len(urls)
for i, url in enumerate(urls):
    dl.append(semaphore.run(getPage, url, i, len(urls)))

dl = twisted.internet.defer.DeferredList(dl)
dl.addCallbacks(lambda x: reactor.stop(), handleError)

reactor.run()
