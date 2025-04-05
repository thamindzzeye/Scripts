
import os, subprocess, platform, sys, json
from enum import Enum
from os import listdir
from os.path import isfile, join
from pathlib import Path
from threading import Timer
import re
from datetime import datetime, timedelta
import shutil
import time
import math

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
	VALIDATE = 3
	COMPLETE = 4
	VIDEO_COMPLETE = 5
	READY_TO_DELETE = 6
	CANCELLED = 7

#Global Paths
pathProjects = ['/Volumes/Public/Blender/Projects', 'A:\\Blender\\Projects']
pathActiveProjects = ['/Volumes/Scratch/Renders/Active Projects', 'R:\\Active Projects']
pathActiveRenders = ['/Volumes/Scratch/Renders/Active Renders', 'R:\\Active Renders']
pathActiveProjectsData = ['/Volumes/Scratch/Renders/Data/activeProjects.json', Path('R:\\Data\\activeProjects.json')]
computerName = getComputerName()
pathActiveNodeData = ['/Volumes/Scratch/Renders/Data/' + computerName + ' .json', Path('R:\\Data\\' + computerName + ' .json')]
pathProjectAnalytics = ['/Volumes/Scratch/Renders/Data/Projects', Path('R:\\Data\\Projects')]
pathActiveNodeRoot = ['/Volumes/Scratch/Renders/Data/Nodes', Path('R:\\Data\\Nodes')]
pathVideoOutputs = ['/Volumes/Scratch/Renders/Outputs', 'R:\\Outputs']

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

def readJsonFile(path, errorDefault):
	with open(path, "r") as jsonData:
		data = json.load(jsonData)
		return data
	return errorDefault

def writeJsonToFile(dataDict, filePath):
	with open(filePath, 'w', encoding='utf-8') as f:
		json.dump(dataDict, f, ensure_ascii=False, indent=4)

def clearConsole():
	if platform.system() == 'Windows':
		os.system('cls')
	else:
		os.system('clear')

def linuxPath(path):
	if platform.system() == 'Windows':
		path = path.replace('\\','/')
		parts = path.split(':')
		path = '/cygdrive/' + parts[0] + parts[1]
		return path
	return path

def chooseAction():
	clearConsole()
	print('Hello, I am ' + computerName + '!\n\n')
	print('\n\n - What would you Like to do? Select a Number only\n')
	action = input('''
	1. Create new Active Render
	2. Monitor Progress (Only for Delphi!)
	3. Clean blend1 files
	4. Create Video Files For Finished Renders
	5. Clean Up OLD Projects
	6. CANCEL Active Render \nAction: ''')
	
	if action == '1':
		takeActionNewActiveRender()
	elif action == '2':
		takeActionMonitorProgress()
	elif action == '3':
		takeActionCleanBlend1Files()
	elif action == '4':
		createVideoFiles()
	elif action == '5':
		cleanupOldProjects()
	elif action == '6':
		cancelActiveRender()

def getActiveProjects():
	currentProjects = []
	if os.path.exists(systemPath(pathActiveProjectsData)):
		currentProjects = readJsonFile(systemPath(pathActiveProjectsData), [])
		return currentProjects
		

def filter_files_by_extension(files, extension):
	# Ensure extension starts with a dot and is lowercase
	if not extension.startswith('.'):
		extension = '.' + extension
	extension = extension.lower()
	
	# Filter files that end with the specified extension (case-insensitive)
	filtered_files = [file for file in files if file.lower().endswith(extension)]
	
	return filtered_files

