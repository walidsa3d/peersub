#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import subprocess
import zipfile

from itertools import chain

import requests

import torrentutils
import click
from bs4 import BeautifulSoup as BS
from termcolor import colored
from . import __version__
import videoscene.core as scene
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
    results = results[:15]
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
    release = magnetdata['name']
    parsed = scene.parse(release)
    title = colored(parsed['title'].title(), 'red')
    year = colored(parsed['year'], 'green')
    print 'Title: {}'.format(title)
    print 'Year: {}'.format(year)


@click.command()
@click.version_option(version=__version__)
@click.argument('link')
@click.option('--vlc', is_flag=True, help='use vlc player')
@click.option('--mpv', is_flag=True, help='use mpv')
@click.option('--mplayer', is_flag=True, help='use mplayer')
def main(link, **kwargs):
    if kwargs['mplayer']:
        player = '--mplayer'
    elif kwargs['mpv']:
        player = '--mpv'
    else:
        player = '--vlc'
    # parse magnet links
    magnetdata = torrentutils.parse_magnet(link)
    releasename = magnetdata['name']
    prettyprint(magnetdata)
    if releasename:
        subtitles = search(releasename)
        for index, sublink in subtitles.iteritems():
            index = colored(str(index), 'white')
            name = colored(sublink['name'], 'cyan')
            lang = colored(LANGUAGE, 'red', 'on_green')
            output = "{:12} {:20} {:50}".format(index, lang, name)
            print output
        subindex = raw_input("Choose Subtitle: \t")
        subindex = int(subindex)
        downlink = subtitles[subindex]['url']
        name = subtitles[subindex]['name']
        subname = download(downlink)
        peerflix = ['peerflix']
        peerflix.append(link)
        peerflix.append(player)
        peerflix.append('--subtitles')
        peerflix.append('/tmp/'+subname)
        peerflix.append('--not-on-top')
        subprocess.Popen(peerflix)
