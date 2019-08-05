
import os, subprocess, platform, PIL, shutil
from os import listdir
from os.path import isfile, join
from PIL import Image


def filter_files_for_images(files):
    return [v.lower() for v in files if v.lower().endswith('.webp') or v.lower().endswith('.jpg') or v.lower().endswith('.jpeg') or v.lower().endswith('.gif') or v.lower().endswith('.tiff') or v.lower().endswith('.png')]

isWindows = platform.system() == 'Windows'
destination_folder = 'C:\\Script_Outputs\\images\\'
destination_temp = 'C:\\Script_Outputs\\images_temp\\'

padding_all_sides = 100
width_4k = 3840
height_4k = 2160

os_user = 'ricky'
#if not isWindows:
    # todo make this work for mac



if not os.path.exists(destination_folder):
    os.makedirs(destination_temp)
else:
    if os.path.exists(destination_temp + 'main_temp.png'):
        os.remove(destination_temp + 'main_temp.png')
    if os.path.exists(destination_temp + 'bg_temp.png'):
        os.remove(destination_temp + 'bg_temp.png')

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

print("""
This Script will take smaller images, or non 16:9 4k Images, and make them better suited for our 4k videos

Please be in the folder the image is in. so that image name is just 'some image.jpg' or 'img.webp' etc...

""")
images = input('What is the image name? (leave blank to run all images in this folder) :  ')
if images:
    images = [images]
else:
    currentPath = os.getcwd()
    images = filter_files_for_images(os.listdir(currentPath))


padding_all_sides = float(input('How much padding around each side? (0 adds non extra) '))

for img in images:

    image = Image.open(img)

    width, height = image.size
    width_original = width
    height_original = height

    print('Image dimensions are ' + str(width) + ' x ' + str(height))
    factor_w = width_4k / width
    factor_h = height_4k / height
    width = width * min(factor_w,factor_h)
    height = height * min(factor_h, factor_w)


    command = 'magick "' + img + '" -interpolative-resize ' + str(width) + ' ' + destination_temp + 'main_temp.png'
    print('Image dimensions are ' + str(width) + ' x ' + str(height))
    print(command)
    os.system(command)

    #-blur 0x10
    width = width_original * max(factor_w, factor_h)
    height = height_original * max(factor_h, factor_w)

    final_width = width_4k + 2 * padding_all_sides
    final_height = height_4k + 2 * padding_all_sides

    command = 'magick "' + img + '" -interpolative-resize ' + str(width + 2 * padding_all_sides) + ' -blur 0x50 ' + ' -crop ' + str(final_width) + 'x' + str(final_height) + '+0+0 ' + destination_temp + 'bg_temp.png'
    print(command)
    os.system(command)

    bg_x_offset = 0
    bg_y_offset = 0
    main_x_offset = padding_all_sides
    main_y_offset = padding_all_sides
    width = width_original * min(factor_w,factor_h)
    height = height_original * min(factor_h, factor_w)
    print('h = ' + str(height) + ' w=' + str(width))
    if width >= width_4k:
        bg_x_offset = (width - (width_4k + padding_all_sides) / 2)
        main_y_offset = (height_4k - height) / 2 + padding_all_sides
    else:
        bg_y_offset = (height - (height_4k + padding_all_sides)) / 2
        main_x_offset = (width_4k - width) / 2 + padding_all_sides

    img = os.path.splitext(img)[0] + '.png'
    # command = 'magick composite -geometry +' + str(main_x_offset) + '+' + str(main_y_offset) + ' ' + destination_temp + 'main_temp.png -geometry ' + str(width_4k + padding_all_sides) + 'x' + str(height_4k + padding_all_sides) + '-' + str(bg_x_offset) + '+' + str(bg_y_offset) + ' ' + destination_temp + 'bg_temp.png ' + destination_folder + img_filename
    command = 'magick composite -geometry +' + str(main_x_offset) + '+' + str(main_y_offset) + ' ' + destination_temp + 'main_temp.png ' + destination_temp + 'bg_temp.png "' + destination_folder + img +'"'

    print(command)
    os.system(command)

print('Complete! check results at: ' + destination_folder)