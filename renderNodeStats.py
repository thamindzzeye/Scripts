import os, subprocess, platform, sys, json
from enum import Enum
from os import listdir
from os.path import isfile, join
from pathlib import Path
from threading import Timer
import re
from datetime import datetime
import shutil
import time
import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Global Variables
lastTime = time.time()
lastFile = ''
pathRendersRoot = ['/Volumes/Scratch/Renders/Active Renders', 'R:\\Active Renders']
pathActiveProjects = ['/Volumes/Scratch/Renders/Data/activeProjects.json', 'R:\\Data\\activeProjects.json']
pathDataRoot = ['/Volumes/Scratch/Renders/Data/Projects', 'R:\\Data\\Projects']

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Global Helper Functions  ----------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def getComputerName():
    name = platform.node()
    parts = name.split('.')
    return parts[0]

def systemPath(pathArray):
    index = int(platform.system() == 'Windows')
    path = pathArray[index]
    return path

def linuxPath(path):
    path = path.replace('\\','/')
    parts = path.split(':')
    path = '/cygdrive/' + parts[0] + parts[1]
    return path

def monitorDirectory():
    path = ['/Volumes/Scratch/Renders/Data/Nodes', 'R:\\Data\\Nodes']
    return systemPath(path)

def readJsonFile(path, errorDefault):
    try:
        with open(path, "r") as jsonData:
            data = json.load(jsonData)
            return data
    except:
        return errorDefault

def writeJsonToFile(dataDict, filePath):
    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(dataDict, f, ensure_ascii=False, indent=4)

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Watcher Class Functions  ----------------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

class OnMyWatch:
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, monitorDirectory(), recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        global lastTime
        global lastFile

        # Prevent Duplicate Calls
        file = event.src_path
        newTime = time.time()
        if file == lastFile and newTime < lastTime + 5:
            return None
        elif event.event_type == 'created' or event.event_type == 'modified':
            parseNewJsonFile(event.src_path)
            lastFile = file
            lastTime = newTime

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------------- Core Analytics Functions  ---------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def parseNewJsonFile(filePath):
    time.sleep(2)
    t = time.time()
    strTime = time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime(t))
    print('T: ' + strTime + ' File: ' + filePath)
    if not filePath.endswith('.json'):
        return
    if not os.path.exists(filePath):
        return
    newArray = readJsonFile(filePath, [])
    split = filePath.split('\\')
    computer = split[-2]
    projectName = split[-1].replace('.json', '')

    framesFolder = os.path.join(systemPath(pathRendersRoot), projectName)
    if not os.path.exists(framesFolder):
        return
    activeProjects = readJsonFile(systemPath(pathActiveProjects), [])
    activeProject = {}
    for project in activeProjects:
        if project['blendName'] == projectName + '.blend':
            activeProject = project
    if len(activeProject.keys()) == 0:
        return
    startFrame = int(activeProject['startFrame'])
    endFrame = int(activeProject['endFrame'])
    
    jsonPath = os.path.join(systemPath(pathDataRoot), projectName + '.json')
    htmlPath = os.path.join(systemPath(pathDataRoot), projectName + '_dashboard.html')
    dataDict = {}
    if os.path.exists(jsonPath):
        dataDict = readJsonFile(jsonPath, {})
    else:
        dataDict['frames'] = {}

    hasChanged = False
    framesData = dataDict['frames']
    newestCreatedFrame = 0
    for frame, duration in newArray.items():
        if frame in framesData:
            d = framesData[frame]
            if computer == d[0] and duration == d[1]:
                continue

        hasChanged = True
        filesize, created, rawTime = getFileStats(framesFolder, frame)
        newestCreatedFrame = max(newestCreatedFrame, rawTime)
        if filesize:
            newEntry = [computer, duration, filesize, created]
            framesData[frame] = newEntry

    if hasChanged:
        if 'nodes' not in dataDict:
            dataDict['nodes'] = {}

        nodes = dataDict['nodes']
        if computer not in nodes:
            nodes[computer] = {}

        nodeData = nodes[computer]
        totalFrames = 0
        totalDuration = 0.0
        lastFrame = 0
        for frame, duration in newArray.items():
            totalDuration += duration
            totalFrames += 1
            lastFrame = max(lastFrame, int(frame))
        averageTime = totalDuration / float(totalFrames)
        nodeData['averageFrame'] = round(averageTime, 1)
        nodeData['totalFrames'] = totalFrames
        nodeData['lastFrameDate'] = newestCreatedFrame
        nodeData['framesPerMinute'] = round(60 / averageTime, 2)
        nodeData['lastCompletedFrame'] = lastFrame
        nodeData['totalDuration'] = round(totalDuration, 0)

    if hasChanged:
        if 'analytics' not in dataDict:
            dataDict['analytics'] = {}

        analytics = dataDict['analytics']
        totalDuration = 0
        totalFrames = 0
        fpm = 0
        maxFrame = 0
        for computer, values in nodes.items():
            totalDuration += values['totalDuration']
            totalFrames += values['totalFrames']
            fpm += values['framesPerMinute']
            maxFrame = max(maxFrame, values['lastCompletedFrame'])

        activeRenders = readJsonFile(systemPath(pathActiveProjects), [])
        totalProjectFrameCount = 0
        for render in activeRenders:
            if render['blendName'] == projectName + '.blend':
                activeRender = render
                totalProjectFrameCount = int(activeRender['endFrame']) - int(activeRender['startFrame']) + 1
        
        percentComplete = round(totalFrames / totalProjectFrameCount, 2)
        missingFrames = totalProjectFrameCount - totalFrames

        timeRemaining = (float(missingFrames) / fpm) * 60  # in secs
        t = time.time()
        eta = time.strftime("%I:%M:%S %p %m-%d-%Y", time.localtime(t + timeRemaining))
        analytics['timeLeft'] = convertSecsToDaysMinutesSeconds(timeRemaining) + ' Remaining'
        analytics['ETA'] = 'ETA: ' + eta
        analytics['totalRenderTime'] = convertSecsToDaysMinutesSeconds(totalDuration) + ' of TOTAL Render Time'
        analytics['framesPerMinute'] = str(round(fpm, 1)) + ' Frames/Minute'
        analytics['percentCompleteStr'] = str(round(percentComplete * 100, 0)) + '% Complete'
        analytics['percentComplete'] = percentComplete

    if hasChanged:
        print('New data detected, updating JSON and generating HTML...')
        writeJsonToFile(dataDict, jsonPath)  # Save to JSON
        writeHtmlFile(dataDict, htmlPath)    # Generate HTML
    else:
        print('No new data')

