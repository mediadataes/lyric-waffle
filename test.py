import os
import unittest

from googleapiclient.discovery import build
from requests_html import HTMLSession


class TestAPIs(unittest.TestCase):

    def test_youtube(self):
        YOUTUBE_API_SERVICE_NAME = 'youtube'
        YOUTUBE_API_VERSION = 'v3'
        PART = 'id,snippet,contentDetails,status'
        LIST = 'PL4XLEC-MUq2uP2OhrGWdOErGUDrEquhqi'
        YOUTUBE_APIKEY = os.environ['YOUTUBE_APIKEY']

        youtube = build(YOUTUBE_API_SERVICE_NAME,
                             YOUTUBE_API_VERSION,
                             developerKey=YOUTUBE_APIKEY)
        plist = youtube.playlistItems()

        req = plist.list(playlistId=LIST, part=PART)
        response = req.execute()

        self.assertTrue('items' in response)
        self.assertTrue(len(response['items']) > 0)

        for item in response['items']:
            self.assertTrue('snippet' in item)
            self.assertTrue('title' in item['snippet'])

    def test_musiclist(self):
        LIST = '40-principales'
        session = HTMLSession()
        r = session.get(f'https://www.musiclist.es/{LIST}')
        ul = r.html.find('ul.chart', first=True)

        self.assertTrue(bool(ul))
        self.assertTrue(len(ul.find('li')) > 0)

        for li in ul.find('li'):
            title = li.find('.chart-content h4', first=True)
            artists = li.find('.chart-content p', first=True)

            self.assertTrue(bool(title))
            self.assertTrue(bool(artists))

if __name__ == '__main__':
    unittest.main()
