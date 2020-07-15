
$fileInput = Read-Host 'What is the file name structure of the image? '
$framerate = Read-Host 'What framerate do you want for the movie? '
$outputName = Read-Host 'What Should the Video be named (no extension)? '
$workingDir = (Get-Location).Path


$fullPath = 'C:\Script_Outputs\movies\'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}
$fullPath = $fullPath + $outputName + '.mp4'
Write-Output "ffmpeg -framerate $framerate -i %file_input -c:v libx264 -pix_fmt yuv420p C:\Users\ricky\Movies\img2mov_outputs\$outputName.mp4"
ffmpeg -framerate $framerate -i $fileInput -codec prores_ks -pix_fmt yuva444p10le -alpha_bits 16 -profile:v 4444 -f mov $fullPath