def createVideoFiles():
	root = systemPath(pathActiveRenders)
	projectName = selectFolder(root)
	project = os.path.join(root, projectName)
	print(projectName)

	
	frames = filter_files_by_extension(os.listdir(project), '.png')

	frames.sort()
	if len(frames) == 0:
		print("NO Frames Found Skipping")
		return
	print(frames[0])
	firstFrame = int(frames[0].replace('frame_','').replace('.png',''))
	lastFrame = int(frames[-1].replace('frame_','').replace('.png',''))
	print('first = ' + str(firstFrame) + ' last = ' + str(lastFrame))
	quit = False
	latestFrame = firstFrame
	zeroFrames = []
	while quit == False:
		frame = 'frame_' + str(latestFrame).zfill(4) + '.png'
		fullPath = os.path.join(project, frame)
		if not os.path.exists(fullPath):
			break
		filesize = os.stat(fullPath).st_size
		if not filesize > 2000:
			zeroFrames.append(fullPath)
			break
		if latestFrame < lastFrame:
			latestFrame += 1
		else:
			break

	# isAlpha = input ('\n\nRender With Alpha? (y)es / (n)o: ')
	# if isAlpha:

	numFrames = str(latestFrame - firstFrame + 1)
	destinationVideo = '"' + os.path.join(systemPath(pathVideoOutputs), projectName + ' [' + str(firstFrame) + '-' + str(latestFrame - firstFrame + 1) + ']' + '.mp4') + '"'
	print(numFrames)
	myargs = [
	'ffmpeg',
	'-framerate', '30',
	'-i', '"' + os.path.join(project, 'frame_%04d.png') + '"',
	'-start_number', str(firstFrame),
	'-frames:v', numFrames,
	'-c:v', 'libx265',
	'-preset', 'slow',
	'-crf', '20',
	'-pix_fmt', 'yuv420p10le',
	'-tag:v', 'hvc1',
	'-f', 'mp4',
	destinationVideo]
	
	cmd = ''
	for arg in myargs:
		cmd = cmd + arg + ' '
 
	print(cmd)
 
	if platform.system() == 'Windows':
 
		cmd = cmd.replace('-c:v libx264', '')
 
	os.system(cmd)
 

 
	print('\n\nComplete!\n\n\n')


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
	print('\nBLENDER CHECKLIST\n\n1. Have you set the Output Settings -> RGB for all videos without alpha (standard)\nRGBA - ONLY when alpha pixels are present\n2. Color Depth -> 16 (16 bit color)\n3. Image Sequence -> YES for Placeholder, NO for Overwrite')
	
	imReady = input('OK Im ready (y)es: ')
	if not imReady.lower() == 'y':
		sys.exit()
	print("Let's Pick which render you want to start")
	projectName = selectFolder(systemPath(pathProjects))
	projectPath = os.path.join(systemPath(pathProjects), projectName)

	blendFile = selectFile(projectPath, '.blend')
	print('You Selected: ' + blendFile + '\n\n')
	action = input('Is this Correct? (Y)es / (N)o: ')
	if not action.lower() == 'y':
		print('\n\nOk Cancelling this operation, Goodbye!\n\n\n')
		sys.exit()
	clearConsole()
	fullBlendPath = linuxPath(os.path.join(projectPath, blendFile))
	destinationPath = linuxPath(os.path.join(systemPath(pathActiveProjects), blendFile))

	
	
	#lets create the meta data
	startFrame = input('Start Frame (usually 0 or 1): ')
	endFrame = input('End Frame: ')
	print('file output PNG')
	print('video FPS 30 frame / sec\n\nWhich Render Engine Should I Use?\n1. Cycles\n2. EVEE')
	engine = input('Render Engine (1 or 2): ')
	if engine == '1':
		# 1 is cycles
		engine = "CYCLES"
	elif engine == 2:
		# 2 is evee
		engine = "BLENDER_EEVEE"
	else:
		print("This is not a valid choice! Please enter either 1 or 2\nBreaking now. Please retry 'renderMaster' if you want to add this project" )
		sys.exit()

	blenderVersion = input('What is the blender version that should be used for rendering?\nExample 4.0 - This must match the exact version of blender found at C:\\Program Files\\Blender Foundation\nVersion: ')
	
	renderDict = {'blenderVersion': blenderVersion, 'projectName': projectName, 'blendName': blendFile, 'path': fullBlendPath, 'status': Status.ACTIVE.name, 'startFrame': startFrame, 'endFrame': endFrame, 'renderEngine': engine}
	
	currentProjects = []
	if os.path.exists(systemPath(pathActiveProjectsData)):
		currentProjects = readJsonFile(systemPath(pathActiveProjectsData), [])
	
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
	activeProjects = readJsonFile(systemPath(pathActiveProjectsData), [])
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

def cleanupOldProjects():
	delete_old_folders(systemPath(pathActiveRenders))
		
def delete_old_folders(root_folder):
	"""
	Scans all subfolders in root_folder, filters those older than 2 weeks,
	and prompts the user to delete them.

	Args:
		root_folder (str): Path to the root directory to scan.
	"""
	# Ensure the root folder exists
	if not os.path.isdir(root_folder):
		print(f"Error: '{root_folder}' is not a valid directory.")
		return

	# Calculate the cutoff date (2 weeks ago)
	two_weeks_ago = datetime.now() - timedelta(weeks=2)
	
	# List to store folders older than 2 weeks
	old_folders = []

	# Walk through all subdirectories
	for dirpath, dirnames, filenames in os.walk(root_folder):
		# Skip the root folder itself, only process subfolders
		if dirpath == root_folder:
			continue
		
		# Get the last modified time of the folder
		mod_time = datetime.fromtimestamp(os.path.getmtime(dirpath))
		
		# Check if the folder is older than 2 weeks
		if mod_time < two_weeks_ago:
			old_folders.append(dirpath)

	# If no old folders found, inform the user and exit
	if not old_folders:
		print(f"No subfolders older than 2 weeks found in '{root_folder}'.")
		return

	# Sort folders for consistent output (optional)
	old_folders.sort()

	# Iterate through old folders and prompt for deletion
	for folder in old_folders:
		while True:
			# Display folder path and last modified date
			mod_time_str = datetime.fromtimestamp(os.path.getmtime(folder)).strftime('%Y-%m-%d %H:%M:%S')
			print(f"\nFolder: {folder}")
			print(f"Last modified: {mod_time_str}")
			
			# Prompt user for input
			response = input("Delete this folder? (y/n): ").strip().lower()
			
			if response == 'y':
				try:
					shutil.rmtree(folder)  # Delete the folder and its contents
					print(f"Deleted: {folder}")
					break
				except Exception as e:
					print(f"Error deleting {folder}: {e}")
					break
			elif response == 'n':
				print(f"Skipped: {folder}")
				break
			else:
				print("Invalid input. Please enter 'y' for yes or 'n' for no.")

def cancelActiveRender():
	activeProjects = getActiveProjects()
	if len(activeProjects) == 0:
		print('No Active projects to cancel!')
		sys.exit()

	print('\n\nSelect which active project to cancel')
	index = 0
	for project in activeProjects:
		print(str(index) + ') - Name: ' + project['blendName'])
		index += 1

	cancelIndex = input('Project to Cancel: ')
	index = int(cancelIndex)

	if index < 0 or index > len(activeProjects) - 1:
		print("Error: Index is out of bounds. Exiting.")
		sys.exit()

	project = activeProjects[index]
	project['status'] = Status.CANCELLED.name
	writeJsonToFile(activeProjects, systemPath(pathActiveProjectsData))


def takeActionMonitorProgress():
	
	print('Monitoring Renders - In Progress')
	while True:
		updateMonitoringData()
		time.sleep(60.0)  

#Start of Script

chooseAction()



