import os
from datetime import datetime
import subprocess, json

def getMediaLength(filename):
    

    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
    print(result)
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration

def get_video_metadata(folder_path):
    """
    Reads all video files in the specified folder and returns a dictionary with metadata.

    Parameters:
        folder_path (str): Path to the folder containing video files.

    Returns:
        dict: A dictionary with video metadata including the creation timestamp, duration, and file path.
    """
    # Supported video file extensions
    video_extensions = ('.mp4', '.wav')
    video_extensions = ('.wav')

    video_metadata = []
    
    # Walk through the directory
    for root, _, files in os.walk(folder_path):

        for file in files:

            if file.lower().endswith(video_extensions):

                file_path = os.path.join(root, file)
                print(file_path)
                # Get the creation timestamp
                created_timestamp = os.path.getctime(file_path)
                created_datetime = datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                duration = getMediaLength(file_path)
                
                # Add metadata to dictionary
                video_metadata.append( {
                    'created': created_datetime,
                    'duration': duration,
                    'path': file_path
                })
    
    return video_metadata


print('starting')
folderPath = input('Choose Path: ')
# folderPath = '/Users/ricky/Downloads'
result = get_video_metadata(folderPath)

for item in result:
    print(item)

