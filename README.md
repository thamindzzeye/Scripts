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

To update your $profile

> Notepad $PROFILE

This will open up notepad, just copy and paste this in.
```
$ps_script_dir = "C:\Scripts\"

New-Alias img2mov $ps_script_dir\createVideoFromImages.ps1
New-Alias youtube $ps_script_dir\yt-dl.ps1
New-Alias trimVideo $ps_script_dir\trimVideo.ps1
New-Alias youtube_music $ps_script_dir\yt-music.ps1
```

Then Save the file, exit powershell, and relaunch it for the changes to take effect. 