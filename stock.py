import os, subprocess, platform
from os import listdir
from os.path import isfile, join



def filter_files_for_videos(files):
    return [v.lower() for v in files if v.lower().endswith('.mp4') or v.lower().endswith('.mov') or v.lower().endswith('.avi')]


def trim_code(start, duration):
    if not start and not duration:
        return ''
    elif not start:
        return ' -ss 00:00:00 -t ' + duration + ' '
    elif not duration:
        return ' -ss ' + start + ' -t 10:00:00 '
    else:
        return ' -ss ' + start + ' -t ' + duration + ' '


def edit_code(gamma, saturation, contrast,is_preview):
    if gamma and saturation and contrast:
        return ' -vf "eq=gamma=' + gamma + ':saturation=' + saturation + ':contrast=' + contrast + '" '
    else:
        if is_preview:
            return ''
        else:
            return ' -vcodec copy '

def encode_video(video, start, duration, gamma, saturation, contrast):
    os.system('ffmpeg -i ' + video + trim_code(start, duration) + edit_code(gamma, saturation, contrast, False) + '-an ' + destination_folder + video)


def process_video(video):
    should_trim = input('Trim Video (y)es / (n)o or (s)kip video: ')
    if should_trim == 's':
        return True

    trim_start = ''
    trim_duration = ''
    gamma = ''
    saturation = ''
    contrast = ''

    if should_trim == 'y':
        trim_start = input('Start Timestamp (00:00:00) :  ')
        trim_duration = input('Duration (00:00:00) :  ')
    should_edit_video = input('Edit Video Gamma/Saturation/contrast ? (y)es / (n)o: ')

    if should_edit_video == 'y':
        gamma = input('Gamma (0.1 - 10.0) (1.0 = normal)?  ')
        saturation = input('Saturation (0.0 - 3.0) (1.0 = normal)?  ')
        contrast = input('Contrast (-2.0 - 2.0) (1.0 = normal)?  ')

    if should_trim == 'y' or should_edit_video == 'y':
        should_preview = input('Preview Video? (y/n): ')

        if should_preview == 'y':
            preview_string = 'ffplay ' + trim_code(trim_start,trim_duration) + edit_code(gamma,saturation,contrast,True) + ' ' + video
            print('\n' + preview_string + '\n')
            os.system(preview_string)
            keep_settings = input('Keep Video Settings? (y)es / (n)o:  ') == 'y'
            if keep_settings:
                encode_video(video,trim_start, trim_duration, gamma, saturation, contrast)
                return True
            else:
                return False

    encode_video(video, trim_start, trim_duration, gamma, saturation, contrast)



#start of script
isWindows = platform.system() == 'Windows'
print("""


Where should we save this file?
The Base path will be C:\Script_Outputs\edited_videos\ *Your custom path*
A blank string will use the base path

""")
dest = input('Folder:  ')
destination_folder = 'C:\Script_Outputs\edited_videos' + '\\' + dest + '\\'
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

existing_vids = filter_files_for_videos(os.listdir(destination_folder))
print("""This folder has %s Videos. We'll skip these files in your working directory.
If you don't want that, delete these files in the destination folder before running the script!""" % str(len(existing_vids)))
currentPath = os.getcwd()
videos = filter_files_for_videos(os.listdir(currentPath))
print('Found ' + str(len(videos)) + ' videos total.')
videos = [x for x in videos if x not in existing_vids]
videos.sort()
print('Working on ' + str(len(videos)) + 'new videos.')

for video in videos:
    use_video = input('\nProcess video ' + video + '   (y)es / (n)o ?: ')
    if use_video == 'y':
        handled = False
        while handled == False:
            print('\nWorking on Video ' + video + '\n')
            handled = process_video(video)





