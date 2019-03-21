#!/usr/bin/env python


from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from config import YOUTUBE_APIKEY, YOUTUBE, MUSICLIST

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

@dataclass
class Song:
    artists: [str]
    title: str
    gender: Optional[str] = None
    length: Optional[int] = None
    created: Optional[datetime] = None


class Provider:
    def download(self):
        raise NotImplementedError

    def save(self, dest):
        songs = self.download()
        with open(dest, 'a') as f:
            for s in songs:
                f.write(f'"{s.title}";"{s.artists}";"{s.created}";"{s.length}";"{s.gender}"\n')


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

                # TODO: normalize artists and title

                try:
                    # TODO: manage '|' as split
                    split = title.index('-')
                except:
                    print("Error, invalid title format:", title)
                    continue

                artists = list(map(str.strip, title[:split].strip().split(',')))
                title = title[split+1:].strip()

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
        return []


class Identify:
    def __init__(self):
        self.providers = []

        for y in YOUTUBE:
            p = YoutubeProvider(y, YOUTUBE_APIKEY)
            self.providers.append(p)

        for m in MUSICLIST:
            self.providers.append(MusicListProvider(m))

    def run(self):
        for p in self.providers:
            p.download()


if __name__ == '__main__':
    # TODO: parse arguments
    identify = Identify()
    identify.run()
