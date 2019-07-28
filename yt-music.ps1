
$url = Read-Host 'What is the youtube url? '
$fullPath = 'C:\Script_Outputs\youtube'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}

youtube-dl -f bestaudio --extract-audio --audio-format mp3 --audio-quality 0 $url -o "$fullPath\%(title)s.%(ext)s"
