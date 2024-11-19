import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
from subprocess import run
import shutil

progressFolder = destination = os.path.expanduser('~/Downloads/YoutubeVids/Progress/')
destination = os.path.expanduser('~/Downloads/YoutubeVids')
videoEndCapPath = os.path.expanduser('~/Code/videoEndCap.mp4')

def getMediaLength(filename):
    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration

def isVideoFile(file):
	validExts = ['.mp4', '.mov','.m4v','.avi']
	ext = Path(file).suffix.lower()
	if ext in validExts:
		return True
	else:
		return False

def shortenVideoIfNeeded(path, file):
	# Finally let's check if its more than 15 minutes and clip it and add the video end cap
	duration = getMediaLength(path)
	if float(duration) > 888:
		# Too long we need to trim
		newFile = file.replace('.mp4','_linkedIn.mp4')
		command = 'ffmpeg -ss 00:00:00 -to 00:14:48 -i "' + path + '" -c copy "' + os.path.join(destination, newFile) + '"'
		os.system(command)
		


def encodeNeededVideos():
	files = os.listdir(progressFolder)
	for file in files:
		if isVideoFile(file):

			fullPath = os.path.join(progressFolder, file)
			newPath = os.path.join(destination, file)
			# Let's remove special characters like $ to be safe $1 for example causes problems
			if fullPath != fullPath.replace("$",""):
				# we have a situation where we gotta rename the file then run everything
				os.rename(fullPath, fullPath.replace("$","USD"))
				fullPath = fullPath.replace("$","USD")
				newPath = newPath.replace("$","USD")



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
			shortenVideoIfNeeded(newPath, file)
			



fileLocation = '\'~/Downloads/YoutubeVids/Progress/%(title)s.%(ext)s\''

if not os.path.exists(progressFolder):
    os.makedirs(progressFolder)


url = input('What is the youtube (share) URL? :  ')
url = url.replace('?feature=shared','')
command = 'yt-dlp -f \'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio\' --merge-output-format mp4 --output ' + fileLocation + ' ' + '\'' + url + '\''
print(command)
os.system(command)
encodeNeededVideos()


print("""

Complete

""")
