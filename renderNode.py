
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
from concurrent.futures import ThreadPoolExecutor as Pool

class Status(Enum):
    PAUSED = 1
    ACTIVE = 2
    VALIDATE = 3
    COMPLETE = 4
    VIDEO_COMPLETE = 5
    READY_TO_DELETE = 6
                

#Global Variables
debug = False
currentRenderDict = {}
renderNodeActive: bool = False

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
pathActiveNodeData = ['/Volumes/Scratch/Renders/Data/Nodes/' + computerName + '.json', 'R:\\Data\\Nodes\\' + computerName + '.json']
pathLocalRenderRoot = ['', 'C:\\Renders']
pathLocalRenderProjects = ['', 'C:\\Renders\\Projects']

def systemPath(pathArray):
	index = int(platform.system() == 'Windows')
	path = pathArray[index]
	return path

def linuxPath(path):
	path = path.replace('\\','/')
	parts = path.split(':')
	path = '/cygdrive/' + parts[0] + parts[1]
	return path

def updateLastModifiedDatesInFolder(folderPath, dateDict, channel):
	projects = os.listdir(folderPath)
	for project in projects:
		if project.lower() in folderSkipArray:
			continue
		
		projectPath = os.path.join(folderPath, project)
		projectKey = channel + '/' + project
		files = os.listdir(projectPath)
		for file in files:
			filepath = os.path.join(projectPath, file)
			if file.lower().endswith('.jpg'):
				fileModified = os.path.getmtime(filepath)
				
				lastModified = 0.0
				if projectKey in dateDict.keys():
					lastModified = dateDict[projectKey]
				if fileModified > lastModified:
					print('New File Detected: ' + project + ' / ' + file)
					dateDict[projectKey] = fileModified
					createMontageForDirectory(projectPath, project)

def selectFile(path, ext):
	files = []
	    # loop through all the entries in the path directory
	for file in os.scandir(path):
	    # if the entry is a folder, append its name to the list
	    if file.name.endswith(ext):
	        files.append(file.name)
	files.sort()
	if len(files) == 0:
		print('''ERROR: Make Sure your connected to Alexandria First!
		connect to server -> smb://alexandria.twobit.local''')
		sys.exit()
	
	ind = 0
	print('\n\n/////////////////////////// ' + path + ' ///////////////////////////\n\n')
	for file in files:
		print(str(ind) + '. ' + file)
		ind = ind + 1
		
	
	selection = -1
	while selection < 0 or selection >= len(files):
		selection = input('\n\n=> Which Folder?\nPlease enter just the number between 0 - ' + str(len(files)-1) + '\n\n')
		selection = int(selection)
		
	return files[selection]		

def selectFolder(path):
	folders = []
	    # loop through all the entries in the path directory
	for entry in os.scandir(path):
	    # if the entry is a folder, append its name to the list
	    if entry.is_dir():
	        folders.append(entry.name)
	folders.sort()
	if len(folders) == 0:
		print('''ERROR: Make Sure your connected to Alexandria First!
		connect to server -> smb://alexandria.twobit.local''')
		sys.exit()
	
	ind = 0
	print('\n\n/////////////////////////// ' + path + ' ///////////////////////////\n\n')
	for folder in folders:
		print(str(ind) + '. ' + folder)
		ind = ind + 1
		
	
	selection = -1
	while selection < 0 or selection >= len(folders):
		selection = input('\n\n=> Which Folder?\nPlease enter just the number between 0 - ' + str(len(folders)-1) + '\n\n')
		selection = int(selection)
		
	return folders[selection]

def dateToString(date):
	return date.strftime('%m-%d-%Y %H:%M:%S')

def stringToDate(string):
	return datetime.strptime(string, '%m-%d-%Y %H:%M:%S')

def readJsonFile(path, errorDefault):
	with open(path, "r") as jsonData:
		data = json.load(jsonData)
		return data
	return errorDefault

