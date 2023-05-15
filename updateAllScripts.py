
import os
import shutil
import subprocess



rootPath = os.path.expanduser('~')
downloadsPath = os.path.join(rootPath, 'Downloads')
moviesPath = os.path.join(rootPath, 'Movies')

os.chdir(downloadsPath)

def getFcpxPlugins():
	dropboxLocation = os.path.expanduser('~/Two Bit da Vinci Dropbox/Two Bit Media/Software/Final Cut Plugins')
	finalCutLocation = os.path.expanduser('~/Movies/Motion Templates.localized')
	print('Updating Final Cut Plugings...\n\n1. Please make sure Dropbox > Two Bit Media > Software > Final Cut Plugins is available offline\n2. make sure dropbox has sycned it and there is no other changes\n\n')
	userInput = input('Ready? (y/n): ')
	userInput = userInput.lower()
	
	if not userInput == 'y':
		sys.exit()
	
	print('\n\nWhat would Like to do?\n\n1. Download the latest plugins\n2. Add New Plugins (Only for Juan)\n\n')
	userInput = input('Selection (1 or 2): ')
	
	sourceDestination = dropboxLocation
	targetDestination = finalCutLocation
	
	if userInput == '2':
		userInput = input('JUAN ONLY, Enter Password: ')
		if not userInput == '811':
			print('Incorrect Password, Aborting')
			sys.exit()
		sourceDestination = finalCutLocation
		targetDestination = dropboxLocation
	
	rsyncString = "rsync -av --delete --progress '" + sourceDestination + "/' '" + targetDestination + "'"
	os.system(rsyncString)
		

def getFcpxPluginsOld():
    githubPath = os.path.join(downloadsPath, 'FcpxPlugins')
    origination = os.path.join(githubPath, 'Motion Templates.localized')
    destination = os.path.join(moviesPath, 'Motion Templates.localized')
    presetsDestination = os.path.join(rootPath, "Library/Application Support/ProApps/Effects Presets")
    presetsOrigination = os.path.join(destination, 'Presets')

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

    #Lets add the presets Now
    for root, dirs, files in os.walk(presetsDestination):
        for file in files:
            os.remove(os.path.join(root, file))
    for root, dirs, files in os.walk(presetsOrigination):
        for file in files:
            start = os.path.join(root, file)
            shutil.move(start, presetsDestination)

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
alias checkinCheckout="python3 ~/Code/Scripts/checkinCheckoutProject.py"
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
