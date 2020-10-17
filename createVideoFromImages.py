
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
from pathlib import Path


destination = '~/Downloads/'
#if not os.path.exists(destination):
#    os.makedirs(destination)

print("""






For the File name structure
example: SomeRenderScene00001.png
the structure would be:   SomeRender%05d.png
%0 followed by the number of numbers in the file name (00001 = 5)
and include the file extension too ".png" or ".jpg" etc


""")
fileInput = input('What is the file name structure of the image? : ')
framerate = input('What framerate do you want for the movie? : ')
outputName = input('What Should the Video be named (no extension)? : ')
print("""
Do you want the alpha channel in the video?
The background will be invisible, but the file size will be MUCH larger

""")
isAlpha = input('Use Alpha Channel? (y)es / (n)o) : ')
workingDir = os.getcwd()

fileLocation = '~/Downloads/' + outputName + '.mp4'

if (isAlpha == 'y' or isAlpha == 'Y'):
    command = 'ffmpeg -framerate ' + framerate + ' -i \'' + fileInput + '\' -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov ' + fileLocation
    #ffmpeg -framerate $framerate -i $fileInput -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov $fullPath
else:
    command = 'ffmpeg -framerate ' + framerate + ' -i \'' + fileInput + '\' -c:v libx264 -pix_fmt yuv420p ' + fileLocation
print(command)
os.system(command)

print("""

Complete






""")
