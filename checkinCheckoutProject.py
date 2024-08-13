
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
from datetime import datetime
import shutil


#Global Variables
debug = False

#Global Paths
workingDir = os.getcwd()
pathProjects = os.path.expanduser('~/Projects')
pathUserData = os.path.expanduser('~/Code/userData.json')
pathAlexandria = '/Volumes/Public/Dropbox'
pathThumbnails = '/Volumes/Public/Dropbox/Thumbnails'

#Global Functions
def initialize(userDict):
	os.system('clear')
	username = ''
	if not os.path.exists(pathUserData):
		print('\n\n\nfirst Time User ... Lets get setup\n\n\n')
		name = input('What is your name? ')
		username = name
		userDict['name'] = name
		userDict['checkouts'] = []
		writeJsonToFile(userDict, pathUserData)
		return userDict
	else:
		userDict = readJsonFile(pathUserData)
		return userDict

def readJsonFile(path):
	jsonData=open(path)
	data = json.load(jsonData)
	jsonData.close()
	return data

def writeJsonToFile(dataDict, filePath):
	with open(filePath, 'w', encoding='utf-8') as f:
		json.dump(dataDict, f, ensure_ascii=False, indent=4)

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
	
def chooseAction(userDict):
	name = userDict['name']
	checkouts = userDict['checkouts']
	print('\n\n Welcome Back ' + name + '\n\nHere are the projects you currently have checked out //////////////////////////////:\n\n')
	ind = 0
	for checkout in checkouts:
		print('-------------------------------------------------\n' + str(ind) + '. ' + checkout["projectType"] + ' | ' + checkout["projectName"] + '\n   ' + checkout["timestamp"])
		ind = ind + 1
	print('//////////////////////////////////////////////////////////////////')
	print('\n\n - What would you Like to do? Select a Number only\n')
	action = input('1. CHECK IN Existing Project I have Checked out\n2. CHECK OUT Existing Project\n3. Start a NEW Project\n\n')
	if action == '1':
		takeActionCheckin(userDict)
	elif action == '2':
		takeActionCheckout(userDict)
	elif action == '3':
		takeActionStartNewProject(userDict)	
	
def checkoutDictForKey(key, userDict):
	checkouts = userDict['checkouts']
	for checkout in checkouts:
		if checkout['key'] == key:
			return checkout
	checkout = {"key": '', "projectType": '', "projectName": '', "timestamp": ''}
	checkouts.append(checkout)
	return checkout

def takeActionCheckin(userDict):
	name = userDict['name']
	checkouts = userDict['checkouts']
	print('\n Here are the projects you currently have checked out //////////////////////////////\n')
	ind = 0
	for checkout in checkouts:
		print('-------------------------------------------------\n' + str(ind) + '. ' + checkout["projectType"] + ' | ' + checkout["projectName"] + '\n   ' + checkout["timestamp"] + '\n\n\n')
		ind = ind + 1
	
	selection = input('Which would you like to check in? (number): ')
	selection = int(selection)
	if selection >= len(checkouts):
		print("That number is invalid. Try again!")
		sys.exit()
	checkout = checkouts[selection]
	projectType = checkout["projectType"]
	project = checkout["projectName"]
	
	pathProjectAlexandria = os.path.join(pathAlexandria, projectType, project)
	pathProjectLocal = os.path.join(pathProjects, projectType, project)
	
	# lets find a list of all final cut projects to check in
	allFiles = os.listdir(pathProjectLocal)
	fcpxbundles = [f for f in allFiles if f.endswith('.fcpbundle')]
	
	for fcpxbundle in fcpxbundles:
		rsyncString = "rsync -av --delete --progress '" + pathProjectLocal + '/' + fcpxbundle + "' '" + pathProjectAlexandria + "'"
		os.system(rsyncString)
	
	
	os.system('clear')
	print('\nSuccessfully Checked Back IN \n\n1. Just Saving but keep it checked out (Im still working)\n2. I want to remove the lock I am done, but keep my local copy (just in case)\n')
	
	isFinished = input('What would you Like to do (pick a number): ')
	if isFinished == '1':
		print('Project Updated to Alexandria, but still checked out!')
	elif isFinished == '2':
		checkedOutFilePath = os.path.join(pathProjectAlexandria, 'CHECKED OUT.json')
		os.remove(checkedOutFilePath)
		checkedOutFilePath = os.path.join(pathProjectLocal, 'CHECKED OUT.json')
		os.remove(checkedOutFilePath)
		del checkouts[selection]
		writeJsonToFile(userDict, pathUserData)
		print('Project Updated to Alexandria & Checked in, others can now edit!')
	
def takeActionCheckout(userDict):
	print("///////////   Checkout Project   //////////////////////////////////////////////")
	projectType = selectFolder(pathAlexandria)
	nextPath = os.path.join(pathAlexandria, projectType)
	project = selectFolder(nextPath)
	
	print('\n\nYou have selected:\n' + projectType + ' / ' + project + '\n')
	confirm = input('Is this correct? (y/n): ')
	
	if not confirm == 'y':
		sys.exit()
	
	
	performProjectCheckout(projectType, project)
	

