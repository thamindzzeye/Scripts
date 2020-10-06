
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
from pathlib import Path


destination = '~/Downloads/'
#if not os.path.exists(destination):
#    os.makedirs(destination)

print("""



rroy: test


For the File name structure
example: SomeRenderScene00001.png
the structure would be:   SomeRender%05d.png
%0 followed by the number of numbers in the file name (00001 = 5)
and include the file extension too ".png" or ".jpg" etc


""")
fileInput = input('What is the file name structure of the image? ')
framerate = input('What framerate do you want for the movie? ')
outputName = input('What Should the Video be named (no extension)? ')
workingDir = os.getcwd()

fileLocation = '~/Downloads/' + outputName + '.mp4'

#ffmpeg -framerate 24 -i $fileInput -c:v libx264 -pix_fmt yuv420p $fullPath
command = 'ffmpeg -framerate ' + framerate + ' -i \'' + fileInput + '\' -c:v libx264 -pix_fmt yuv420p ' + fileLocation
print(command)
os.system(command)

print("""

Complete






""")
