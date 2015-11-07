#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import subprocess
import zipfile

from itertools import chain

import requests

import torrentutils

from bs4 import BeautifulSoup as BS
from termcolor import colored
import argparse
from . import __version__

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
    parser = argparse.ArgumentParser(usage="-h for full usage")
    parser.add_argument(
        '-V', '--version', action='version', version=__version__)
    parser.add_argument('link', help='magnet link')
    parser.add_argument('--vlc', help='magnet link', action='store_true')
    parser.add_argument('--mpv', help='magnet link', action='store_true')
    parser.add_argument('--mplayer', help='magnet link', action='store_true')
    args = parser.parse_args()
    if args.mplayer:
        player = '--mplayer'
    elif args.mpv:
        player = '--mpv'
    else:
        player = '--vlc'
    # parse magnet links
    magnetdata = torrentutils.parse_magnet(args.link)
    releasename = magnetdata['name']
    prettyprint(magnetdata)
    if releasename is not None:
        subtitles = search(releasename)
        for index, link in subtitles.iteritems():
            index = colored(str(index), 'white')
            name = colored(link['name'], 'cyan')
            lang = colored(LANGUAGE, 'red', 'on_green')
            s = "{:12} {:20} {:50}".format(index, lang, name)
            print s
        x = raw_input("Choose Subtitle: \t")
        downlink = subtitles[int(x)]['url']
        name = subtitles[int(x)]['name']
        subname = download(downlink)
        command = ['peerflix', args.link, player,
                   '--remove', '--connections', '60']
        command.append('--subtitles')
        command.append('/tmp/'+subname)
        subprocess.Popen(command)
