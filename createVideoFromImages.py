
import os, subprocess, platform, sys
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re

#Global Variables
workingDir = os.getcwd()

destination = os.path.expanduser('~/Downloads')

dict = {}
debug = False

def log(str):
    if debug:
        print(str)

# [folderPath, file, name, number, extension]
def breakdownFilePath(fullPath):
    split = os.path.split(fullPath.lower())
    folderPath = split[0]
    file = split[1]
    regexStr = '[0-9]{2,8}\.(png|jpg)'
    match = re.search(regexStr, file.lower())
    name = file.replace(match.group(),"")
    substr = match.group()
    number = re.search('[0-9]{2,8}',substr)
    number = number.group()
    extension  = substr.replace(number,"")

    return [folderPath, file, name, number, extension]

def keyForFile(file):
    key = file.replace(workingDir, "").lower()
    regexStr = '[0-9]{2,8}\.(png|jpg)'
    match = re.search(regexStr, key)
    key = key.replace(match.group(),"")
    return key

def browseAllFiles(path):
    files = os.listdir(path)
    files = sorted(files)
    uniques = []
    for file in files:
        if file.startswith('.'):
            continue
        fullFilename = os.path.join(path, file)
        if os.path.isfile(fullFilename):
            array = breakdownFilePath(os.path.join(path, file))
            key = keyForFile(fullFilename)
            log("key = " + key)
            if key in dict:
                current = dict[key]
                current.append(array)
                dict[key] = current
                log(array)
                log(str(len(current)))
            else:
                dict[key] = [array]

        else:
            folder = os.path.join(path, file)
            browseAllFiles(folder)

def renameAllWithStartIndex(array):
    index = 1

    for list in array:
        log(list)
        oldPath = os.path.join(list[0], list[1])
        zeroes = len(list[3])
        newName = list[2] + str(index).zfill(zeroes) + list[4]
        newPath = os.path.join(list[0], newName)
        log(oldPath)
        log(newPath)
        os.rename(oldPath, newPath)
        index = index + 1

def reportMissingFrames(array):
    start = int(array[0][3])
    last = int(array[-1][3])
    index = start
    for list in array:
        number = int(list[3])
        if index == number:
            last = index
            index = index + 1
        else:

            print("\n\n MISSING Frames at " + str(index) + "\n\n  Will create a sample instead \n\n")
            break
    return [start, last]
    # for index in range(start, len(array)):
    #     log("OK")

def createMovie(format, outputName, startFrame, totalFrames,framerate, isAlpha):
    # fileLocation = '~/Downloads/' + outputName + '.mp4'
    fileInput = format
    if (isAlpha == 'y' or isAlpha == 'Y'):
        command = 'ffmpeg -framerate ' + framerate + startFrame + ' -i \'' + fileInput + '\'' + totalFrames + ' -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov ' + '\'' + outputName + '\''
        #ffmpeg -framerate $framerate -i $fileInput -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov $fullPath
    else:
        command = 'ffmpeg -framerate ' + framerate + startFrame + ' -i \'' + fileInput + '\'' + totalFrames + ' -c:v libx264 -pix_fmt yuv420p ' + outputName
    print(command)
    os.system(command)

    print("""

    Complete






    """)

def workOnImageSet(array, framerate, isAlpha):
    if len(array) == 0:
        return
    first = array[0]

    # First let's check for missing emptyFrames
    range = reportMissingFrames(array)
    print(array[0][1] + " working range [" + str(range[0]) + "," + str(range[1]) + "]" )

    format = array[0][2] + '%0' + str(len(array[0][3])) + 'd' + array[0][4]
    log(format)
    outputName = array[0][2] + '[' + str(range[0]) + '-' + str(range[1]) + '].mp4'
    outputName = os.path.join(destination, outputName)
    log(outputName)
    vFrame = ' -vframes ' + str(int(range[1])) + ' '
    startFrame = ' -start_number ' + str(range[0]) + ' '
    log(vFrame)
    os.chdir(array[0][0])

    createMovie(format, outputName, startFrame, vFrame, framerate, isAlpha)
    # createMovie(format, outputName, startNumber, totalFrames,framerate, isAlpha)

def beginCode():
    os.system("clear")

    framerate = input('What framerate do you want for the movie? : ')
    print("""
    Do you want the alpha channel in the video?
    The background will be invisible, but the file size will be MUCH larger

    """)
    isAlpha = input('Use Alpha Channel? (y)es / (n)o) : ')

    browseAllFiles(workingDir)
    print(str(len(dict.keys())) + " Types of files found")
    for key in dict.keys():
        item = dict[key]
        print(item[1])
    print("\n\n\n")

    for key in dict.keys():
        array = dict[key]
        workOnImageSet(array, framerate, isAlpha)




beginCode()
