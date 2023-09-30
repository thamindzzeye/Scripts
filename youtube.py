import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
from subprocess import run
import shutil

progressFolder = destination = os.path.expanduser('~/Downloads/YoutubeVids/Progress/')
destination = os.path.expanduser('~/Downloads/YoutubeVids')

def isVideoFile(file):
	validExts = ['.mp4', '.mov','.m4v','.avi']
	ext = Path(file).suffix.lower()
	if ext in validExts:
		return True
	else:
		return False

def encodeNeededVideos():
	files = os.listdir(progressFolder)
	for file in files:
		if isVideoFile(file):
			fullPath = os.path.join(progressFolder, file)
			newPath = os.path.join(destination, file)
			command = 'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "' + fullPath + '"'
			codec  = os.popen(command).readlines()[0].lower()
			print('------------------------------------------\nWorking on: ' + file)
			if "h264" in codec:
				shutil.move(fullPath, newPath)
			else:
				print('Video has Codec: ' + codec + ' which is not supported. converting now...')
				command = 'ffmpeg -i "' + fullPath + '" -c:v libx264 -codec:a copy "' + newPath + '"'
				os.system(command)
				os.remove(fullPath)



fileLocation = '\'~/Downloads/YoutubeVids/Progress/%(title)s.%(ext)s\''



if not os.path.exists(progressFolder):
    os.makedirs(progressFolder)


url = input('What is the youtube (share) URL? :  ')

command = 'yt-dlp -f \'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio\' --merge-output-format mp4 --output ' + fileLocation + ' ' + '\'' + url + '\''
print(command)
os.system(command)

encodeNeededVideos()

print("""

Complete

""")
