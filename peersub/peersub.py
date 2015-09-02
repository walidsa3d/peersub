import zipfile
import cStringIO
import re
import subprocess
import requests
from sys import argv
from bs4 import BeautifulSoup as bs
from termcolor import colored
import magneto
from itertools import chain

base_url='http://subscene.com'
language='english'

def search(release_name):
    """search subtitles from subscene.com"""
    results=[]
    payload={'q':release_name,'r':'true'}
    url='http://subscene.com/subtitles/release'
    response=requests.get(url,params=payload).text
    soup = bs(response,"lxml")
    positive=soup.find_all(class_='l r positive-icon')
    neutral=soup.find_all(class_='l r neutral-icon')
    for node in chain(positive,neutral):
        suburl=node.parent['href']
        quality=node['class'][2].split('-')[0]
        name=node.parent.findChildren()[1].text.strip()
        if language in suburl and 'trailer' not in name.lower():
            results.append({'url':base_url+suburl,'name':name,'quality':quality})
    return dict(enumerate(results))


def download(sub_url):
    """download and unzip subtitle archive to a temp location"""
    response=requests.get(sub_url).text
    soup = bs(response,'lxml')
    downlink=base_url+soup.select('.download a')[0]['href']
    data = requests.get(downlink)
    z = zipfile.ZipFile(cStringIO.StringIO(data.content))
    srt_files = [f.filename for f in z.filelist
                 if f.filename.rsplit('.')[-1].lower() in ['srt', 'ass']]
    z.extract(srt_files[0], '/tmp/')
    return srt_files[0]

    
def main():
    filename=magneto.parse(argv[1])['name']
    if filename is not None:
        subtitles=search(filename)
        for index,link in subtitles.iteritems():
            index=colored(str(index),'white')
            name=colored(link['name'],'cyan')
            lang=colored(language, 'red','on_green')
            quality=colored(link['quality'],'blue')
            s="{:12} {:20} {:20} {:50}".format(index,lang,quality,name)
            print s
        x=raw_input("Choose Subtitle: \t")
        downlink=subtitles[int(x)]['url']
        name=subtitles[int(x)]['name']
        subname=download(downlink)
        command = ['peerflix', argv[1], '--vlc', '--remove', '--connections', '60']
        command.append('--subtitles')
        command.append('/tmp/'+subname)
        subprocess.Popen(command)

main()