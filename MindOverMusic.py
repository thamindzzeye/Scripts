
import os, subprocess, platform, random
from datetime import date, datetime
from os import listdir
from os.path import isfile, join
from pathlib import Path
from mutagen.mp3 import MP3

def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')

def getSongSeconds(path):
    audio = MP3(path)
    audio_info = audio.info
    length_in_secs = int(audio_info.length)
    return length_in_secs

desiredDurationInHours = 3
desiredDuration = desiredDurationInHours * 3600 + 1200

print('\n\n\n Don\'t forget to install : pip3 install mutagen')
print('Don\'t forget to install : brew install mp3wrap')

path_lofi = '/Volumes/Dorne/Music/Lofi'
path_relax = '/Volumes/Dorne/Music/Relaxation'
path_test = '/Volumes/Dorne/Music/Test'
path_videoRecord = '/Volumes/Dorne/Music/VideoRecord'
path = ''

type = input('What Style do you want (L) for Lofi (R) for Relaxation :')

files = ''

if type == 'L':
    path = path_lofi
    type = 'Lofi'
elif type == 'R':
    path = path_relax
    type = 'Relaxation'
elif type == 'T':
    path = path_test
    type = 'Test'


files = os.listdir(path)

fileBase = datetime.now().strftime("%Y%m%d_%H%M%S_") + type
textFileName = fileBase + '.txt'
outputFilename = fileBase + '.mp3'
outputPath = os.path.join(get_download_path(), outputFilename)
textFilePath = os.path.join(path_videoRecord, textFileName)
my_file = open(textFilePath,"w+")
fileContent = ''
totalLengthInSecs = 0
while len(files) > 0:
    numElements = len(files) - 1
    index = random.randint(0, numElements)
    file = files[index]
    if file == '.DS_Store':
        continue

    print(file)
    files.remove(files[index])
    filepath = os.path.join(path, file)
    fileContent += "file \'" + filepath + '\'\n'
    seconds = getSongSeconds(filepath)
    totalLengthInSecs += seconds
    if totalLengthInSecs > desiredDuration:
        break
my_file.write(fileContent)
my_file.close()

print(textFilePath)
command = 'ffmpeg -f concat -safe 0 -i ' + textFilePath + ' -c copy ' + outputPath
print(command)
os.system(command)
