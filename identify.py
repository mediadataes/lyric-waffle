#!/usr/bin/env python

import re
import sys

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from requests_html import HTMLSession

from config import YOUTUBE_APIKEY, YOUTUBE, MUSICLIST

@dataclass
class Song:
    artists: [str]
    title: str
    gender: Optional[str] = None
    length: Optional[int] = None
    created: Optional[datetime] = None

    def to_csv(self):
        title = self.title
        created = self.created or ""
        length = self.length or ""
        gender = self.gender or ""
        artists = ', '.join(self.artists)
        return f'"{title}";"{artists}";"{created}";"{length}";"{gender}"\n'

    @classmethod
    def from_csv(cls, row):
        title, artists, created, length, gender = row
        artists = artists.split(', ')
        created = datetime.fromisoformat(created)

        s = Song(title=title,
                 artists=artists,
                 gender=gender,
                 length=length,
                 created=created)
        return s


class Provider:
    def download(self):
        raise NotImplementedError


RE_ARTIST = '([\w\. ]+)([,&/]\s)?'
RE_ARTISTS = f"(?P<artists>({RE_ARTIST})+)"
RE_TITLE = r"(?P<title>[\w:'_\s]+)"
RE1 = re.compile(f"{RE_ARTISTS}\s*[-|]\s*{RE_TITLE}", flags=re.UNICODE)
RE2 = re.compile(f"{RE_TITLE}\s*[-|]\s*{RE_ARTISTS}", flags=re.UNICODE)


class YoutubeProvider(Provider):
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    PART = 'id,snippet,contentDetails,status'

    def __init__(self, playlist, apikey):
        self.playlist = playlist
        self.apikey = apikey
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME,
                             self.YOUTUBE_API_VERSION,
                             developerKey=apikey)

    def download(self):
        songs = []
        plist = self.youtube.playlistItems()
        req = plist.list(playlistId=self.playlist, part=self.PART)
        response = req.execute()
        while response:
            for item in response['items']:
                info = item['snippet']
                title = info['title']

                match = RE1.match(title)
                if not match:
                    match = RE2.match(title)
                if not match:
                    print("Error, invalid title format:", title)
                    continue

                artists = match.group('artists')
                title = match.group('title')

                artists = [a.strip() for a, _ in re.findall(RE_ARTIST, artists, flags=re.UNICODE)]
                title = title.strip()

                s = Song(artists=artists, title=title, created=datetime.now())
                songs.append(s)
            req = plist.list_next(req, response)
            if not req:
                break
            response = req.execute()

        return songs


class MusicListProvider(Provider):
    # https://www.musiclist.es/40-principales
    def __init__(self, list_):
        self.list_ = list_

    def download(self):
        songs = []

        session = HTMLSession()
        r = session.get(f'https://www.musiclist.es/{self.list_}')
        ul = r.html.find('ul.chart', first=True)
        for li in ul.find('li'):
            title = li.find('.chart-content h4', first=True).text
            artists = li.find('.chart-content p', first=True).text
            artists = [a.strip() for a, _ in re.findall(RE_ARTIST, artists, flags=re.UNICODE)]
            s = Song(artists=artists, title=title, created=datetime.now())
            songs.append(s)

        return songs


class Identify:
    def __init__(self):
        self.providers = []

        for y in YOUTUBE:
            p = YoutubeProvider(y, YOUTUBE_APIKEY)
            self.providers.append(p)

        for m in MUSICLIST:
            self.providers.append(MusicListProvider(m))

    def run(self):
        songs = []
        for p in self.providers:
            songs += p.download()

        with open('output/songs.csv', 'w') as f:
            written = {}
            for s in songs:
                if s.title in written:
                    continue

                written[s.title] = s
                f.write(s.to_csv())


if __name__ == '__main__':
    # TODO: parse arguments
    identify = Identify()
    identify.run()