def writeJsonToFile(dataDict, filePath):
	with open(filePath, 'w', encoding='utf-8') as f:
		json.dump(dataDict, f, ensure_ascii=False, indent=4)

def findFiles(root, ext):
    # initialize two empty lists to store the paths and sizes
    paths = []
    sizes = []
    # loop through all the files and folders in the root directory
    for entry in os.scandir(root):
        # if the entry is a file and has the given extension, append its path and size to the lists
        if entry.is_file() and entry.name.endswith(ext):
            paths.append(entry.path)
            sizes.append(entry.stat().st_size / (1024 * 1024)) # convert bytes to megabytes
        # if the entry is a folder, recursively call the function on it and extend the lists with the results
        elif entry.is_dir():
            sub_paths, sub_sizes = findFiles(entry.path, ext)
            paths.extend(sub_paths)
            sizes.extend(sub_sizes)
    # return the lists of paths and sizes
    return paths, sizes

def listItemsInArray(currentProjects):
	index = 0
	for project in currentProjects:
		print(str(index) + '. ' + project['blendName'] + ' Status: [' + project['status'] + ']')
		index = index + 1
	print('\n')
					
def moveAllFilesFromTo(oldRoot, newRoot):
	print('old: ' + oldRoot)
	print('new: ' + newRoot)
	allFiles = os.listdir(oldRoot)
	
	if not os.path.exists(newRoot):
		os.makedirs(newRoot)
	for file in allFiles:
		old = os.path.join(oldRoot, file)
		new = os.path.join(newRoot, file)
		shutil.move(old, new)

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Render Node Functions! ------------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def getBlenderLogPaths():
	localRoot = systemPath(pathLocalRenderRoot)
	localData = os.path.join(localRoot, 'Data')
	logPath = os.path.join(localData, 'logs.txt')
	errorsPath = os.path.join(localData, 'errors.txt')
	return logPath, errorsPath

def startRendering(renderDict):
	print("rendering: " + renderDict['blendName'])
	
	logPath, errorsPath = getBlenderLogPaths()
	if os.path.exists(logPath):
		os.remove(logPath)
	if os.path.exists(errorsPath):
		os.remove(errorsPath)

	#first lets rsync the project to our local location
	sourceFile = os.path.join(systemPath(pathActiveProjects), renderDict['blendName'])
	destinationFile = os.path.join(systemPath(pathLocalRenderProjects), renderDict['blendName'])
	sourceFileX = linuxPath(sourceFile)
	destinationFileX = linuxPath(destinationFile)
	subprocess.run(["rsync", "-a", "--progress", sourceFileX, destinationFileX], shell=True)

	blenderProgramPath = 'C:\\Program Files\\Blender Foundation\\Blender '+ renderDict['blenderVersion'] +'\\blender.exe'
	if not os.path.exists(blenderProgramPath):
		print('\n\n#####-------------------------------Blender Version Not Installed!------------------------------------------####\n Please install before you can render this scene')
		print(blenderProgramPath)
		return
	else:
		print('Correct Blender Version Detected')
		print(blenderProgramPath)

	frames = ' -s ' + renderDict['startFrame'] + ' -e ' + renderDict['endFrame'] + ' '

	fileFolder = renderDict['blendName'].split('.')[0]
	framePath = os.path.join(systemPath(pathActiveRenders), fileFolder)
	framePath = os.path.join(framePath, 'frame_####')

	#let's create the render command
	with open(logPath,"wb") as out, open(errorsPath,"wb") as err:
		print('starting')
		myargs = [
		blenderProgramPath,
		"-b",
		destinationFile,
		"-o",
		framePath,
		"-E",
		"CYCLES",
		"-a",
		"--",
		"--cycles-device CUDA",
		"-F",
		"PNG"
		]
		updateRenderStatus(True)
		global pool
		f = pool.submit(subprocess.call, myargs,stdout=out,stderr=err, shell=True)
		f.add_done_callback(renderDidFinish)
		pool.shutdown(wait=False)

