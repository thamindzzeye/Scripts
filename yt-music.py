
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
from pathlib import Path


isWindows = platform.system() == 'Windows'
destination_itunes = ''
destination_folder = 'C:\Script_Outputs\youtube' + '\\'



os_user = 'ricky'
if isWindows:
      destination_itunes = ('C:\\Users\\' + os_user + '\\Music\\iTunes\\iTunes Media\\Automatically Add to iTunes\\')
else:
      print('Mac Detected')
      destination_itunes = str(Path.home()) + '/Music/Music/Media.localized/Automatically Add to Music.localized'
      destination_folder = str(Path.home()) + '/script_output/youtube/'
      print(destination_itunes)
      print(destination_folder)


if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

if os.path.exists(destination_folder + 'temp.mp3'):
    os.remove(destination_folder + 'temp.mp3')

url = input('What is the youtube URL? :  ')

command = 'youtube-dl -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 ' + url + ' -o "' + destination_folder + 'temp.mp3"'
print(command)
os.system(command)

artist = input('what is the name of the artist? : ')
title = input('what is the name of the title? : ')
filename = artist.title() + ' - ' + title.title() + '.mp3'
save_to_itunes = input('Auto add to your iTunes Library? (y)es / (n)o : ')
full_path = ''
if save_to_itunes == 'y':
    os.system('iTunes.exe')
    full_path = destination_itunes + '/' + filename
else:
    full_path = destination_folder + '/' + filename

command = 'ffmpeg -i "' + destination_folder + '/temp.mp3"' + ' -id3v2_version 3 -write_id3v1 1 -metadata artist="' + artist.title() + '" -metadata title="' + title.title() + '" -c:a libmp3lame "' + full_path + '"'
print('\n\n' + command + '\n\n')
os.system(command)

os.remove(destination_folder + 'temp.mp3')

print("""

Copmlete

""")
