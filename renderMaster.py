
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
	
class Status(Enum):
    PAUSED = 1
    ACTIVE = 2
    COMPLETE = 3
    VIDEO_COMPLETE = 4
    READY_TO_DELETE = 5

#Global Paths
pathProjects = ['/Volumes/Public/Blender/Projects', 'A:\\Blender\\Projects']
pathActiveProjects = ['/Volumes/Scratch/Renders/Active Projects', 'R:\\Active Projects']
pathActiveRenders = ['/Volumes/Scratch/Renders/Active Renders', 'R:\\Active Renders']
pathActiveProjectsData = ['/Volumes/Scratch/Renders/Data/activeProjects.json', Path('R:\\Data\\activeProjects.json')]
computerName = getComputerName()
pathActiveNodeData = ['/Volumes/Scratch/Renders/Data/' + computerName + ' .json', Path('R:\\Data\\' + computerName + ' .json')]
pathProjectAnalytics = ['/Volumes/Scratch/Renders/Data/Projects', Path('R:\\Data\\Projects')]

def systemPath(pathArray):
	index = int(platform.system() == 'Windows')
	return pathArray[index]

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

def readJsonFile(path):
	jsonData=open(path)
	data = json.load(jsonData)
	jsonData.close()
	return data

def writeJsonToFile(dataDict, filePath):
	with open(filePath, 'w', encoding='utf-8') as f:
		json.dump(dataDict, f, ensure_ascii=False, indent=4)
	
def chooseAction():
	os.system('clear')
	print('Hello, I am ' + computerName + '!\n\n')
	print('\n\n - What would you Like to do? Select a Number only\n')
	action = input('''
	1. Create new Active Render
	2. Monitor Progress (Only for Delphi!)
	3. Clean blend1 files\n\n''')
	
	if action == '1':
		takeActionNewActiveRender()
	elif action == '2':
		takeActionMonitorProgress()
	elif action == '3':
		takeActionCleanBlend1Files()

def takeActionCleanBlend1Files():
	filesToDelete, fileSizes = findFiles(systemPath(pathProjects), '.blend1')
	if len(filesToDelete) == 0:
		print("No Blend1 Files So you are good to go! GoodBye!")
		sys.exit()
	
	
	totalSize = 0.0
	for i, (file, size) in enumerate(zip(filesToDelete, fileSizes)):
		print('file: ' + file + ' size: ' + str(size))
		totalSize = totalSize + size
	print('\n\n I found the ^^ These blend1 files that should be deleted.\n\n')
	print('Total Size: ' + str(int(totalSize)) + ' MB\n\n')
	
	action = input('Delete Files? (Y)es / (N)o: ')
	if action.lower() == 'y':
		print("delete in progress")
		for file in filesToDelete:
			os.remove(file)
		
	else:
		print("Cancelled")
	
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

