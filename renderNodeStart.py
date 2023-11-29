
import os, subprocess, platform, sys
from os import listdir
from os.path import isfile, join
from pathlib import Path
from datetime import datetime
import shutil


def linuxPath(path):
	path = path.replace('\\','/')
	parts = path.split(':')
	path = '/cygdrive/' + parts[0] + parts[1]
	return path

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## ------------------------------------------------------ START OF SCRIPT! --------------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##


subprocess.run(["rsync", "-a", "--progress", linuxPath('R:\\Scripts\\renderNode.py'), linuxPath('C:\\Code\\Scripts\\renderNode.py')], shell=True)
subprocess.run(["rsync", "-a", "--progress", linuxPath('R:\\Scripts\\renderNodeStats.py'), linuxPath('C:\\Code\\Scripts\\renderNodeStats.py')], shell=True)
subprocess.run(["rsync", "-a", "--progress", linuxPath('R:\\Scripts\\renderMaster.py'), linuxPath('C:\\Code\\Scripts\\renderMaster.py')], shell=True)

print('updates complete!')

os.system('C:\\Code\\Scripts\\renderNode.py')
