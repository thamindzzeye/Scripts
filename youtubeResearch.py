
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
            , {'name':'Wendover Productions', 'url':'https://www.youtube.com/@Wendoverproductions/videos'}
            , {'name':'Kyle Hill', 'url':'https://www.youtube.com/@kylehill/videos'}
            , {'name':'Tom Scott', 'url':'https://www.youtube.com/@TomScottGo/videos'}
            , {'name':'Veritasium', 'url':'https://www.youtube.com/@Veritasium/videos'}
            , {'name':'Technology Connections', 'url':'https://www.youtube.com/@TechnologyConnections/videos'}
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
    days = int(splitUp[1])
    timePeriod = splitUp[2]
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
    regexId = '{"content":{"videoRenderer":{"videoId":".*?"'
    matches = re.findall(regexStr, content)
    matchesIds = re.findall(regexId, content)
    data = []
    dataArray = [['Channel Name', 'Video Title', 'Days Since Post', 'Views']]
    averageViews = 0
    totalMatches = 0
    for match in matches:

        if ' by ' in match and ' views' in match:
            vidId = ''
            if len(matchesIds) > 0:
                vidId = matchesIds.pop(0)
                vidId = vidId.replace('{"content":{"videoRenderer":{"videoId":"','')
                vidId = vidId.replace('\"','')
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
            row = [channelName, splitList[0].capitalize(),vidId, days, views]
            data.append(row)
            # data = data + channelName + ',' + splitList[0].capitalize() + ',' + str(days) + ',' + str(views) + '\n'

    averageViews = round((averageViews / totalMatches) * 1000)

    for row in data:
        row.append(str(subscribers))
        row.append(str(averageViews))
        viewScore = round(row[4] / averageViews * 100) / 100
        row.append(str(viewScore))
        subsScore = round(row[4] / subscribers * 100) / 100
        row.append(str(subsScore))
        row[3] = str(row[3])
        row[4] = str(row[4])
    return data

def createReport(data):
    #Open CSV file whose path we passed.
    file = open(path, 'w+', newline ='')
    with file:
        write = csv.writer(file)
        write.writerows(data)



data = [['Channel', 'Video Title','Video Id', '# of Days', '# of Views', '# of Subs', 'Avg Views', 'Views/Avg', 'Views/Sub']]
for channel in channels:
    print(channel)
    nextData = runReport(channel)

    data = data + nextData
createReport(data)
