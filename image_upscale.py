
import os, subprocess, platform, PIL, shutil
from os import listdir
from os.path import isfile, join
from PIL import Image
from pathlib import Path

def filter_files_for_images(files):
    return [v.lower() for v in files if v.lower().endswith('.webp') or v.lower().endswith('.jpg') or v.lower().endswith('.jpeg') or v.lower().endswith('.gif') or v.lower().endswith('.tiff') or v.lower().endswith('.png')]

rootPath = os.path.expanduser('~')
rootPath = os.path.join(rootPath, 'Downloads')

origination_folder = os.path.join(rootPath, 'Images/Original/')
destination_folder = os.path.join(rootPath, 'Images/Upscaled/')
destination_temp = os.path.join(rootPath, 'Images/Temp/')

padding_all_sides = 100
width_4k = 3840
height_4k = 2160

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

if not os.path.exists(origination_folder):
    os.makedirs(origination_folder)

if not os.path.exists(destination_temp):
    os.makedirs(destination_temp)

if os.path.exists(destination_temp + 'main_temp.png'):
    os.remove(destination_temp + 'main_temp.png')
if os.path.exists(destination_temp + 'bg_temp.png'):
    os.remove(destination_temp + 'bg_temp.png')

print("""
version: 1.0.0

This Script will take smaller images, or non 16:9 4k Images, and make them better suited for our 4k videos

Put your images in ~/Downloads/Images/Original  .... I will upscale all the images in this folder for your
If the file in "Original" already exists in "Upscaled" it will be skipped.
SO if you want it run again, delete it from "Upscaled" before starting this
and put the results in /Downloads/Images/Upscaled

""")

images = filter_files_for_images(os.listdir(origination_folder))

padding_all_sides = float(input('How much padding around each side? (0 adds non extra) '))
blur_edges = input('Blur the 4 edges of the image into the background? (y)es / (n)o ')
blur_code = ' '
if blur_edges == 'y':
    blur_code = ' -alpha set -virtual-pixel transparent -channel A  -morphology Distance Euclidean:20,50\! +channel '

for img in images:
    # First let's check if it exists in Upscaled
    imgPath = os.path.join(origination_folder, img)
    futureImg = os.path.splitext(img)[0] + '.jpg'
    if os.path.exists(os.path.join(destination_folder, futureImg)):
        continue
    image = Image.open(imgPath)

    width, height = image.size
    width_original = width
    height_original = height

    print('Image dimensions are ' + str(width) + ' x ' + str(height))
    factor_w = width_4k / width
    factor_h = height_4k / height
    width = width * min(factor_w,factor_h)
    height = height * min(factor_h, factor_w)

    command = 'magick "' + imgPath + '" -interpolative-resize ' + str(round(width,0)) + blur_code + destination_temp + 'main_temp.png'
    print('Image dimensions are ' + str(width) + ' x ' + str(height))
    print(command)
    os.system(command)

    #-blur 0x10
    width = width_original * max(factor_w, factor_h)
    height = height_original * max(factor_h, factor_w)

    final_width = width_4k + 2 * padding_all_sides
    final_height = height_4k + 2 * padding_all_sides

    command = 'magick "' + imgPath + '" -interpolative-resize ' + str(round(width + 2 * padding_all_sides,0)) + ' -blur 0x60 ' + ' -crop ' + str(round(final_width,0)) + 'x' + str(round(final_height,0)) + '+0+0 ' + destination_temp + 'bg_temp.png'
    print(command)
    os.system(command)

    bg_x_offset = 0
    bg_y_offset = 0
    main_x_offset = padding_all_sides
    main_y_offset = padding_all_sides
    width = width_original * min(factor_w,factor_h)
    height = height_original * min(factor_h, factor_w)
    print('h = ' + str(height) + ' w=' + str(width))
    if width / width_4k >= height / height_4k:
        print('width is bigger')
        bg_x_offset = (width - (width_4k + padding_all_sides) / 2)
        main_y_offset = round((height_4k - height) / 2 + padding_all_sides,1)
        print('width = ', str(main_y_offset))
    else:
        bg_y_offset = (height - (height_4k + padding_all_sides)) / 2
        main_x_offset = round((width_4k - width) / 2 + padding_all_sides,1)

    img = os.path.splitext(img)[0] + '.jpg'
    # command = 'magick composite -geometry +' + str(main_x_offset) + '+' + str(main_y_offset) + ' ' + destination_temp + 'main_temp.png -geometry ' + str(width_4k + padding_all_sides) + 'x' + str(height_4k + padding_all_sides) + '-' + str(bg_x_offset) + '+' + str(bg_y_offset) + ' ' + destination_temp + 'bg_temp.png ' + destination_folder + img_filename
    command = 'magick composite -geometry +' + str(main_x_offset) + '+' + str(main_y_offset) + ' ' + destination_temp + 'main_temp.png ' + destination_temp + 'bg_temp.png "' + destination_folder + img +'"'

    print(command)
    os.system(command)

print('Complete! check results at: ' + destination_folder)
