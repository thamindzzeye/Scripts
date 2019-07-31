
$filename = Read-Host 'What is the filename? '

$fullPath = 'C:\Script_Outputs\edited_videos\'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}

$finalString = 'ffmpeg -i "' + $filename + '"' + '-filter:v "crop=3840:2160:0:0"' + ' "' + $fullPath + $filename + '"'
Write-Host $finalString
Invoke-Expression $finalString
