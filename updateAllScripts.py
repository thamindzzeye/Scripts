
import os
import shutil




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

getFcpxPlugins()
