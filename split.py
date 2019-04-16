#!/usr/bin/env python

import argparse
import os
import sys
import subprocess


def duration(video):
    command = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1'
    return float(subprocess.check_output(command.split(' ') + [video]).strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split a video in frames.')
    parser.add_argument('-s', default=10,
        help='Number of seconds between frames')
    parser.add_argument('-x', action='store_true',
        help='Cut by scene instead of seconds')
    parser.add_argument('-w', metavar='WxH', default='640x360',
        help='Size of the output frames')
    parser.add_argument('-o', default='png', choices=['png', 'jpg'],
        help='Output frame format, png or fpg')
    parser.add_argument('video', nargs='*',
        help='One or more videos to split')

    args = parser.parse_args()

    frames = args.x
    seconds = int(args.s)
    outformat = args.o
    size = args.w
    videos = args.video

    ffmpeg_args = []

    if frames:
        ffmpeg_args += ['-vf', 'select=gt(scene\,0.4)', '-vsync', 'vfr']

    ffmpeg_args += ['-s', size]

    output_dir = os.path.join('output', 'frames')
    os.makedirs(output_dir, exist_ok=True)

    for video in videos:
        args = [i for i in ffmpeg_args]

        basename = os.path.basename(video)
        output = os.path.join(output_dir, basename)
        os.makedirs(output, exist_ok=True)
        output = os.path.join(output, f'frame%04d.{outformat}')

        if not frames:
            s = seconds
            args += ['-ss', '3', '-r', f'1/{s}']

        subprocess.run(['ffmpeg', '-i', f'{video}'] + args + [output])
