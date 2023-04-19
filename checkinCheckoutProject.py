
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
from datetime import datetime



#Global Variables
debug = False

#Global Paths
workingDir = os.getcwd()
pathProjects = os.path.expanduser('~/Projects')
pathUserData = os.path.expanduser('~/Code/userData.json')
pathAlexandria = '/Volumes/Public/Dropbox'

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
	action = input('1. CHECK IN Existing Project I have Checked out\n2. CHECK OUT New Project\n\n\n')
	if action == '1':
		takeActionCheckin(userDict)
	elif action == '2':
		takeActionCheckout(userDict)
	
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
	
	rsyncString = "rsync -av '" + pathProjectLocal + "/' '" + pathProjectAlexandria + "'"
	os.system(rsyncString)
	
	print('\nSuccessfully Checked Back IN \n\n1. Just Saving but keep it checked out (Im still working)\n2. I want to remove the lock I am done, but keep my local copy (just in case)\n')
	
	isFinished = input('What would you Like to do (pick a number): ')
	if isFinished == '1':
		print('Project Updated to Alexandria, but still checked out!')
	elif isFinished == '2':
		checkedOutFilePath = os.path.join(pathProjectAlexandria, 'CHECKED OUT.json')
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
	
	pathProjectAlexandria = os.path.join(nextPath, project)
	pathProjectLocal = os.path.join(pathProjects, projectType, project)
	
	key = projectType + '/' + project
	
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
	
	timestamp = dateToString(datetime.now())
	checkoutDict = checkoutDictForKey(key, userDict)
	checkoutDict["key"] = key
	checkoutDict["projectType"] = projectType
	checkoutDict["projectName"] = project
	checkoutDict["timestamp"] = timestamp
	checkoutDict["user"] = userDict["name"]
	
	
	rsyncString = "rsync -av '" + pathProjectAlexandria + "/' '" + pathProjectLocal + "'"
	os.system(rsyncString)
	checkoutFilePath = os.path.join(pathProjectAlexandria, 'CHECKED OUT.json')
	writeJsonToFile(checkoutDict, checkoutFilePath)
	writeJsonToFile(userDict, pathUserData)
	print('Successfully Checked OUT - No one else can edit this now')

#Start of Script
userDict = {}
userDict = initialize(userDict)
chooseAction(userDict)












