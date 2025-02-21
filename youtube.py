import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
from subprocess import run
import shutil
import yt_dlp

progressFolder = destination = os.path.expanduser('~/Downloads/YoutubeVids/Progress/')
destination = os.path.expanduser('~/Downloads/YoutubeVids')
fontPath = os.path.expanduser('~/Library/Fonts/SF-Pro-Display-Black.otf')

def isVideoFile(file):
	validExts = ['.mp4', '.mov','.m4v','.avi']
	ext = Path(file).suffix.lower()
	if ext in validExts:
		return True
	else:
		return False

def encodeNeededVideos(sourceText):
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
			command = 'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "' + fullPath + '"'
			vidRes  = os.popen(command).readlines()[0].lower().split('x')
			vidResX = vidRes[0]
			print('Video RES')
			print(vidRes)
			
			ratio = int(vidResX) / 1920
			bv = 2500000 * ratio
			maxRate = 3500000 * ratio
			if sourceText:
				sourceText = " -vf " + f"drawtext=fontfile='{fontPath}':text='{sourceText}':fontcolor=white:fontsize={int(24 * ratio)}:box=1:boxcolor=black@0.5:boxborderw={int(10 * ratio)}:x={int(30 * ratio)}:y=h-th-{int(30 * ratio)}"

			if "h264" in codec:
				if sourceText:
					command = 'ffmpeg -i "' + fullPath + '"' + sourceText + ' -c:v h264_videotoolbox -b:v '+ str(bv) + ' -maxrate ' + str(maxRate) + ' -bufsize 6000k -preset fast -codec:a copy "' + newPath + '"'
					os.system(command)
					os.remove(fullPath)
				else:
					shutil.move(fullPath, newPath)
			else:
				print('Video has Codec: ' + codec + ' which is not supported. converting now...')
				
				command = 'ffmpeg -i "' + fullPath + '"' + sourceText + ' -c:v h264_videotoolbox -b:v '+ str(bv) + ' -maxrate ' + str(maxRate) + ' -bufsize 6000k -preset fast -codec:a copy "' + newPath + '"'
				os.system(command)
				os.remove(fullPath)


def download_highest_quality(url, save_path):
    # Define options for yt-dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Download best video and best audio
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',  # Convert the video if necessary
            'preferedformat': 'mp4',  # Convert to MP4 format
        }],
        'outtmpl': save_path,  # Set the output filename and path
        'merge_output_format': 'mp4',  # Ensure merging of audio and video in MP4 format
        'socket_timeout': 30,  # Increase timeout (default is 10 seconds)
        'retries': 5,
    }

    # Create a yt-dlp instance and download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


fileLocation = os.path.join(destination, 'Progress/%(title)s.%(ext)s')

if not os.path.exists(progressFolder):
    os.makedirs(progressFolder)




url = input('What is the youtube (share) URL? :  ')
url = url.replace('?feature=shared','')
sourceText = input('Source Text? (blank for none): ')
if sourceText:
	sourceText = "▶ // " + sourceText

download_highest_quality(url, fileLocation)

encodeNeededVideos(sourceText)

print("""

Complete

""")
