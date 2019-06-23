# lyric waffle

Download popular lyrics from different resources

## Docker

To build the docker image run:

```
$ docker build -t mediadataes/lyric-waffle .
```

You should need to set the configuration in an environment file called ".env",
for example this .env:

```
YOUTUBE_APIKEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Run test

```
$ docker run --env-file .env --rm -ti mediadataes/lyric-waffle python test.py
```

### Song identify

```
$ docker run --env-file .env --rm -ti -v $PWD/output:/app/output mediadataes/lyric-waffle python identify.py
```

### Lyrics download

```
$ docker run --rm -ti -v $PWD/output:/app/output mediadataes/lyric-waffle python lyrics.py
```

This command will download all songs lyrics in the songs.csv file to the output/songs folder

### Youtube video download

```
$ docker run --rm -ti -v $PWD/output:/app/output mediadataes/lyric-waffle python videos.py
```

This command will download all videos in the songs.csv file to the output/videos folder

### video split

```
$ docker run --rm -ti -v $PWD/output:/app/output mediadataes/lyric-waffle python split.py [video]
```

This is the command help:

```
usage: split.py [-h] [-s S] [-x] [-w WxH] [-o {png,jpg}] [video [video ...]]

Split a video in frames.

positional arguments:
  video         One or more videos to split

optional arguments:
  -h, --help    show this help message and exit
  -s S          Number of seconds between frames
  -x            Cut by scene instead of seconds
  -w WxH        Size of the output frames
  -o {png,jpg}  Output frame format, png or fpg
```

This command will split a video into frames and save to output/frames/VIDEO

### helper scripts

There are some scripts that run this exact commands so you can run:

 * ./test
 * ./identify
 * ./lyrics
 * ./videos
 * ./split
