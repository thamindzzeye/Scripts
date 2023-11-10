
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
from datetime import datetime
import shutil
import sys


fileChanged = sys.argv[1]



path = os.path.expanduser('~/Downloads/test.txt')
file = open(path, 'w+', newline ='')

dirs = fileChanged.split('/')
file = dirs[-1]
parentDir = os.path.dirname(fileChanged)



with open(path, 'w') as f:
    f.write('file changed: ' + file + ' folder: ' + parentDir)