def updateRenderStatus(status):
	global renderNodeActive
	if not status  == renderNodeActive:
		renderNodeActive = status
		strVal = "Active"
		if not status:
			strVal = "NOT Active"
		print('=====================================================================================\nRender Status Changed: ' + strVal + '\n=====================================================================================')

def renderDidFinish(args):
	updateRenderStatus(False)
	global pool
	pool = Pool(max_workers=1)
	checkIfComplete()

def cleanupBadFrames():
	logPath, errorsPath = getBlenderLogPaths()
	if not os.path.exists(logPath):
		return

	lines = ''
	with open(logPath, 'r') as file:
		lines = file.readlines()[-30:]
		for lineData in reversed(lines):
			line = lineData.strip()
			regex = 'Fra:.{1,4}\\s'
			matches = re.findall(regex, line)
			if len(matches) > 0:
				match = matches[0]
				match = match.replace('Fra:','')
				frameNum = int(match)
				if 'blendName' in currentRenderDict.keys():
					blendName = currentRenderDict['blendName']
					folder = blendName.split('.')[0]
					fullPath = os.path.join(systemPath(pathActiveRenders), folder)
					fullPath = os.path.join(fullPath, 'frame_' + str(frameNum).zfill(4) + '.png')
					if os.path.exists(fullPath):
						frameSize = os.stat(fullPath).st_size
						previousSize = 0
						if frameNum > 2:
							prevFramePath = os.path.join(systemPath(pathActiveRenders), folder)
							prevFramePath = os.path.join(prevFramePath, 'frame_' + str(frameNum - 1).zfill(4) + '.png')
							if os.path.exists(prevFramePath):
								previousSize = os.stat(prevFramePath).st_size

						if frameSize < previousSize * .95 or frameSize == 0:
							os.remove(fullPath)
						return

def resumeRenderIfNeccessary():
	#lets check if we're rendering yet'
	shouldRender = False
	nodeData = {}
	if not renderNodeActive:
		activeRenders = readJsonFile(systemPath(pathActiveProjectsData), [])	
		if len(activeRenders) > 0:
			#we have an active render we should start!

			render = {}
			for activeRender in activeRenders:
				if activeRender['status'] == Status.ACTIVE.name:
					render = activeRender
					break

			if len(render.keys()) == 0:
				#no renders active so we break
				print('No Active Renders to Pick up')
				nodeData['activeProject'] = ''
			else:
				global currentRenderDict
				currentRenderDict = render
				shouldRender = True
				nodeData['activeProject'] = render['blendName']

			#next lets clean up bad frames
			cleanupBadFrames()
		else:
			nodeData['activeProject'] = ''
	nodeData['ping'] = time.time()
	writeJsonToFile(nodeData, systemPath(pathActiveNodeData))
	if shouldRender:
		startRendering(render)


