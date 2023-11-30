
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
import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#Global Variables
lastTime = time.time()
lastFile = ''
pathRendersRoot = ['/Volumes/Scratch/Renders/Active Renders', 'R:\\Active Renders']
pathActiveProjects = ['/Volumes/Scratch/Renders/Data/activeProjects.json', 'R:\\Data\\activeProjects.json']
pathDataRoot = ['/Volumes/Scratch/Renders/Data/Projects', 'R:\\Data\\Projects']

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
	time.sleep(2)
	t = time.time()
	strTime = time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime(t))
	print('T: ' + strTime + ' File: ' + filePath)
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
	newestCreatedFrame = 0
	for frame, duration in newArray.items():

		if frame in framesData:
			#already exists
			d = framesData[frame]
			if computer == d[0] and duration == d[1]:
				continue

		#new frame!
		hasChanged = True
		#Format - Frame - RenderNodeName - RenderTime - Filesize - CreatedDate
		filesize, created, rawTime = getFileStats(framesFolder, frame)
		newestCreatedFrame = max(newestCreatedFrame, rawTime)
		if not filesize == '':
			newEntry = [computer, duration, filesize, created]
			framesData[frame] = newEntry
	
	
	#Lets do the node based analytics
	if hasChanged:
		if not 'nodes' in dataDict.keys():
			dataDict['nodes'] = {}

		nodes = dataDict['nodes']
		if not computer in nodes.keys():
			nodes[computer] = {}

		nodeData = nodes[computer]
		totalFrames = 0
		totalDuration = 0.0
		lastFrame = 0
		for frame, duration in newArray.items():
			totalDuration += duration
			totalFrames += 1
			lastFrame = max(lastFrame, int(frame))
		averageTime = totalDuration / float(totalFrames)
		nodeData['averageFrame'] = round(averageTime, 1)
		nodeData['totalFrames'] = totalFrames
		nodeData['lastFrameDate'] = newestCreatedFrame
		nodeData['framesPerMinute'] = round(60 / averageTime, 2)
		nodeData['lastCompletedFrame'] = lastFrame
		nodeData['totalDuration'] = round(totalDuration, 0)

	#Next Let's do full project analytics
	if hasChanged:
		if not 'analytics' in dataDict.keys():
			dataDict['analytics'] = {}

		analytics = dataDict['analytics']

		totalDuration = 0
		totalFrames = 0
		fpm = 0
		maxFrame = 0
		for computer, values in nodes.items():
			totalDuration += values['totalDuration']
			totalFrames += values['totalFrames']
			fpm += values['framesPerMinute']
			maxFrame = max(maxFrame, values['lastCompletedFrame'])

		#now we need to read in the active renders data
		activeRenders = readJsonFile(systemPath(pathActiveProjects), [])
		totalProjectFrameCount = 0
		for render in activeRenders:
			if render['blendName'] == projectName + '.blend':
				activeRender = render
				totalProjectFrameCount = int(activeRender['endFrame']) - int(activeRender['startFrame']) + 1
		
		percentComplete = round(totalFrames / totalProjectFrameCount, 2)
		missingFrames = totalProjectFrameCount - totalFrames

		#time remaining calcs
		timeRemaining = (float(missingFrames) / fpm) * 60 #in secs
		t = time.time()
		eta = time.strftime("%I:%M:%S %p %m-%d-%Y", time.localtime(t + timeRemaining))
		analytics['timeLeft'] = convertSecsToDaysMinutesSeconds(timeRemaining) + ' Remaining'
		analytics['ETA'] = 'ETA: ' + eta
		analytics['totalRenderTime'] = convertSecsToDaysMinutesSeconds(totalDuration) + ' of TOTAL Render Time'
		analytics['framesPerMinute'] = str(round(fpm, 1)) + ' Frames/Minute'
		analytics['percentCompleteStr'] = str(round(percentComplete * 100, 0)) + '% Complete'
		analytics['percentComplete'] = percentComplete


	if hasChanged:
		print('new data saving:')
		writeJsonToFile(dataDict, dataPath)
	else:
		print('no new data')

def convertSecsToDaysMinutesSeconds(seconds):
	days = math.floor(seconds / 86400.0)
	seconds = seconds - days * 86400.0
	hours = math.floor(seconds / 3600.0)
	seconds = seconds - hours * 3600.0
	minutes = math.floor(seconds / 60.0)
	timeLeft = ''
	if minutes > 0:
		timeLeft = str(minutes) + ' Mins'
	if hours > 0:
		timeLeft = str(hours) + ' Hours, ' + timeLeft
	if days > 0:
		timeLeft = str(days) + ' Days, ' + timeLeft
	return timeLeft

def getFileStats(rootPath, index):
	file = os.path.join(rootPath, 'frame_' + str(index).zfill(4) + '.png')
	if not os.path.exists(file):
		return '', ''
	fileStat = os.stat(file)
	filesize = str(round(fileStat.st_size/1000000, 2)) + ' MB'
	rawTime = fileStat.st_mtime
	created = datetime.fromtimestamp(fileStat.st_mtime).strftime('%I:%M %p %m-%d-%Y')
	return filesize, created, rawTime


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

