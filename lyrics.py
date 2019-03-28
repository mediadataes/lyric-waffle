#!/usr/bin/env python

import csv
import os
import re
import sys
import datetime

from difflib import SequenceMatcher
from functools import partial
from multiprocessing import Pool

from identify import Song
from lyricsmaster.providers import Genius, LyricWiki
from cachier import cachier


TAG = re.compile(r'^\[[\w -_:]+\]$')
# number of simultaneous processes
NP = 10


def similar(a, b):
    return SequenceMatcher(lambda x: x in " -_|,", a, b).ratio()


def save_song(output, song, lyric):
    lines = lyric.lyrics
    output_dir = os.path.join(output, 'songs')
    os.makedirs(output_dir, exist_ok=True)
    filename = f'{song.title}.csv'.lower()
    path = os.path.join(output_dir, filename)
    with open(path, 'w') as f:
        stanza = 1
        verse = 1
        for line in map(str.strip, lines.splitlines()):
            if not line:
                if verse > 1:
                    stanza += 1
                continue

            if TAG.match(line):
                continue

            f.write(f'"{stanza}";"{verse}";"{line}"\n')
            verse += 1


@cachier(stale_after=datetime.timedelta(days=3))
def get_albums(artist, provider='genius'):
    if provider == 'genius':
        provider = Genius()
    elif provider == 'wiki':
        provider = LyricWiki()
    disc = provider.get_lyrics(artist=artist)
    return disc


def get_lyrics(output, song, provider='genius'):
    print(f'get lyrics: {song.title}')
    title = song.title.lower()

    discs = []
    for artist in song.artists:
        print(f'Looking for the artist discography {artist}')
        disc = get_albums(artist, provider)
        if disc:
            discs.append(disc)

    for disc in discs:
        for album in disc:
            for s in album:
                if not s:
                    continue

                ratio = similar(s.title.lower(), title)
                if ratio > 0.8:
                    save_song(output, song, s)
                    return

    # fallback to other provider
    if provider == 'genius':
        get_lyrics(output, song, provider='wiki')
        return

    # TODO: log out this output to a file?
    artists = ', '.join(song.artists)
    print(f'Cannot find the song: "{song.title}" from {artists}',
          file=sys.stderr)


class Lyrics:
    def __init__(self, output='output', songs_file='songs.csv'):
        self.output = output
        self.songs_file = songs_file

    def run(self):
        path = os.path.join(self.output, self.songs_file)
        songs = []
        with open(path, newline='') as csvfile:
            songsreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in songsreader:
                song = Song.from_csv(row)
                songs.append(song)

        with Pool(NP) as p:
            p.map(partial(get_lyrics, self.output), songs)


if __name__ == '__main__':
    lyrics = Lyrics()
    lyrics.run()