def convertSecsToDaysMinutesSeconds(seconds):
    days = math.floor(seconds / 86400.0)
    seconds = seconds - days * 86400.0
    hours = math.floor(seconds / 3600.0)
    seconds = seconds - hours * 3600.0
    minutes = math.floor(seconds / 60.0)
    timeLeft = ''
    if minutes > 0:
        timeLeft = str(minutes) + ' Mins'
    if hours > 0:
        timeLeft = str(hours) + ' Hours, ' + timeLeft
    if days > 0:
        timeLeft = str(days) + ' Days, ' + timeLeft
    return timeLeft

def getFileStats(rootPath, index):
    file = os.path.join(rootPath, 'frame_' + str(index).zfill(4) + '.png')
    if not os.path.exists(file):
        return '', '', 0
    fileStat = os.stat(file)
    filesize = str(round(fileStat.st_size/1000000, 2)) + ' MB'
    rawTime = fileStat.st_mtime
    created = datetime.fromtimestamp(fileStat.st_mtime).strftime('%I:%M %p %m-%d-%Y')
    return filesize, created, rawTime

def writeHtmlFile(dataDict, filePath):
    # Generate HTML content with embedded data and sortable tables
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30"> <!-- Auto-refresh every 30 seconds -->
    <title>Render Data Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f2f5;
            color: #2c3e50;
        }}
        h1 {{
            text-align: center;
            color: #34495e;
            margin-bottom: 20px;
        }}
        .section {{
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 15px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background-color: #2980b9;
            color: white;
            font-weight: 600;
            cursor: pointer;
        }}
        th:hover {{
            background-color: #1f6391;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #ecf0f1;
            transition: background-color 0.2s;
        }}
        .analytics-box h2 {{
            color: #34495e;
            margin-bottom: 15px;
        }}
        .analytics-box p {{
            margin: 8px 0;
            font-size: 1.1em;
        }}
        #lastUpdated {{
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <h1>Render Data Dashboard</h1>

    <div class="section analytics-box">
        <h2>Render Analytics</h2>
        <p><strong>Time Left:</strong> {dataDict['analytics']['timeLeft']}</p>
        <p><strong>ETA:</strong> {dataDict['analytics']['ETA']}</p>
        <p><strong>Total Render Time:</strong> {dataDict['analytics']['totalRenderTime']}</p>
        <p><strong>Frames/Minute:</strong> {dataDict['analytics']['framesPerMinute']}</p>
        <p><strong>Progress:</strong> {dataDict['analytics']['percentCompleteStr']}</p>
    </div>

    <div class="section">
        <h2>Node Statistics</h2>
        <table class="sortable" id="nodesTable">
            <thead>
                <tr>
                    <th>Computer</th>
                    <th>Avg Frame (s)</th>
                    <th>Total Frames</th>
                    <th>Frames/Min</th>
                    <th>Last Frame</th>
                    <th>Total Time (s)</th>
                </tr>
            </thead>
            <tbody>
