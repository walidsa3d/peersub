#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import subprocess
import sys
import zipfile

from itertools import chain

import requests

import torrentutils

from bs4 import BeautifulSoup as BS
from termcolor import colored

# site url
BASE_URL = 'http://subscene.com'
# language of subtitles
LANGUAGE = 'english'


def search(release_name):
    """search subtitles from subscene.com"""
    results = []
    payload = {'q': release_name, 'r': 'true'}
    url = 'http://subscene.com/subtitles/release'
    response = requests.get(url, params=payload).text
    soup = BS(response, "lxml")
    positive = soup.find_all(class_='l r positive-icon')
    neutral = soup.find_all(class_='l r neutral-icon')
    for node in chain(positive, neutral):
        suburl = node.parent['href']
        quality = node['class'][2].split('-')[0]
        name = node.parent.findChildren()[1].text.strip()
        if LANGUAGE in suburl and 'trailer' not in name.lower():
            results.append(
                {'url': BASE_URL+suburl, 'name': name, 'quality': quality})
    return dict(enumerate(results))


def download(sub_url):
    """download and unzip subtitle archive to a temp location"""
    response = requests.get(sub_url).text
    soup = BS(response, 'lxml')
    downlink = BASE_URL+soup.select('.download a')[0]['href']
    data = requests.get(downlink)
    z = zipfile.ZipFile(cStringIO.StringIO(data.content))
    srt_files = [f.filename for f in z.filelist
                 if f.filename.rsplit('.')[-1].lower() in ['srt', 'ass']]
    z.extract(srt_files[0], '/tmp/')
    return srt_files[0]


def prettyprint(magnetdata):
    for k, v in magnetdata.iteritems():
        if type(v) is list:
            print "{} : {}".format(k, ', '.join(v))
        else:
            print "{} : {}".format(k, v)


def main():
    if len(sys.argv) < 2:
        print "No magnet link provided"
        sys.exit(1)
    # parse magnet links
    magnetdata = torrentutils.parse_magnet(sys.argv[1])
    releasename = magnetdata['name']
    prettyprint(magnetdata)
    if releasename is not None:
        subtitles = search(releasename)
        for index, link in subtitles.iteritems():
            index = colored(str(index), 'white')
            name = colored(link['name'], 'cyan')
            lang = colored(LANGUAGE, 'red', 'on_green')
            quality = colored(link['quality'], 'blue')
            s = "{:12} {:20} {:20} {:50}".format(index, lang, quality, name)
            print s
        x = raw_input("Choose Subtitle: \t")
        downlink = subtitles[int(x)]['url']
        name = subtitles[int(x)]['name']
        subname = download(downlink)
        command = ['peerflix', sys.argv[1], '--vlc',
                   '--remove', '--connections', '60']
        command.append('--subtitles')
        command.append('/tmp/'+subname)
        subprocess.Popen(command)
