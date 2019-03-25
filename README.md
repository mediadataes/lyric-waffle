# lyric waffle

Download popular lyrics from different resources

## Docker

To build the docker image run:

```
$ docker build -t lyric-waffle .
```

You should need to set the configuration in an environment file called ".env",
for example this .env:

```
YOUTUBE_APIKEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Run test

```
$ docker run --env-file .env --rm -ti lyric-waffle python test.py
```

### Song identify

```
$ docker run --env-file .env --rm -ti -v $PWD/songs.csv:/app/songs.csv lyric-waffle python identify.py
```

### Lyrics download

```
$ docker run --env-file .env --rm -ti -v $PWD/songs.csv:/app/songs.csv lyric-waffle python lyrics.py
```

There are some scripts that run this exact commands so you can run:

 * ./test
 * ./identify
 * ./lyrics
