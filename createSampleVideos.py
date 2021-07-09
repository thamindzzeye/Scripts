import os, subprocess, platform, sys
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re

# for i in *.mp4 *.m4v *.mov *.MP4 *.M4V *.MOV; do ffmpeg -i "$i" -vf scale=720:-2 -c:v libx264 "/Users/ricky/Movies/renders/samples/${i%.*}.mp4"; done


workingDir = os.getcwd()
destination = '~/Desktop/'
files = os.listdir(workingDir)
videoExtensions = ['mp4', 'mov', 'mkv', 'avi']
videosFound = []
selectionIndex = 1
print("""



Video Files Found:

""")

for file in files:
    split = file.split('.')
    if split[-1] in videoExtensions:
        #we have a video file
        videosFound.append(file)
        print(str(selectionIndex) + '. ' + file)
        selectionIndex += 1

selection = '1'
if len(videosFound) == 0:
    print("\n\nNo Video Files were Found. Exiting")
    sys.exit()
elif len(videosFound) > 1:
    selection = input('\n\nSelect which Video you want create a sample of: ')
else:
    selection = '1'

selectionIndex = int(selection) - 1

video = videosFound[selectionIndex]
outputFile = os.path.splitext(video)[0] + '.mp4'
output = os.path.join(destination, 'sample_' + outputFile)
print(output)

shouldUseX265 = False
lib = ''
tag = ''
if shouldUseX265:
    lib = 'libx265'
    tag = ' -tag:v hvc1'
else:
    lib = 'libx264'

command = 'ffmpeg -i ' + video + ' -vf scale=1280x720:flags=lanczos -c:v ' + lib + ' -crf 30 -preset fast -c:a aac -b:a 128k '+ tag + ' ' + output
print(command)
os.system(command)
