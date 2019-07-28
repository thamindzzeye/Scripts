
$filename = Read-Host 'What is the filename? '
$trim = Read-Host 'Trim the Video Length? (y/n) '
$trim_code = ''

$fullPath = 'C:\Script_Outputs\edited_videos\'

If(!(test-path $fullPath))
{
      New-Item -ItemType Directory -Force -Path $fullPath
}

If($trim -eq 'y') {
  $begin = Read-Host 'What is the start timestamp? '
  $duration = Read-Host 'What is the duration? '
  $trim_code = (' -ss ' + $begin + ' -t ' + $duration)
}

$audio = Read-Host 'Include Audio? (y/n) '
$audio_code = '-an'
$video_code = ' -vcodec copy '
If($audio -eq 'y')
{
  $audio_code = '-acodec copy '
}
$edit_video = Read-Host 'Edit Video Gamma/Saturation? '
$video_satisfied = 'n'
If($edit_video -eq 'y') {
  $gamma = 1.0
  $saturation = 1.0
  $contrast = 1.0
  While($video_satisfied -ne 'y') {
    If($video_satisfied -eq 'q') {
      break
    }
    $gamma = Read-Host 'Gamma (0.1 - 10.0) (1.0 = normal)? '
    $saturation = Read-Host 'Saturation (0.0 - 3.0) (1.0 = normal)? '
    $contrast = Read-Host 'Contrast (-2.0 - 2.0) (1.0 = normal)? '
    $shouldPreview = Read-Host 'Preview Video? (y/n) '
    If($shouldPreview -eq 'y') {
      $previewString = 'ffplay -vf "eq=gamma=' + $gamma + ':saturation=' + $saturation + ':contrast=' + $contrast + '" ' + $filename
      Write-Host $previewString
      Invoke-Expression $previewString
      $video_satisfied = Read-Host 'Keep Video Settings? (y/n) '
    }
  }
  If($video_satisfied -eq 'y') {
    $video_code = ' -vf "eq=gamma=' + $gamma + ':saturation=' + $saturation + ':contrast=' + $contrast + '" '
  }
}
#ffmpeg -i $filename -ss $begin -t $duration -vcodec copy $audio_code copy G:\Stock_footage\$filename
#ffmpeg -i $filename $trim_code -vcodec copy $audio_code copy G:\Stock_footage\$filename

$finalString = 'ffmpeg -i ' + $filename + $trim_code + $video_code + $audio_code + ' ' + $fullPath + $filename
Write-Host $finalString
Invoke-Expression $finalString
