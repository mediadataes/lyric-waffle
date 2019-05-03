#!/usr/bin/env python

import argparse
import csv
import os
import sys
import datetime
import itertools

import youtube_dl

from identify import Song


class Logger(object):
    def __init__(self, outfile):
        self.outfile = open(outfile, 'w')

    def __del__(self):
        self.outfile.close()

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.outfile.write(msg + '\n')


class Video:
    def __init__(self, songs_file=None):
        self.output = 'output'
        if songs_file:
            self.path = songs_file
        else:
            filename = datetime.datetime.now().strftime('songs-%Y-%m-%d.csv')
            self.path = os.path.join('output', filename)

    def run(self):
        songs = []
        with open(self.path, newline='') as csvfile:
            songsreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in itertools.islice(songsreader, 1, None):
                song = Song.from_csv(row)
                songs.append(song)

        orig_path = os.path.abspath(os.curdir)
        os.makedirs(self.output, exist_ok=True)
        filename = os.path.join(orig_path, self.output, 'video-errors.txt')
        archive = os.path.join(orig_path, self.output, 'video-archive.txt')

        videos = os.path.join(self.output, 'videos')
        os.makedirs(videos, exist_ok=True)

        opts = {
            'logger': Logger(filename),
            'download_archive': archive,
            'sleep_interval': 1,
            'max_sleep_interval': 2,
            'outtmpl': '%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
        }

        os.chdir(videos)
        with youtube_dl.YoutubeDL(opts) as ydl:
            for song in songs:
                try:
                    ydl.download([song.youtube_id])
                except Exception as e:
                    print(f'Error: {e}')
                    print(f'Error downloading video with ID: {song.youtube_id}')
        os.chdir(orig_path)

        print()
        print(f'Take a look to the errors file {filename}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download youtube video.')
    parser.add_argument('songs', nargs='?',
        help='The CSV file with songs to download, generated by identify.py')

    args = parser.parse_args()

    video = Video(songs_file=args.songs)
    video.run()
