
$url = Read-Host 'What is the youtube url? '
#youtube-dl -F $url
#$videoOption = Read-Host 'What video quality? '
#$audioOption = Read-Host 'What audio Quality? '
#$path = Read-Host 'What file name (no extension)' ?
$fullPath = 'C:\Users\ricky\Movies\youtube_dl'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}

youtube-dl -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]' $url -o "$fullPath\%(title)s.%(ext)s"
