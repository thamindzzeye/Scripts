
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
pathProjects = os.path.expanduser('~/Projects')
pathUserData = os.path.expanduser('~/Code/userData.json')
pathAlexandria = '/Volumes/Public/Dropbox'
pathLastUpdatedData = '/Volumes/Public/Dropbox/Thumbnails/Data/lastUpdatedData.json'
pathProjectsRoot = '/Volumes/Public/Dropbox/Thumbnails/'
pathMontage = '/Volumes/Public/Dropbox/Thumbnails/Previews'
folderSkipArray = ['previews', 'data', 'helpers', 'template', '.ds_store']

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

def takeActionCreateMontages():
	lastModifiedDict = readFileToDict(pathLastUpdatedData)
	channels = os.listdir(pathProjectsRoot)
	for channel in channels:
		if channel.lower() in folderSkipArray:
			continue
		if not os.path.isdir(os.path.join(pathProjectsRoot, channel)):
			continue
		print('\n\nStarting On Channel: ' + channel)
		updateLastModifiedDatesInFolder(os.path.join(pathProjectsRoot, channel), lastModifiedDict, channel)
	
	writeDictToFile(lastModifiedDict, pathLastUpdatedData)
	print("completed thumbnail montages\n\n\n")
		

def selectFolder(path):
	folders = files = os.listdir(path)
	folders.sort()
	if len(folders) == 0:
		print('''ERROR: Make Sure your connected to Alexandria First!
		connect to server -> smb://alexandria.two.bit''')
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
	action = input('1. Create new Thumbnail Request\n2. Sync New Requests\n3. Create Thumbnail Montages\n4. Move Thumbnails To New Location\n\n')
	if action == '1':
		takeActionNewThumbnailRequest()
	elif action == '2':
		print('ok')
	elif action == '3':
		takeActionCreateMontages()
	elif action == '4':
		moveThumbnailsToNewLocation()


def checkoutDictForKey(key, userDict):
	checkouts = userDict['checkouts']
	for checkout in checkouts:
		if checkout['key'] == key:
			return checkout
	checkout = {"key": '', "projectType": '', "projectName": '', "timestamp": ''}
	checkouts.append(checkout)
	return checkout

def takeActionNewThumbnailRequest():
	print("new thumbnail request")
def takeActionSyncThumbnailRequests():
	print("sync thumbnail reqs")
	
def takeActionThumbnailMontage(userDict):
	pathVideos = '/Volumes/Public/Dropbox/Two Bit da Vinci Projects'
	projectPath = selectFolder(pathVideos)
	nextPath = os.path.join(pathAlexandria, projectPath)
	nextPath = os.path.join(nextPath, 'Thumbnails')
	print(nextPath)

def moveThumbnailsToNewLocation():
	oldLocationBase = '/Volumes/Public/Dropbox/'
	newLocationBase = '/Volumes/Public/Dropbox/Thumbnails/'
	typeFolder = selectFolder(oldLocationBase)
	oldTypeFolderBase = os.path.join(oldLocationBase, typeFolder)
	newTypeFolderBase = os.path.join(newLocationBase, typeFolder)
	if not os.path.exists(newTypeFolderBase):
		os.makedirs(newTypeFolderBase)
	allFolders = os.listdir(oldTypeFolderBase)
	for folder in allFolders:
		fullPath = os.path.join(oldTypeFolderBase, folder)
		thumbnailPath = os.path.join(fullPath, 'Thumbnails')
		
		if os.path.exists(thumbnailPath):
			newPathBase = os.path.join(newTypeFolderBase, folder)
			moveAllFilesFromTo(thumbnailPath, newPathBase)
			os.rmdir(thumbnailPath)
					
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












