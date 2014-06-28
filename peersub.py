import requests
import json
import zipfile
import cStringIO
import urllib
import urllib2
import re
import subprocess
from sys import argv
import guessit
from bs4 import BeautifulSoup
import requests

def searchsub(release_name):
	base_url='http://subscene.com'
	results=[]
	url='http://subscene.com/subtitles/release?q='+release_name+'&r=true'
	print url
	response=requests.get(url)
	html=response.text
	tree = BeautifulSoup(html)
	for node in tree.findAll(attrs={'class': 'l r neutral-icon'}):
	    n=node.parent
	    x=n.parent['href']
	    if 'english' in x:
	    	y=base_url+x
	    	results.append(y)
	return dict(enumerate(line for line in results))
def get_download_link(sub_url):
	base_url='http://subscene.com'
	response=requests.get(sub_url)
	html=response.text
	tree = BeautifulSoup(html)
	for node in tree.findAll(attrs={'class':'download'}):
		return base_url+node.find('a')['href']

def dlSub(url):
    data = requests.get(url)
    z = zipfile.ZipFile(cStringIO.StringIO(data.content))
    srt_files = [i.filename for i in z.filelist
	             if i.filename.rsplit('.')[-1].lower() in ['srt', 'ass']]
    z.extract(srt_files[0], '/tmp/')
    return srt_files[0]

def getFileName(movie_link):
	if movie_link.startswith('magnet:'):
	    movie_filename = urllib.unquote_plus(movie_link)\
	                           .split('&dn=')[-1]\
	                           .split('&')[0]
	return movie_filename
def get_title(torrent_name):
	guess = guessit.guess_movie_info(torrent_name, info=['filename'])
	return guess['title']
	

x=getFileName(argv[1])
print x
subtitles=searchsub(x)
for i in subtitles:
	print str(i)+"."+subtitles[i]
x=raw_input("Choose Subtitle: \t")
z=get_download_link(subtitles[int(x)])
print z
w=dlSub(z)
print w
command = ['peerflix', argv[1], '--vlc', '--remove', '--connections', '60']
command.append('--subtitles')
command.append('/tmp/'+w)
p = subprocess.Popen(command)

