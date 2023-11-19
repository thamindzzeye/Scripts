
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


#Global Variables
debug = False
renderNodeActive = False

def getComputerName():
	name = platform.node()
	parts = name.split('.')
	return parts[0]

#Global Paths
pathProjects = ['/Volumes/Public/Blender/Projects', 'A:\\Blender\\Projects']
pathActiveProjects = ['/Volumes/Scratch/Renders/Active Projects', 'R:\\Active Projects']
pathActiveRenders = ['/Volumes/Scratch/Renders/Active Renders', 'R:\\Active Renders']
pathActiveProjectsData = ['/Volumes/Scratch/Renders/Data/activeProjects.json', 'R:\\Data\\activeProjects.json']
computerName = getComputerName()
pathActiveNodeData = ['/Volumes/Scratch/Renders/Data/Nodes/' + computerName + '.json', 'R:\\Data\\Nodes\\' + computerName]
pathLocalRenderRoot = ['', 'C:\\Renders']
pathLocalRenderProjects = ['', 'C:\\Renders\\Projects']
activeFrame = -1

blenderProcess = subprocess.run('', capture_output=True, shell=True)

def systemPath(pathArray):
	index = int(platform.system() == 'Windows')
	path = pathArray[index]
	return path

def linuxPath(path):
	path = path.replace('\\','/')
	parts = path.split(':')
	path = '/cygdrive/' + parts[0] + parts[1]
	return path

def dateToString(date):
	return date.strftime('%m-%d-%Y %H:%M:%S')

def stringToDate(string):
	return datetime.strptime(string, '%m-%d-%Y %H:%M:%S')

def readJsonFile(path):
	jsonData=open(path)
	data = json.load(jsonData)
	jsonData.close()
	return data

def writeJsonToFile(dataDict, filePath):
	with open(filePath, 'w', encoding='utf-8') as f:
		json.dump(dataDict, f, ensure_ascii=False, indent=4)

## ----------------------------------------Render Node Functions! ---------------------------------------- ## 

projectName = 'x'
projectDict = {}

def initializeData(project):
	fullPath = os.path.join(pathActiveNodeData, project + '.json')
	print(fullPath)

def findMetaDataFromMatches(matches):
	data=[]
	projectName = ''
	for match in matches:
		bits = match.split('\n')
		first = bits[0]
		first = first.replace("Saved: '",'').replace(".png'", '')
		firstBits = first.split('\\')
		if projectName == '':
			projectName = firstBits[-2]
		frame = firstBits[-1]
		frame = int(frame.replace('frame_', ''))
		second = bits[1]
		t = second.replace('Time: ','').replace(' (Saving', '')
		tSplit = t.split(':')
		mins = float(tSplit[0])
		secs = float(tSplit[1])
		time = mins*60 + secs
		data.append([frame, time])
	return projectName, data


def ping(args):
	t = time.time()
	strTime = time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime(t))
	print('ping: ' + strTime)

	localRoot = systemPath(pathLocalRenderRoot)
	localData = os.path.join(localRoot, 'Data')
	logPath = os.path.join(localData, 'logs.txt')
	errorsPath = os.path.join(localData, 'errors.txt')

	lines = ''
	with open(logPath) as f:
		lines = f.read()

	pattern = 'Saved:[\\S\\s]*?\\(Saving'
	matches = re.findall(pattern, lines)
	projectName, newData = findMetaDataFromMatches(matches)

	dataPath = systemPath(pathActiveNodeData)
	dataPath = os.path.join(dataPath, projectName + '.json')
	fullData = []
	print(dataPath)
	if os.path.exists(dataPath):
		fullData = readJsonFile(dataPath)
	
	resultingData = fullData + [i for i in newData if i not in fullData]
	writeJsonToFile(resultingData, dataPath)

#Start of Script

#First let's create any needed folders
if not platform.system() == 'Windows':
	print('Render Node is only made for windows PCs with NVidia GPUs!')
	sys.exit()

#create the local folders

dataFolder = systemPath(pathActiveNodeData)
print(dataFolder)
if not os.path.exists(dataFolder):
	os.mkdir(systemPath(pathActiveNodeData))

while True:
	ping('')
	time.sleep(60.0)    