def performProjectCheckout(projectType, project):
	
	pathProjectAlexandria = os.path.join(pathAlexandria, projectType, project)
	pathProjectLocal = os.path.join(pathProjects, projectType, project)
	key = projectType + '/' + project
	
	allFiles = os.listdir(pathProjectAlexandria)
	fcpxbundles = [f for f in allFiles if f.endswith('.fcpbundle')]

	
	# let's check if is checked out
	checkedOutFilePath = os.path.join(pathProjectAlexandria, 'CHECKED OUT.json')
	if os.path.exists(checkedOutFilePath):
		currentCheckoutDict = readJsonFile(checkedOutFilePath)
		os.system('clear')
		print("\nTHIS PROJECT IS Already Checked out by " + currentCheckoutDict["user"] + '. \n This file was checked out at ' + currentCheckoutDict["timestamp"])
		print("\nPlease ask " + currentCheckoutDict["user"] + ' to check this project IN before checking it out yourself')
		sys.exit()
	
	
	if not os.path.exists(pathProjectLocal):
		os.makedirs(pathProjectLocal)
	
	
	for fcpxbundle in fcpxbundles:

		fileToCheck = os.path.join(pathProjectAlexandria, fcpxbundle)
		localFileToCheck = os.path.join(pathProjectLocal, fcpxbundle)

		copyExists = os.path.exists(localFileToCheck)
		if os.path.exists(localFileToCheck) == False:
			try:
				# Copy the entire folder
				print("This Project doesn't exist so Copying now... Please Wait...")
				shutil.copytree(fileToCheck, localFileToCheck)

			except Exception as e:
				print(f"An error occurred: {e}")


		rsyncString = "rsync -av --delete --progress '" + pathProjectAlexandria + '/' + fcpxbundle + "' '" + pathProjectLocal + "'"
		os.system(rsyncString)


	timestamp = dateToString(datetime.now())
	checkoutDict = checkoutDictForKey(key, userDict)
	checkoutDict["key"] = key
	checkoutDict["projectType"] = projectType
	checkoutDict["projectName"] = project
	checkoutDict["timestamp"] = timestamp
	checkoutDict["user"] = userDict["name"]
	
	#create checkout file both on alexandria and local
	checkoutFilePath = os.path.join(pathProjectAlexandria, 'CHECKED OUT.json')
	checkoutFilePathLocal = os.path.join(pathProjectLocal, 'CHECKED OUT.json')
	writeJsonToFile(checkoutDict, checkoutFilePath)
	writeJsonToFile(checkoutDict, checkoutFilePathLocal)
	writeJsonToFile(userDict, pathUserData)

	print('Successfully Checked OUT - No one else can edit this now')

def takeActionStartNewProject(userDict):
	projectType = selectFolder(pathAlexandria)
	projectPath = os.path.join(pathAlexandria, projectType)
	folders = os.listdir(projectPath)
	folders.sort()
	checker = re.compile('[a-zA-Z]{1,2}[0-9]{1,6}')
	letterChecker = re.compile('[a-zA-z]{1,2}')
	numberChecker = re.compile('[0-9]{1,6}')
	dataDict = {}
	for folder in folders:
		
		result = checker.match(folder)
		if result:
			ans = result.group(0)
			letter = letterChecker.match(ans)
			letter = letter.group(0)
			number = ans.replace(letter,"")
			number = int(number)
			currentMax = number
			if letter in dataDict.keys():
				currentMax = max(currentMax, dataDict[letter])
			dataDict[letter] = currentMax
	projectName = input('What do you want to name this project?\n\n').title()
	print('\nWhich Prefix Do you Want to use?\n')
	for key in dataDict.keys():
		print(key + "{:03d}".format(dataDict[key] + 1) + ' - ' + projectName)
	print('\nPlease Select the First LETTER of the prefix you want to use. example: M')
	prefix = input('Prefix: ').upper()
	if not prefix in dataDict.keys():
		sys.exit()
	baseProjectName = projectName
	projectName = prefix + "{:03d}".format(dataDict[prefix] + 1) + ' - ' + projectName
	pathNewProject = os.path.join(projectPath, projectName)
	os.mkdir(pathNewProject)
	
	templatePath = os.path.join(projectPath, 'TEMPLATE')
	rsyncString = "rsync -av --progress '" + templatePath + "/' '" + pathNewProject + "'"
	os.system(rsyncString)
	
	#also make folder in thumbnails
	newThumbDir = os.path.join(pathThumbnails, projectType)
	if os.path.exists(newThumbDir):
		newThumbDir = os.path.join(newThumbDir, projectName)
		os.mkdir(newThumbDir)
	
	fcpxOldPath = os.path.join(pathNewProject, 'Template.fcpbundle')
	fcpxNewPath = os.path.join(pathNewProject, baseProjectName + '.fcpbundle')
	os.rename(fcpxOldPath, fcpxNewPath)
	
	os.system('clear')
	print('\nSuccessfully Created Project\n')
	shouldCheckout = input('Do you Want to CHECK OUT ' + projectName + ' Now? (y/n)\n\n').lower()
	if not shouldCheckout == 'y':
		sys.exit()
	
	performProjectCheckout(projectType, projectName)


#Start of Script
userDict = {}
userDict = initialize(userDict)
chooseAction(userDict)












