
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
import datetime
import shutil
import time


#Global Variables
debug = False

#Global Paths
workingDir = os.getcwd()
videoExts = ['.mkv', '.avi', '.mp4', '.mov']

def readFileToDict(filePath):
	if not os.path.exists(pathLastUpdatedData):
		data = {}
		writeDictToFile(data, pathLastUpdatedData)
	with open(filePath) as file:
		data = json.load(file)
	return data
	
def writeDictToFile(dictionary, filePath):
	with open(filePath, 'w') as file:
		json.dump(dictionary, file)
		
def clearConsole():
	if platform.system() == 'Windows':
		os.system('cls')
	else:
		os.system('clear')

def dateToString(date):
	return date.strftime('%m-%d-%Y %H:%M:%S')

def stringToDate(string):
	return datetime.strptime(string, '%m-%d-%Y %H:%M:%S')

def getFullPaths(root):
	# Initialize an empty list to store the full paths
	full_paths = []
	# Use os.walk to iterate over the root directory and its subdirectories
	for dirpath, dirnames, filenames in os.walk(root):
		# For each file in the current directory, append its full path to the list
		for filename in filenames:
			if checkExtensions(filename, videoExts):
				full_paths.append(os.path.join(dirpath, filename))
	# Return the list of full paths
	return full_paths

def checkExtensions(filename, extensions):
	# Get the file extension using os.path.splitext
	file_ext = os.path.splitext(filename)[1]
	# Check if the file extension is in the list of extensions
	return file_ext in extensions

def performActionOnVideo(filePath):
	command = 'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "' + filePath + '"'
	codec  = os.popen(command).readlines()[0].lower()
	if "h265" in codec or "hevc" in codec:
		return
	newFilePath = os.path.splitext(filePath)[0] + '_hvcx' + os.path.splitext(filePath)[1]
	if os.path.exists(newFilePath):
		print('hevc file already exists so skipping')
		return

	cmdStr = 'ffmpeg -i "' + filePath + '" -c:v libx265 -crf 28 -preset medium -codec:a copy -tag:v hvc1 "' + newFilePath + '"'
	os.system(cmdStr)

clearConsole()
print('Working directory is where you navigate to:\n')
print(': ' + workingDir)

def performClearOldCopiesOfVideos(filePath):
	file = os.path.splitext(filePath)[0]
	ext = os.path.splitext(filePath)[1]
	if '_hvcx' + ext in filePath:
		print("already encoded: " + filePath)
		return

	newFilePath = os.path.splitext(filePath)[0] + '_hvcx' + os.path.splitext(filePath)[1]
	if os.path.exists(newFilePath):
		# we have a old file that has a new encoded file. so this is a file we should delete
		os.remove(filePath)

current = datetime.datetime.now()
timestamp = current.strftime("%Y-%m-%d %H:%M:%S")
logName = 'Encode_' + timestamp + '.txt'
ans = input('1. Encode all videos to HEVC\n2. Remove old version of newly encoded files\nSelect: ')
if ans == '1':
	allVideos = getFullPaths(workingDir)
	for file in allVideos:
		performActionOnVideo(file)
elif ans == '2':
	allVideos = getFullPaths(workingDir)
	for file in allVideos:
		performClearOldCopiesOfVideos(file)









