
import os, subprocess, platform, sys
from os import listdir
from os.path import isfile, join
from pathlib import Path
import re
import urllib
import urllib.request
import csv
import numpy as np




debug = True

path = os.path.expanduser('~/Downloads/YTReport.csv')

channels = [{'name':'Undecided with Matt Ferrell', 'url':'https://www.youtube.com/@UndecidedMF/videos'}
            , {'name':'Just Have a Think', 'url':'https://www.youtube.com/justhaveathink/videos'}
            , {'name':'Freethink', 'url':'https://www.youtube.com/@freethink/videos'}
            , {'name':'Ziroth', 'url':'https://www.youtube.com/@ZirothTech/videos'}
            , {'name':'DW Planet A', 'url':'https://www.youtube.com/@DWPlanetA/videos'}
            , {'name':'Tech for Luddites', 'url':'https://www.youtube.com/@TechforLudditesSira/videos'}
            , {'name':'Subject Zero Science', 'url':'https://www.youtube.com/@SubjectZeroScience/videos'}
            , {'name':'Real Engineering', 'url':'https://www.youtube.com/@RealEngineering/videos'}
            ]

def log(str):
    if debug:
        print(str)

def getPage(url):
    opener = urllib.request.FancyURLopener({})
    f = opener.open(url)
    content = f.read()
    return str(content, 'UTF-8')

def getSubscribersCount(str):
    check = str.lower()
    subscribersRegex = '(\d+(?:\.\d+)?[mk]\ssubscribers)'
    subsMatch = re.findall(subscribersRegex, check, re.ASCII)
    subStr = subsMatch[-1]
    subStr = subStr.replace(' subscribers','')

    if 'm' in subStr:
        subStr = subStr.replace('m','')
        subNum = float(subStr)
        subNum = subNum * 1000000
        return int(subNum)
    if 'k' in subStr:
        subStr = subStr.replace('k','')
        subNum = float(subStr)
        subNum = subNum * 1000
        return int(subNum)
    return int(subStr)

def convertToDays(str):
    splitUp = str.split(' ')
    days = int(splitUp[0])
    timePeriod = splitUp[1]
    if 'month' in timePeriod:
        days = days * 30
    if 'year' in timePeriod:
        days = days * 365
    return days

def runReport(dict):
    url = dict['url']
    channelName = dict['name']
    content = getPage(url)
    subscribers = getSubscribersCount(content)
    regexStr = '{"label":[^}]+}'
    matches = re.findall(regexStr, content)

    data = []
    dataArray = [['Channel Name', 'Video Title', 'Days Since Post', 'Views']]
    averageViews = 0
    totalMatches = 0
    for match in matches:
        if ' by ' in match and ' views' in match:
            totalMatches = totalMatches + 1
            match = match.replace('{"label":"','')
            match = match.replace('"}','')
            viewsRegex = '([0-9]|,)* views'
            result = re.search(viewsRegex, match)
            viewsStr = result.group()
            result = result.group().replace(' views','')
            result = result.replace(',','')


            views = int(result)
            averageViews = averageViews + (views / 1000)
            match = match.replace(viewsStr,'')
            splitter = ' by ' + channelName + ' '
            splitList = match.lower().split(splitter.lower())
            datePost = splitList[1].split(' ago ')
            duration = datePost[1] #TODO
            datePost = datePost[0]
            days = convertToDays(datePost)
            row = [channelName, splitList[0].capitalize(), days, views]
            data.append(row)
            # data = data + channelName + ',' + splitList[0].capitalize() + ',' + str(days) + ',' + str(views) + '\n'

    averageViews = round((averageViews / totalMatches) * 1000)

    for row in data:
        row.append(str(subscribers))
        row.append(str(averageViews))
        viewScore = round(row[3] / averageViews * 100) / 100
        row.append(str(viewScore))
        subsScore = round(row[3] / subscribers * 100) / 100
        row.append(str(subsScore))
        row[2] = str(row[2])
        row[3] = str(row[3])
    return data

def createReport(data):
    #Open CSV file whose path we passed.
    file = open(path, 'w+', newline ='')
    with file:
        write = csv.writer(file)
        write.writerows(data)



data = [['Channel', 'Video Title', '# of Days', '# of Views', '# of Subs', 'Avg Views', 'Views/Avg', 'Views/Sub']]
for channel in channels:
    nextData = runReport(channel)

    data = data + nextData
createReport(data)