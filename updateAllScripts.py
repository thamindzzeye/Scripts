
import os
import shutil
import subprocess



rootPath = os.path.expanduser('~')
downloadsPath = os.path.join(rootPath, 'Downloads')
moviesPath = os.path.join(rootPath, 'Movies')

os.chdir(downloadsPath)

def getFcpxPlugins():
    githubPath = os.path.join(downloadsPath, 'FcpxPlugins')
    origination = os.path.join(githubPath, 'Motion Templates.localized')
    destination = os.path.join(moviesPath, 'Motion Templates.localized')
    print('Updating Final Cut Pro Plugins...')
    if os.path.exists(githubPath):
        os.chdir(githubPath)
        os.system('git pull')
    else:
        os.system('git clone git@github.com:thamindzzeye/FcpxPlugins.git')

    shutil.rmtree(destination, ignore_errors=True)
    print('Moving to ' + destination)
    shutil.move(origination, destination)
    shutil.rmtree(githubPath, ignore_errors=True)

    print("""
    Finished Updating Final Cut Pro Plugins.
    Please Force Quit Final Cut Pro
    To Make sure Changes Take Effect

    """)

def copy2clip(txt):
    cmd='echo '+txt.strip()+'|pbcopy'
    return subprocess.check_call(cmd, shell=True)

def getScripts():
    codePath = os.path.join(rootPath, 'Code')
    scriptsPath = os.path.join(codePath, 'Scripts')
    if os.path.exists(codePath) == False:
        os.makedirs(codePath)
    os.chdir(codePath)
    if os.path.exists(scriptsPath) == False:
        os.system('git clone git@github.com:thamindzzeye/Scripts.git')
    os.chdir(scriptsPath)
    os.system('git reset --hard origin/master')
    os.system('git pull')

def updateAliases():
    filePath = os.path.join(rootPath, '.zshrc')
    if os.path.exists(filePath) == False:
        os.system('touch ' + filePath)
    aliasValues = """
alias youtube_music="python3 ~/Code/Scripts/yt-music.py"
alias py=python3
alias youtube="python3 ~/Code/Scripts/youtube.py"
alias img2mov="python3 ~/Code/Scripts/createVideoFromImages.py"
alias imageUpscale="python3 ~/Code/Scripts/image_upscale.py"
alias imageResearcher="python3 ~/Code/Scripts/GetImagesFromGoogle.py"
alias updateAllScripts="python3 ~/Code/Scripts/updateAllScripts.py"
alias testScript="python3 ~/Code/Scripts/test.py"
alias createSampleVideo="python3 ~/Code/Scripts/createSampleVideos.py"
"""
    copy2clip(aliasValues)
    print("""
    Next we are going to update the shortcuts.

    1. A new window just popped up you see it?
    2. Delete everything
    3. Copy the following Text between the ************  and Copy it to the file,
    4. Be sure to save it
    5. Now you can close this window

    Restart Final Cut Pro, and Terminal Before you use the new tools!

************
    """)
    print(aliasValues)
    os.system('open ~/.zshrc')
    print('************')


os.system('clear')
getFcpxPlugins()
getScripts()
updateAliases()
