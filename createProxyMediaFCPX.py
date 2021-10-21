
import os, subprocess, platform, PIL, shutil, sys, urllib, requests, re, selenium, time, io
from os import listdir
from os.path import isfile, join
import pathlib as pathlib
from pathlib import Path

from PIL import Image
from bs4 import BeautifulSoup
import urllib.parse as urlparse

#REGEX: (?i)\[\"http.*\.(jpg|png|tiff|jpeg|svg).*\",[0-9].*,[0-9].*\](\n|.*)*?}

def createProxyMediaForVideoPath(fullPath):
    return []

def getListOfOriginalMediaForEvent(eventPath):
    if not os.path.isdir(os.path.normpath(eventPath)):
        return []

    files = os.listdir(eventPath)
    if 'Original Media' not in files:
        return []
    mediaPath = os.path.join(eventPath, 'Original Media')
    files = os.listdir(mediaPath)
    results = []
    for file in files:
        if isFileAVideo(file):
            results.append(os.path.join(mediaPath, file))

    return results

def isFileAVideo(file):
    ext = pathlib.Path(file).suffix.lower()
    matches = ['.mp4', '.mov', '.avi', '.m4v', '.mpeg', '.mpg', '.mkv']
    if ext in matches:
        return True

    return False


def isProjectLocal(folderPath):
    print(folderPath)
    size = getFolderSize(folderPath)
    print(str(size))

def getFolderSize(folderPath):
    size = 0
    for file in Path(folderPath).rglob('*'):

        size += file.stat().st_size

    return size

def removeUnwantedFiles(files):
    result = files
    stuffToRemove = ['Icon', 'Ad Spots', '.DS_Store']
    for remove in stuffToRemove:
        if remove in result:
            result.remove(remove)
    result = [f for f in result if not f.startswith('.')]
    result = [f for f in result if not f.startswith('_')]

    return result

os.system('clear')
rootPath = os.path.expanduser('~')
rootPath = os.path.join(rootPath, 'Two Bit da Vinci Dropbox/Two Bit Media')

if not os.path.exists(rootPath):
    print('Dropbox is NOT setup! Setup Two Bit da Vinci Dropbox First then try again')
    sys.exit()

projectTypes = os.listdir(rootPath)
projectTypes = removeUnwantedFiles(projectTypes)



index = 1
for type in projectTypes:
    print(str(index) + '. ' + type)
    index = index + 1

projectIndex = input('Which Project Are You Working on (number)? :')
rootPath = os.path.join(rootPath, projectTypes[int(projectIndex) - 1])
os.system('clear')
print(rootPath + '\n\n')
projects = os.listdir(rootPath)
projects = removeUnwantedFiles(projects)
index = 1
for project in projects:
    print(str(index) + '. ' + project)
    index = index + 1

projectIndex = input('\n\nWhich Project Are You Working on (number)? :')
rootPath = os.path.join(rootPath, projects[int(projectIndex) - 1])
os.system('clear')
print(rootPath + '\n\n')

events = os.listdir(rootPath)
events = removeUnwantedFiles(events)
fcpxProjects = []
for event in events:
    if event.__contains__('.fcpbundle'):
        fcpxProjects.append(event)


#At this point we should just have 1 final cut project.
# But if we don't lets ask the user which thye want to use
project = ''
index = 1

if len(fcpxProjects) == 1:
    project = os.path.join(rootPath, fcpxProjects[0])
else:
    for fcpxProject in fcpxProjects:
        print(str(index) + '. ' + fcpxProject)
        index = index + 1
    print('\n\n')
    projectIndex = input('Which Project Do you want to Run (number)? : ')
    project = os.path.join(rootPath, fcpxProjects[int(projectIndex) - 1])

projectPath = project
os.system('clear')

# We finally have the project we want to work with!
# Next lets get all the sub events we need to work on

files = os.listdir(projectPath)
events = removeUnwantedFiles(files)

allVideos = []
overrideExistingProxies = False
overrideAsked = False
answer = input('If Proxies Exist, over write them, or skip existing? (o)verwrite / (s)kip :')
if answer in ['o', 'O', 'overwrite', 'override']:
    overrideExistingProxies = True
for event in events:
    eventPath = os.path.join(projectPath, event)
    files = getListOfOriginalMediaForEvent(eventPath)

    if len(files) == 0:
        continue
    transcodedPath = os.path.join(eventPath, 'Transcoded Media')
    proxyPath = os.path.join(transcodedPath, 'Proxy Media')
    highQualityPath = os.path.join(transcodedPath, 'High Quality Media')

    for video in files:
        fileName = pathlib.PurePath(video).name
        proxyFile = os.path.join(proxyPath, fileName)
        ext = pathlib.Path(proxyFile).suffix.lower()
        proxyFile = proxyFile.replace(ext, '.mov')
        print(proxyFile)
        
        if os.path.exists(proxyFile):
            if overrideExistingProxies:
                os.remove(proxyFile)
            else:
                continue

        command = 'ffmpeg -i \'' + video + '\' -vcodec prores -profile:v 0 -acodec pcm_s16le -s 1280x720 -filter:v fps=15 \'' +  proxyFile + '\''
        os.system(command)
        # print(command)




sys.exit()
