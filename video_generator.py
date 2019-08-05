
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
import shutil


frames_folder = 'C:\\Script_Outputs\\frames_temp'
destination_folder = 'C:\\Script_Outputs\\vid_generated'

if os.path.exists(frames_folder):
    shutil.rmtree(frames_folder)
os.makedirs(frames_folder)

print('Welcome to Video Generator!\n All Pictures should be in .png format\nLooking for pictures called\nfront.png, mid.png back.png and(or) farback.png')

front = 'front.png'
mid = 'mid.png''
far = 'far.png'

if os