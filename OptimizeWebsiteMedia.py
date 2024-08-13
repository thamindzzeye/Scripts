
import os, subprocess, platform, sys, json
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
import datetime
import shutil
import time


#Global Variables
debug = False

#Global Paths
workingDir = os.getcwd()

rootPath =  os.path.expanduser('~/Downloads/WebsiteMedia')
outputPath = os.path.join(rootPath, 'Output')
videoExts = ['.mkv', '.avi', '.mp4', '.mov', '.m4v']
imageExts = ['.jpg', '.jpeg', '.png']

def getFilenameWithoutExtension(full_path):
    # Extract the base name from the full path
    base_name = os.path.basename(full_path)
    # Split the base name into name and extension
    file_name, _ = os.path.splitext(base_name)
    return file_name

def ensureFolderExists(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        try:
            # Create the folder if it doesn't exist
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except Exception as e:
            print(f"Failed to create folder '{folder_path}': {e}")

def findFilesByExtension(folder_path, extensions):
    """
    Finds files in the specified folder that match the given extensions.

    Parameters:
    - folder_path (str): Path to the folder to search.
    - extensions (list of str): List of file extensions to match.

    Returns:
    - list of str: List of file paths that match the specified extensions.
    """
    matched_files = []

    # Validate folder path
    if not os.path.isdir(folder_path):
        raise ValueError(f"Invalid folder path: {folder_path}")

    # Get all files in the folder
    files = os.listdir(folder_path)

    # Filter files based on extensions
    for file in files:
        _, file_ext = os.path.splitext(file)
        if file_ext.lower() in extensions:
            matched_files.append(os.path.join(folder_path, file))

    return matched_files

def convertImagestoWebp(files):
    quality = input('Specify quality (50 is usual 100 is max): ')
    for file in files:
        newFile = os.path.join(outputPath, getFilenameWithoutExtension(file) + '.webp')
        cmd = 'magick "' + file + '" -quality ' + quality + ' -define webp:lossless=false  "' + newFile + '"'
        os.system(cmd)

ensureFolderExists(rootPath)
ensureFolderExists(outputPath)

print("videos")
videosArray = findFilesByExtension(rootPath, videoExts)


print('images')
imagesArray = findFilesByExtension(rootPath, imageExts)

convertImagestoWebp(imagesArray)