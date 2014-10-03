'''Scrapes the registrar for information about all of the courses and dumps
them into /registrar.'''

import urllib2, re, codecs, os, shutil
from xml.dom.minidom import parseString
import time

DELETE_OLD_STUFF_MODE = False

# timetable or roster depending on time of year
urlType = "roster"

# gives us a correct XML version of the URL
response = urllib2.urlopen("http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fwww.upenn.edu%2Fregistrar%2F" + urlType + "%2F%22%20and%20xpath%3D%22%2F%2Ftd%5B%40class%3D'body'%5D%2Fa%22&diagnostics=false")
html = response.read()

xmldoc = parseString(html)

subjects = [(link.getAttribute('href'), re.sub('\s+', ' ', link.firstChild.data)) \
             for link in xmldoc.documentElement.firstChild.childNodes if link.getAttribute('href') != '#' and not link.firstChild is None]

if DELETE_OLD_STUFF_MODE:
  shutil.rmtree('./registrardata')

try:
  os.mkdir('registrardata')
except Exception:
  pass

os.chdir('./registrardata')

#This may get throttled around 'l' - thank you Dan for yahoo pipes.
for subject in subjects:
    url = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fwww.upenn.edu%2Fregistrar%2F"+ urlType +"%2F" + (subject[0] if subject[0] != "cogs%20.html" else "cogs.html") + "%22%20and%20xpath%3D%22%2F%2Fpre%22"
    file_name = subject[0].split('.')[0] + '.txt'
    print file_name, url
    #if file already exists, just skip this one for now
    if not os.path.isfile(file_name):
      subjdoc = parseString(urllib2.urlopen(url).read())
      outfile = open(file_name, 'w')
      outfile.write(subject[1].encode('utf-8') + '\n')
      outfile.write("".join([codecs.getencoder('ascii')(x.nodeValue, 'ignore')[0] for x in subjdoc.firstChild.firstChild.firstChild.childNodes if x.nodeType==3]))
      outfile.close()
      time.sleep(3)  # don't get all angry at me for scraping yo
