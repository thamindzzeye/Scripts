# Scripts
All Mac and Windows scripts

WINDOWS
The first step is to get git bash for windows.
https://gitforwindows.org/

Once installed, open it and type

> cd c:

> git clone https://github.com/thamindzzeye/Scripts.git

This will clone the repo to the location C:\Scripts\

Then to update, just open git bash, go to the c:\Scripts directory and type
> git pull

net you'll need to install chocolately user powershell

open powershell as an administrator and then

```
Get-ExecutionPolicy
```
If it returns Restricted then run
```
Set-ExecutionPolicy Bypass -Scope Process
```

Now you will install chocolately
```
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

Now you need to install image magick
```
choco install imagemagick
```
```
choco install python
```
```
choco install pip
```
```
pip install pillow
```

To update your $profile

> Notepad $PROFILE

This will open up notepad, just copy and paste this in.
```
$ps_script_dir = "C:\Scripts\"
$env:PATHEXT += ";.py"

function runGenerator {python $ps_script_dir\video_generator.py}
function runImageUpscale {python $ps_script_dir\image_upscale.py}

New-Alias img2mov $ps_script_dir\createVideoFromImages.ps1
New-Alias img2mov $ps_script_dir\createVideoFromImagesAlpha.ps1
New-Alias youtube $ps_script_dir\yt-dl.ps1
New-Alias edit_video $ps_script_dir\trimVideo.ps1
New-Alias youtube_music $ps_script_dir\yt-music.ps1
New-Alias crop4k $ps_script_dir\crop4k.ps1
New-Alias stock $ps_script_dir\stock.ps1
New-Alias generator runGenerator
New-Alias image_upscale runImageUpscale

```

Then Save the file, exit powershell, and relaunch it for the changes to take effect.
