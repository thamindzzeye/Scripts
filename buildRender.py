
import os, subprocess, platform, sys, json
from enum import Enum
from os import listdir
from os.path import isfile, join
from pathlib import Path
import runpy


#Global Variables
debug = False
renderNodeActive = False

def getComputerName():
	name = platform.node()
	parts = name.split('.')
	return parts[0]

#Global Paths
renderScriptsSource = '/Users/ricky/Code/Scripts'
renderScriptsDestination = '/Volumes/Scratch/Renders/Scripts'
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

#Start of Script

source = os.path.join(renderScriptsSource, 'renderNode.py')
destination = os.path.join(renderScriptsDestination, 'renderNode.py')
os.system('rsync -av --progress "' + source + '" "' + destination + '"')

source = os.path.join(renderScriptsSource, 'renderMaster.py')
destination = os.path.join(renderScriptsDestination, 'renderMaster.py')
os.system('rsync -av --progress "' + source + '" "' + destination + '"')

source = os.path.join(renderScriptsSource, 'renderNodeStats.py')
destination = os.path.join(renderScriptsDestination, 'renderNodeStats.py') 
os.system('rsync -av --progress "' + source + '" "' + destination + '"')
