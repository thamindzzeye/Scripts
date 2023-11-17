
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
from datetime import datetime
import shutil
import time


#Global Variables
debug = False

#Global Paths
workingDir = os.getcwd()
pathProjects = ['/Volumes/Public/Blender/Projects', Path('A:/Blender/Projects')]
pathActiveProjects = ['/Volumes/Scratch/Renders/Active Projects', Path('R:/Active Projects')]
# pathProjects = os.path.expanduser('~/Projects')
# pathUserData = os.path.expanduser('~/Code/userData.json')
# pathAlexandria = '/Volumes/Public/Dropbox'
# pathLastUpdatedData = '/Volumes/Public/Dropbox/Thumbnails/Data/lastUpdatedData.json'
# pathProjectsRoot = '/Volumes/Public/Dropbox/Thumbnails/'
# pathMontage = '/Volumes/Public/Dropbox/Thumbnails/Previews'
# folderSkipArray = ['previews', 'data', 'helpers', 'template', '.ds_store']

def systemPath(pathArray):
	index = int(platform.system() == 'Windows')
	return pathArray[index]

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
		
		
def createMontageForDirectory(path, name):
	inputStr = '"' + path + '/*.jpg"'
	outputStr = os.path.join(pathMontage, name + '.jpg')
	outputStr = '"' + outputStr + '"'
	cmd = "montage -label '%t' -pointsize 45 -fill white -stroke white -strokewidth 2 " + inputStr + " -background '#000000' -geometry 640x360+5+5 -tile 3x  " + outputStr
	os.system(cmd)


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
	
def chooseAction():

	print('\n\n - What would you Like to do? Select a Number only\n')
	action = input('''
	1. Create new Active Render (Run on Mac)
	2. Join as a Render Node (Run on Windows)
	3. Monitor Progress (Only for Delphi!)
	4. Clean blend1 files\n\n''')
	
	if action == '1':
		takeActionNewActiveRender()
	elif action == '2':
		print('ok 2')
	elif action == '3':
		print('ok 3')
	elif action == '4':
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

def checkoutDictForKey(key, userDict):
	checkouts = userDict['checkouts']
	for checkout in checkouts:
		if checkout['key'] == key:
			return checkout
	checkout = {"key": '', "projectType": '', "projectName": '', "timestamp": ''}
	checkouts.append(checkout)
	return checkout

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
	print("lets go")
	fullBlendPath = os.path.join(projectPath, blendFile)
	print(fullBlendPath)
	destinationPath = os.path.join(systemPath(pathActiveProjects), blendFile)
	print(destinationPath)
	if os.path.exists(destinationPath):
		print('Error, you already have a file with the same name in active projects!\n\nAborting')
		sys.exit()
	shutil.copy(fullBlendPath, destinationPath)
					
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
	
def findThumbnailsAtPath(path):
	allFiles = os.listdir(path)
	for file in allFiles:
		if file.lower().endswith('.jpg'):
			print('thumbnail! ' + file)

#Start of Script

chooseAction()












