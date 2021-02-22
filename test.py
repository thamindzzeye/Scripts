
import os, subprocess, platform, urllib
from urllib.parse import urlparse
from os import listdir
from os.path import isfile, join
import re

destination_temp = "Downloads/Project/Progress/"
destination_folder = "Downloads/Project/Images/"
img = "test.png"
command = 'magick composite -geometry +' + str(0) + '+' + str(0) + ' ' + destination_temp + 'main_temp.png ' + destination_temp + 'bg_temp.png "' + destination_folder + img +'"'

print(command)
