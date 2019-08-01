import os, subprocess
from os import listdir
from os.path import isfile, join


def filter_files_for_videos(files):
    return [v for v in files if v.lower().endswith('.mp4') or v.lower().endswith('.mov') or v.lower().endswith('.avi')]

def trim_code(start,duration):
    return ' -ss ' + trim_start + ' -t ' + trim_duration + ' '

def edit_code(gamma, saturation, contrast):
    if gamma and saturation and contrast:
        return ' "eq=gamma=' + gamma + + ':saturation=' + saturation + ':contrast=' + contrast + '"'


def process_video(video):
    should_trim = input('Trim Video (y)es / (n)o?: ')
    if should_trim == 'y':
        trim_start = input('Start Timestamp (00:00:00) :  ')
        trim_duration = input('Duration (00:00:00) :  ')
    should_edit_video = input('Edit Video Gamma/Saturation/contrast ? (y)es / (n)o: ')

    if should_edit_video == 'y':
        gamma = input('Gamma (0.1 - 10.0) (1.0 = normal)?  ' )
        saturation = input('Saturation (0.0 - 3.0) (1.0 = normal)?  ')
        contrast = input('Contrast (-2.0 - 2.0) (1.0 = normal)?  ')
        should_preview = input('Preview Video? (y/n): ')

        if should_preview == 'y':
            os.system('ffplay -i ' + video + trim_code(trim_start,trim_duration) + edit_code(gamma,saturation,contrast) )
            keep_settings = input('Keep Video Settings? (y)es / (n)o:  ')



currentPath = os.getcwd()
videos = filter_files_for_videos(os.listdir(currentPath))
print(videos)

for video in videos:
    use_video = input('process video ' + video + '   (y)es / (n)o ?: ')
    if use_video == 'y':
        process_video(video)




