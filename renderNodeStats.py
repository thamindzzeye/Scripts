
import os, subprocess, platform, sys, json
from enum import Enum
from os import listdir
from os.path import isfile, join
from pathlib import Path
from threading import Timer
import re
from datetime import datetime
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#Global Variables
lastTime = time.time()
lastFile = ''
pathRendersRoot = ['/Volumes/Scratch/Renders/Active Renders', 'R:\\Active Renders']
pathActiveProjects = ['/Volumes/Scratch/Renders/Data/activeProjects.json', Path('R:\\Data\\activeProjects.json')]
pathDataRoot = ['/Volumes/Scratch/Renders/Data/Projects', Path('R:\\Data\\Projects')]

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Global Helper Functions  ----------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def getComputerName():
	name = platform.node()
	parts = name.split('.')
	return parts[0]

def systemPath(pathArray):
	index = int(platform.system() == 'Windows')
	path = pathArray[index]
	return path

def linuxPath(path):
	path = path.replace('\\','/')
	parts = path.split(':')
	path = '/cygdrive/' + parts[0] + parts[1]
	return path

def monitorDirectory():
	path = ['/Volumes/Scratch/Renders/Data/Nodes', 'R:\\Data\\Nodes']
	return systemPath(path)

def readJsonFile(path, errorDefault):
	with open(path, "r") as jsonData:
		data = json.load(jsonData)
		return data
	return errorDefault

def writeJsonToFile(dataDict, filePath):
	with open(filePath, 'w', encoding='utf-8') as f:
		json.dump(dataDict, f, ensure_ascii=False, indent=4)

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Watcher Class Functions  ----------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

class OnMyWatch:
	# Set the directory on watch
 
	def __init__(self):
		self.observer = Observer()
 
	def run(self):
		event_handler = Handler()
		self.observer.schedule(event_handler, monitorDirectory(), recursive = True)
		self.observer.start()
		try:
			while True:
				time.sleep(5)
		except:
			self.observer.stop()
			print("Observer Stopped")
 
		self.observer.join()

class Handler(FileSystemEventHandler):

	@staticmethod
	def on_any_event(event):
		if event.is_directory:
			return None

		global lastTime
		global lastFile

		#Prevent Duplicate Calls
		file = event.src_path
		newTime = t = time.time()
		if file == lastFile and newTime < lastTime + 5:
			return None
		elif event.event_type == 'created' or event.event_type == 'modified':
			# Event is created, you can process it now
			parseNewJsonFile(event.src_path)
			lastFile = file
			lastTime = newTime

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------------- Core Analytics Functions  ---------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def parseNewJsonFile(filePath):
	print('File: ' + filePath)
	if not filePath.endswith('.json'):
		return
	if not os.path.exists(filePath):
		return
	newArray = readJsonFile(filePath, [])
	split = filePath.split('\\')
	computer = split[-2]
	projectName = split[-1].replace('.json', '')

	framesFolder = os.path.join(systemPath(pathRendersRoot), projectName)
	if not os.path.exists(framesFolder):
		#This shouldn't happen but the frames folder isn't present
		return
	activeProjects = readJsonFile(systemPath(pathActiveProjects), [])
	activeProject = {}
	for project in activeProjects:
		if project['blendName'] == projectName + '.blend':
			activeProject = project
	if len(activeProject.keys()) == 0:
		return
	startFrame = int(activeProject['startFrame'])
	endFrame = int(activeProject['endFrame'])
	
	dataPath = os.path.join(systemPath(pathDataRoot), projectName + '.json')
	dataDict = {}
	if os.path.exists(dataPath):
		#this is just final json file we write to disk
		dataDict = readJsonFile(dataPath,{})
	else:
		#file didn't exist so let's create the properties
		dataDict['frames'] = {}

	hasChanged = False
	framesData = dataDict['frames']
	for frame, duration in newArray.items():

		if frame in framesData:
			#already exists
			d = framesData[frame]
			if computer == d[0] and duration == d[1]:
				continue

		#new frame!
		hasChanged = True
		#Format - Frame - RenderNodeName - RenderTime - Filesize - CreatedDate
		filesize, created = getFileStats(framesFolder, frame)
		if not filesize == '':
			newEntry = [computer, duration, filesize, created]
			framesData[frame] = newEntry
	if hasChanged:
		print('new data saving:')
		writeJsonToFile(dataDict, dataPath)
	else:
		print('no new data')

def getFileStats(rootPath, index):
	file = os.path.join(rootPath, 'frame_' + str(index).zfill(4) + '.png')
	if not os.path.exists(file):
		return '', ''
	fileStat = os.stat(file)
	filesize = str(round(fileStat.st_size/1000000, 2)) + ' MB'
	created = datetime.fromtimestamp(fileStat.st_mtime).strftime('%I:%M %p %m-%d-%Y')
	return filesize, created


## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Initialization & Startup Functions  ------------------------------------------------ ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def initialize():
	#first make sure its windows
	if not platform.system() == 'Windows':
		print('Render Node is only made for windows PCs with NVidia GPUs!')
		sys.exit()

	localFile = 'C:\\Code\\Scripts\\renderNodeStats.py'
	remoteFile = 'R:\\Scripts\\renderNodeStats.py'
	localModified = os.path.getmtime(localFile)
	remoteModified = os.path.getmtime(remoteFile)
	if not remoteModified == localModified:
		subprocess.run(["rsync", "-a", "--progress", linuxPath(remoteFile), linuxPath(localFile)], shell=True)
		print('There was a change in the render script file, it has been updated. \nPlease run the Render Node again!\n----------------------------Exiting-----------------------------------')
		sys.exit()

	print('initialization Checks Completed\n\n Progress Monitoring in Progress')

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## --------------------------------------------------------------- Start of Script!  ----------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

#pip install watchdog - needed!


initialize()

if __name__ == '__main__':
	watch = OnMyWatch()
	watch.run()

