
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
from pathlib import Path


destination = '~/Downloads/YoutubeVids/'
# fileLocation = '~/Downloads/YoutubeVids/(title)s.%(ext)s'
fileLocation = '\'~/Downloads/YoutubeVids/%(title)s.%(ext)s\''
if not os.path.exists(destination):
    os.makedirs(destination)


url = input('What is the youtube (share) URL? :  ')

command = 'yt-dlp -f \'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio\' --merge-output-format mp4 --output ' + fileLocation + ' ' + '\'' + url + '\''
print(command)
os.system(command)

print("""

Complete

""")