def checkIfComplete():
	logPath, errorsPath = getBlenderLogPaths()
	if not os.path.exists(logPath):
		return

	lines = ''
	with open(logPath, 'r') as file:
		lines = file.readlines()[-20:]
		for lineData in reversed(lines):
			line = lineData.strip()
			regex = 'No frames rendered, skipped to not overwrite'
			matches = re.findall(regex, line)
			if len(matches) > 0:
				match = matches[0]
				print("Think its done!")
				activeRenders = readJsonFile(systemPath(pathActiveProjectsData), [])
				currentRender = readJsonFile(systemPath(pathActiveNodeData), {})
				for activeRender in activeRenders:
					print(activeRender)
					if activeRender['blendName'] == currentRender['activeProject']:
						#found it...
						activeRender['status'] = Status.VALIDATE.name
						writeJsonToFile(activeRenders, systemPath(pathActiveProjectsData))

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Initialization & Startup Functions  ------------------------------------------------ ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def initialize():
	#first make sure its windows
	if not platform.system() == 'Windows':
		print('Render Node is only made for windows PCs with NVidia GPUs!')
		sys.exit()

	#create the local folders
	localRoot = systemPath(pathLocalRenderRoot)
	localData = os.path.join(localRoot, 'Data')
	localProjects = os.path.join(localRoot, 'Projects')
	if not os.path.exists(localRoot):
		os.makedirs(localRoot)
	if not os.path.exists(localData):
		os.makedirs(localData)
	if not os.path.exists(localProjects):
		os.makedirs(localProjects)

	#delete existing blender log files
	localRoot = systemPath(pathLocalRenderRoot)
	localData = os.path.join(localRoot, 'Data')
	logPath = os.path.join(localData, 'logs.txt')
	errorsPath = os.path.join(localData, 'errors.txt')
	#shouldn't need this, but we'll see
	# if os.path.exists(logPath):
	# 	os.remove(logPath)
	# if os.path.exists(errorsPath):
	# 	os.remove(errorsPath)

	localFile = 'C:\\Code\\Scripts\\renderNode.py'
	remoteFile = 'R:\\Scripts\\renderNode.py'
	localModified = os.path.getmtime(localFile)
	remoteModified = os.path.getmtime(remoteFile)
	if not remoteModified == localModified:
		subprocess.run(["rsync", "-a", "--progress", linuxPath(remoteFile), linuxPath(localFile)], shell=True)
		print('There was a change in the render script file, it has been updated. \nPlease run the Render Node again!\n----------------------------Exiting-----------------------------------')
		sys.exit()

	#stats folders
	dataFolder = systemPath(['/Volumes/Scratch/Renders/Data/Nodes/' + computerName, 'R:\\Data\\Nodes\\' + computerName])
	print(dataFolder)
	if not os.path.exists(dataFolder):
		os.mkdir(dataFolder)
	print('initialization Checks Complete')


## --------------------------------------------------------------------------------------------------------------------------------------- ##
## --------------------------------------------------- Statistics Functions! ------------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def findMetaDataFromMatches(matches):
	data={}
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
		time = round(mins*60 + secs, 2)
		data[frame] = time
	return projectName, data

def parseBlenderOutputFiles():
	t = time.time()
	strTime = time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime(t))
	print('ping: ' + strTime)

	localRoot = systemPath(pathLocalRenderRoot)
	localData = os.path.join(localRoot, 'Data')
	logPath = os.path.join(localData, 'logs.txt')
	errorsPath = os.path.join(localData, 'errors.txt')

	lines = ''
	if not os.path.exists(logPath):
		return
	with open(logPath) as f:
		lines = f.read()

	pattern = 'Saved:[\\S\\s]*?\\(Saving'
	matches = re.findall(pattern, lines)
	projectName, newData = findMetaDataFromMatches(matches)

	dataPath = systemPath(['/Volumes/Scratch/Renders/Data/Nodes/' + computerName, 'R:\\Data\\Nodes\\' + computerName])
	dataPath = os.path.join(dataPath, projectName + '.json')
	fullData = {}
	if os.path.exists(dataPath):
		fullData = readJsonFile(dataPath, {})
	
	hasChanged = False
	if len(newData.keys()) == 0:
		return
	for key, value in newData.items():
		if key in fullData:
			if value == fullData[key]:
				#nothing new skip
				continue
		fullData[key] = value
		hasChanged = True

	if hasChanged:
		writeJsonToFile(fullData, dataPath)

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## ------------------------------------------------------ START OF SCRIPT! --------------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

initialize()

activeRenders = readJsonFile(systemPath(pathActiveProjectsData), [])
os.system('cls')
print(computerName + ' Reporting for Duty & Ready to Render!!\n\nActive Renders...\n')
listItemsInArray(activeRenders)

# print("begin waiting")
pool = Pool(max_workers=1)



while True:
	if not renderNodeActive:
		print('Re-starting Rendering Logic')
		resumeRenderIfNeccessary()
	time.sleep(30.0)
	parseBlenderOutputFiles()

print('test')