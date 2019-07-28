
$url = Read-Host 'What is the youtube url? '
#youtube-dl -F $url
#$videoOption = Read-Host 'What video quality? '
#$audioOption = Read-Host 'What audio Quality? '
#$path = Read-Host 'What file name (no extension)' ?
$fullPath = 'C:\Users\ricky\Movies\youtube_audio'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}

youtube-dl -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 $url -o "$fullPath\%(title)s.%(ext)s"
