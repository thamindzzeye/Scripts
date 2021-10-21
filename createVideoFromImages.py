
import os, subprocess, platform, sys
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re

#Global Variables
workingDir = os.getcwd()
destination = '~/Downloads/'

#Functions
def getAllUniqueFileNames():
    files = os.listdir(workingDir)
    uniques = []
    for file in files:

        split = file.split('_')
        if split[0].startswith('.'):
            continue
        if split[0] not in uniques:
            uniques.append(split[0])
    return uniques

def checkForMissingFiles():
    files = os.listdir(workingDir)
    missing = []
    numbers = []
    name = ''
    zeroes = 4
    extension = '.png'
    for file in files:
        if file.startswith('.'):
            continue
        split = file.split('_')
        split2 = split[1].split('.')
        number = split2[0]
        extension = split2[1]
        name = split[0]
        zeroes = len(number)
        numbers.append(int(number))

    numbers = sorted(numbers)

    #First lets check if files are files are missing
    missingFrames = []
    emptyFrames = []

    renameDelta = numbers[0] - 1
    checkFile = 1

    if numbers[0] == 0:
        renameDelta = 0
        checkFile = 0
    filesToDelete = []
    for index in numbers:
        rightNumber = index
        if renameDelta != 0:
            rightNumber = index - renameDelta
            oldName = os.path.join(workingDir, name + '_' + str(index).zfill(zeroes) + '.' + extension)
            newName = os.path.join(workingDir, name + '_' + str(rightNumber).zfill(zeroes) + '.' + extension)
            os.rename(oldName, newName)
        fileToCheck = os.path.join(workingDir, name + '_' + str(checkFile).zfill(zeroes) + '.' + extension)
        if os.path.exists(fileToCheck):
            #File exists
            size = os.path.getsize(fileToCheck)
            if size < 1000:
                #we have a bad file lets delete it
                emptyFrames.append(str(checkFile).zfill(zeroes))
                filesToDelete.append(fileToCheck)
                missingFrames.append(str(checkFile).zfill(zeroes))
        else:
            missingFrames.append(str(checkFile).zfill(zeroes))
        checkFile += 1

    format = name + '_' + '%0' + str(zeroes) + 'd.' + extension
    if len(missingFrames) > 0:
        print("""

        The following frames are MISSING!
        Please re-run blender with overwrite turned off to complete the renders
        Then run this program again!
        """)
        print('Empty files detected:')
        print(emptyFrames)
        deleteEmpty = input('Delete Empty zero byte frames? (y)es / (n)o) : ')
        if (deleteEmpty == 'y' or deleteEmpty == 'Y'):
            for file in filesToDelete:
                print('RROY: deleting!')
                os.remove(file)
        print('Missing Files:')
        print(missingFrames)
        sample = input('Render a sample for now? (y)es / (n)o) : ')
        if (sample == 'y' or sample == 'Y'):
            vFrame = ' -vframes ' + str(int(missingFrames[0]) - 1) + ' '
            createMovie(format, name + '-Partial', vFrame)
        sys.exit()


    createMovie(format, name + '-Complete', '')

def createMovie(format,outputName, vFrame):
    framerate = input('What framerate do you want for the movie? : ')
    print("""
    Do you want the alpha channel in the video?
    The background will be invisible, but the file size will be MUCH larger

    """)
    isAlpha = input('Use Alpha Channel? (y)es / (n)o) : ')
    fileLocation = '~/Downloads/' + outputName + '.mp4'
    fileInput = format
    if (isAlpha == 'y' or isAlpha == 'Y'):
        command = 'ffmpeg -framerate ' + framerate + ' -i \'' + fileInput + '\'' + vFrame + ' -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov ' + fileLocation
        #ffmpeg -framerate $framerate -i $fileInput -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov $fullPath
    else:
        command = 'ffmpeg -framerate ' + framerate + ' -i \'' + fileInput + '\'' + vFrame + ' -c:v libx264 -pix_fmt yuv420p ' + fileLocation
    print(command)
    os.system(command)

    print("""

    Complete






    """)


uniques = getAllUniqueFileNames()
if len(uniques) == 0:
    print("Directory is empty, quitting\n\n")
elif len(uniques) == 1:
    print(uniques[0] + ' Found Starting Program')
    checkForMissingFiles()
else:
    #ask user which they want to work with shouldn't happen
    sys.exit()