def takeActionNewActiveRender():
	print("Let's Pick which render you want to start")
	
	projectName = selectFolder(systemPath(pathProjects))
	projectPath = os.path.join(systemPath(pathProjects), projectName)

	blendFile = selectFile(projectPath, '.blend')
	print('You Selected: ' + blendFile + '\n\n')
	action = input('Is this Correct? (Y)es \ (N)o: ')
	if not action.lower() == 'y':
		print('\n\nOk Cancelling this operation, Goodbye!\n\n\n')
		sys.exit()
	os.system('clear')
	fullBlendPath = os.path.join(projectPath, blendFile)
	destinationPath = os.path.join(systemPath(pathActiveProjects), blendFile)
	
	#lets create the meta data
	startFrame = input('Start Frame (usually 0 or 1): ')
	endFrame = input('End Frame: ')
	print('file output PNG')
	print('video FPS 30 frame / sec\n\n')
	blenderVersion = input('What is the blender version that should be used for rendering?\nExample 4.0 - This must match the exact version of blender found at C:\Program Files\Blender Foundation\nVersion: ')
	
	renderDict = {'blenderVersion': blenderVersion, 'projectName': projectName, 'blendName': blendFile, 'path': fullBlendPath, 'status': Status.ACTIVE.name, 'startFrame': startFrame, 'endFrame': endFrame}
	
	currentProjects = []
	if os.path.exists(systemPath(pathActiveProjectsData)):
		currentProjects = readJsonFile(systemPath(pathActiveProjectsData))
	
	projectExists = False
	for project in currentProjects:
		if project['path'].lower() == fullBlendPath.lower():
			projectExists = True
			project['status'] = Status.ACTIVE.name
			print('This project is already in active projects...')
			sys.exit()
	
	if len(currentProjects) == 0:
		print('\n\n You Have No Active Projects, Adding ' + blendFile + ' now!')
		currentProjects.append(renderDict)
	else:
		print('\n\n You have the following active projects:\n')
		listItemsInArray(currentProjects)
		index = int(input('Where should we add this project?\n0 = top of the queue: '))
		if index > len(currentProjects):
			index = len(currentProjects)
		currentProjects.insert(index, renderDict)
	
	renderFolderAddon = blendFile.split('.')[0]
	renderDestination = os.path.join(systemPath(pathActiveRenders), renderFolderAddon)
	print(renderDestination)
	if os.path.exists(renderDestination):
		existingFiles = os.listdir(renderDestination)
		if not len(existingFiles) == 0:
			print(existingFiles)
			print('There is already a folder in the render path with files in it.')
			print('\n\n\n Remove Them before starting?')
			ans = input('Delete Existing Files? (Y)es / (N)o: ')
			if ans.lower() == 'y':
				for file in existingFiles:
					os.remove(os.path.join(renderDestination, file))
		
	else:
		os.mkdir(renderDestination)
	
	#moving into active folder
	rsyncCommand = "rsync -av --progress '" + fullBlendPath + "' '" + destinationPath + "'"
	print('RYNC Command: ' + rsyncCommand)
	os.system(rsyncCommand)
	#writing the json file
	print('\n\nHere are the active projects:')
	listItemsInArray(currentProjects)
	writeJsonToFile(currentProjects, systemPath(pathActiveProjectsData))

def listItemsInArray(currentProjects):
	index = 0
	for project in currentProjects:
		print(str(index) + '. ' + project['blendName'])
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

## ----------------------------------------Render Monitoring Functions! ---------------------------------------- ## 

def updateMonitoringData():
	analyticsRootPath = systemPath(pathProjectAnalytics)
	activeProjects = readJsonFile(systemPath(pathActiveProjectsData))
	for project in activeProjects:
		createAnalyticsDataForProject(project)
	print('Analytics Complete')

def createAnalyticsDataForProject(projDict):
	print('Starting Analytics for: ' + projDict['blendName'])
	startFrame = int(projDict['startFrame'])
	endFrame = int(projDict['endFrame'])
	
	#first let's check if we have a render folder
	blendFile = projDict['blendName']
	blendFolder = blendFile.split('.')[0]
	framesFolder = systemPath(pathActiveRenders)
	framesFolder = os.path.join(framesFolder, blendFolder)
	dataDict = {}
	if os.path.exists(framesFolder):
		#Exists so let's see what frames are found
		createFileAttributesDictForFolder(framesFolder)
		
			
	else:
		#There's no folder so its not active all frames missing
		print('else')
	
#Format - Frame - RenderNodeName - RenderTime - Filesize - CreatedDate

def createFileAttributesDictForFolder(folder):
	data = {}
	with os.scandir(folder) as files:
		for file in files:
			info = file.stat()
# 			os.stat_result(st_mode=33216, st_ino=1443055845590940478, st_dev=905969667, st_nlink=1, st_uid=501, st_gid=20, st_size=7036437, st_atime=1700447668, st_mtime=1700447722, st_ctime=1700447722)
			created = datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %-I:%M %p')
			filesize = str(round(info.st_size/1000000, 2)) + ' MB'
			frame = int(file.name.replace('frame_','').replace('.png', ''))
			
			data[frame] = ['', '', filesize, created]
	
	print(data)
	sys.exit()
		

def takeActionMonitorProgress():
	
	print('Monitoring Renders - In Progress')
	while True:
		updateMonitoringData()
		time.sleep(60.0)  

#Start of Script

chooseAction()














