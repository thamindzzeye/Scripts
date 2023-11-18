
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
from threading import Timer
import re
from datetime import datetime
import shutil
import time


#folder watcher class
class Watcher(object):
    running = True
    refresh_delay_secs = 1

    # Constructor
    def __init__(self, watch_file, call_func_on_change=None, *args, **kwargs):
        self._cached_stamp = 0
        self.filename = watch_file
        self.call_func_on_change = call_func_on_change
        self.args = args
        self.kwargs = kwargs

    # Look for changes
    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            # File has changed, so do something...
            print('File changed')
            if self.call_func_on_change is not None:
                self.call_func_on_change(*self.args, **self.kwargs)

    # Keep watching in a loop        
    def watch(self):
        while self.running: 
            try: 
                # Look for changes
                time.sleep(self.refresh_delay_secs) 
                self.look() 
            except KeyboardInterrupt: 
                print('\nDone') 
                break 
            except FileNotFoundError:
                # Action on file not found
                pass
            except: 
                print('Unhandled error: %s' % sys.exc_info()[0])
                
#timer class

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

# Call this function each time a change happens
def custom_action(text):
    print(text)

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
pathActiveProjectsData = ['/Volumes/Scratch/Renders/Data/activeProjects.json', 'R:\\Data\\activeProjects.json']
computerName = getComputerName()
pathActiveNodeData = ['/Volumes/Scratch/Renders/Data/Nodes/' + computerName + '.json', 'R:\\Data\\Nodes\\' + computerName + '.json']
pathLocalRenderRoot = ['', 'C:\\Renders']

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
		print(str(index) + '. ' + project['projectName'])
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

## ----------------------------------------Render Node Functions! ---------------------------------------- ## 
def startRendering(renderDict):
	print("rendering!")

def ping(args):
	t = time.time()
	print(str(t))
	strTime = time.strftime("%Y-%m-%d %-I:%M:%S %p", time.localtime(t))
	print(strTime)
	nodeData = {}
	if os.path.exists(systemPath(pathActiveNodeData)):
		nodeData = readJsonFile(systemPath(pathActiveNodeData))
	else:
		nodeData['NodeName'] = computerName
	nodeData['ping'] = t
	
	#lets check if we're rendering yet
	if not renderNodeActive:
		activeRenders = readJsonFile(systemPath(pathActiveProjectsData))
		if len(activeRenders) > 0:
			#we have an active render we should start!
			render = activeRenders[0]
			startRendering(render)
			nodeData['ActiveProject'] = render['projectName']
		else:
			nodeData['ActiveProject'] = ''
			
	
	writeJsonToFile(nodeData, systemPath(pathActiveNodeData))

    


#Start of Script

#First let's create any needed folders
if not platform.system() == 'Windows':
	print('Render Node is only made for windows PCs with NVidia GPUs!')
	sys.exit()

#create the local folders
localRoot = systemPath(pathLocalRenderRoot)
localData = os.path.join(localRoot, 'Data')
localProject = os.path.join(localRoot, 'Projects')
if not os.path.exists(localRoot):
	os.makedirs(localRoot)
if not os.path.exists(localData):
	os.makedirs(localData)
if not os.path.exists(localProjects):
	os.makedirs(localProjects)
	

activeRenders = readJsonFile(systemPath(pathActiveProjectsData))
os.system('clear')
print(computerName + ' Reporting for Duty & Ready to Render!!\n\nActive Renders...\n')
listItemsInArray(activeRenders)
ping('start')
# rt = RepeatedTimer(60, ping, "ping")

with open("stdout.txt","wb") as out, open("stderr.txt","wb") as err:
	subprocess.Popen("ls",stdout=out,stderr=err)



#watch_file = 'my_file.txt'
#
## watcher = Watcher(watch_file)  # simple
#watcher = Watcher(watch_file, custom_action, text='yes, changed')  # also call custom action function
#watcher.watch()  # start the watch going







with open("stdout.txt","wb") as out, open("stderr.txt","wb") as err: subprocess.Popen("ls",stdout=out,stderr=err)