"""
    for nodeName, metadata in dataDict['nodes'].items():
        html_content += f"""                <tr>
                    <td>{nodeName}</td>
                    <td>{metadata['averageFrame']:.2f}</td>
                    <td>{metadata['totalFrames']}</td>
                    <td>{metadata['framesPerMinute']:.2f}</td>
                    <td>{metadata['lastCompletedFrame']}</td>
                    <td>{metadata['totalDuration']:.1f}</td>
                </tr>
"""
    html_content += """            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Frame Data</h2>
        <table class="sortable" id="framesTable">
            <thead>
                <tr>
                    <th>Frame</th>
                    <th>Computer</th>
                    <th>Time (s)</th>
                    <th>Size (MB)</th>
                    <th>Completed</th>
                </tr>
            </thead>
            <tbody>
"""
    for frameNum, frameData in dataDict['frames'].items():
        computer, renderTime, fileSize, timestamp = frameData
        sizeMB = parseFloat(fileSize.split(' ')[0])
        html_content += f"""                <tr>
                    <td>{frameNum}</td>
                    <td>{computer}</td>
                    <td>{renderTime:.2f}</td>
                    <td>{sizeMB:.2f}</td>
                    <td>{timestamp}</td>
                </tr>
"""
    html_content += f"""            </tbody>
        </table>
    </div>

    <div id="lastUpdated">Last updated: {datetime.now().strftime('%I:%M:%S %p')} | Project: {os.path.basename(filePath).replace('_dashboard.html', '')}</div>

    <script>
        function sortTable(n, tableId) {{
            var table = document.getElementById(tableId);
            var rows, switching = true, i, x, y, shouldSwitch, dir = "asc", switchcount = 0;
            while (switching) {{
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    var xContent = x.textContent;
                    var yContent = y.textContent;
                    // Handle numeric or date sorting
                    if (n === 0 || n === 2 || n === 3 || n === 5) {{ // Frame, Time (s), Size (MB), Total Frames, Total Time (s)
                        xContent = parseFloat(xContent) || 0;
                        yContent = parseFloat(yContent) || 0;
                    }} else if (n === 4) {{ // Completed (date/time)
                        xContent = new Date(xContent).getTime();
                        yContent = new Date(yContent).getTime();
                    }}
                    if (dir === "asc") {{
                        if (xContent > yContent) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }} else if (dir === "desc") {{
                        if (xContent < yContent) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }}
                }}
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }} else if (switchcount === 0 && dir === "asc") {{
                    dir = "desc";
                    switching = true;
                }}
            }}
        }}

        document.addEventListener("DOMContentLoaded", function() {{
            var tables = document.getElementsByClassName("sortable");
            for (var t = 0; t < tables.length; t++) {{
                var headers = tables[t].getElementsByTagName("th");
                for (var i = 0; i < headers.length; i++) {{
                    headers[i].addEventListener("click", (function(tableIndex, colIndex) {{
                        return function() {{ sortTable(colIndex, tables[tableIndex].id); }};
                    }})(t, i));
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open(filePath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML dashboard written to: {filePath}")

def parseFloat(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## -------------------------------------------------- Initialization & Startup Functions  ------------------------------------------------ ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

def initialize():
    if not platform.system() == 'Windows':
        print('Render Node is only made for windows PCs with NVidia GPUs!')
        sys.exit()

    localFile = 'C:\\Code\\Scripts\\renderNodeStats.py'
    remoteFile = 'R:\\Scripts\\renderNodeStats.py'
    localModified = os.path.getmtime(localFile)
    remoteModified = os.path.getmtime(remoteFile)
    if not remoteModified == localModified:
        subprocess.run(["rsync", "-a", "--progress", linuxPath(remoteFile), linuxPath(localFile)], shell=True)
        print('There was a change in the render script file, it has been updated. \nPlease run the Render Node again!\n----------------------------Exiting-----------------------------------')
        sys.exit()

    print('Initialization Checks Completed\n\n Progress Monitoring in Progress')

## --------------------------------------------------------------------------------------------------------------------------------------- ##
## --------------------------------------------------------------- Start of Script!  ----------------------------------------------------- ##
## --------------------------------------------------------------------------------------------------------------------------------------- ##

initialize()

if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()