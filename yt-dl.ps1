
$url = Read-Host 'What is the youtube url? '
$fullPath = 'C:\Script_Outputs\youtube'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}

youtube-dl -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]' $url -o "$fullPath\%(title)s.%(ext)s"
