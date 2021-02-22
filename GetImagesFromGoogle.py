
import os, subprocess, platform, PIL, shutil, sys, urllib, requests, re, selenium, time, io
from selenium import webdriver
from os import listdir
from os.path import isfile, join
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
import urllib.parse as urlparse

#REGEX: (?i)\[\"http.*\.(jpg|png|tiff|jpeg|svg).*\",[0-9].*,[0-9].*\](\n|.*)*?}

def generate_sections_of_url(url):
    path = urlparse.urlparse(url).path
    sections = []; temp = "";
    while path != '/':
        temp = os.path.split(path)
        path = temp[0]
        sections.append(temp[1])
    return sections

def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&biw=1851&bih=981&gs_l=img"
    # search_url = 'https://www.google.com/search?q=%7Bq%7D&tbm=isch&safe=off&tbs=isz:l&hl=en&sa=X&ved=0CAEQpwVqFwoTCIjuj8eT_O4CFQAAAAAdAAAAABAC&biw=1851&bih=981'

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

def getUniqueFilename(searchTerm:str, folder:str, url:str):
    index = 1
    filename = searchTerm.replace(" ", "_") + '_' + str(index) + ".jpg"
    while os.path.isfile(os.path.join(folder,filename)):
        index += 1
        filename = searchTerm.replace(" ", "_") + '_' + str(index) + ".jpg"
    return filename

def persist_image(folder_path:str,url:str, searchTerm:str):
    finalReport = ''
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")
    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        uniqueFileName = getUniqueFilename(searchTerm, folder_path, url)
        file_path = os.path.join(folder_path,uniqueFileName)
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
        finalReport = uniqueFileName + ',' + searchTerm + ',' + url + '\n'
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")
    return finalReport

def filter_files_for_images(files):
    return [v.lower() for v in files if v.lower().endswith('.webp') or v.lower().endswith('.jpg') or v.lower().endswith('.jpeg') or v.lower().endswith('.gif') or v.lower().endswith('.tiff') or v.lower().endswith('.png')]

def search_and_download(search_term:str,target_folder='./images',number_images=100):
    # target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))
    reportObject = open(report_path, "a")
    read = open(report_path, "r")
    finalReport = read.read()

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driverPath) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=.5)

    for elem in res:

        if elem in finalReport:
            print("This Image is already downloaded skipping...\nelem\n")
        else:
            finalReport += persist_image(target_folder,elem, search_term)
            reportObject.write(finalReport)
    reportObject.close()

rootPath = os.path.expanduser('~')
driverPath = os.path.join(rootPath, 'Code/chromeDriver/chromedriver')
rootPath = os.path.join(rootPath, 'Downloads/ImagesResearcher')
projectPath = rootPath
if not os.path.exists(rootPath):
    os.makedirs(rootPath)


padding_all_sides = 100
width_4k = 3840
height_4k = 2160

print("""
version: 1.0.0

'run :
pip install requests
pip install selenium
pip install beautifulsoup4

install chrome driver at ~/Code/chromeDriver/chromedriver

If you see:
“chromedriver” can’t be opened because Apple cannot check it for malicious software."
Then go settings -> Security & Privacy -> General -> ALlow Anyway

These are the Active Image Research Projects you have now...

""")

projects = os.listdir(rootPath)
if '.DS_Store' in projects:
    projects.remove('.DS_Store')
projectIndex = 1
for project in projects:
    print('['+ str(projectIndex) + '] ' + project)
    projectIndex += 1
print('[' + str(projectIndex) + ']' + ' Start New Image Research Project')


type = int(input('\n\nWhich Image Research Project do you want to run? :'))
isNew = False
if type > len(projects):
    projectName = str.title(input('\n\nWhat is the name of this Image Research Project (example: howard hughes) :'))
    isNew = True
elif type > 0 and type <= len(projects):
    projectName = projects[type - 1]
else:
    print("Invalid Selection - Breaking")
    sys.exit()

projectPath = os.path.join(rootPath, projectName)
report_folder = os.path.join(projectPath, 'Report/')
report_path = os.path.join(report_folder, 'report.txt')
destination_folder = os.path.join(projectPath, 'Images/')
temp_images = os.path.join(projectPath, 'Temp/')
destination_temp = os.path.join(projectPath, 'Progress/')
if isNew:
    os.makedirs(projectPath)
    os.makedirs(report_folder)
    os.makedirs(temp_images)
    os.makedirs(destination_folder)
    os.makedirs(destination_temp)

searchTerm = input('\n\n[1] Use \'' + projectName +'\' as search term on Google?\n[2] Custom search term\n\n')
if int(searchTerm) == 2:
    searchTerm = input('\n\nEnter your Search Term: \n use a common separated list if you want multiple passes \n (example: mario, luigi, bowser)\n')
else:
    searchTerm = projectName
print(searchTerm)
searchTermEncoded = urllib.parse.quote(searchTerm)
numImages = int(input('\n\nHow many Images Should I Download? \n\n'))
# padding_all_sides = float(input('How much padding around each side? (0 adds non extra) '))
# blur_edges = input('Blur the 4 edges of the image into the background? (y)es / (n)o ')
padding_all_sides = 100
blur_edges = 'y'
searchComponents = searchTerm.split(',')
for searchTerm in searchComponents:

    search_and_download(searchTerm, temp_images, numImages)

    # Next for the upscaling business


    images = filter_files_for_images(os.listdir(temp_images))
    blur_code = ' '
    if blur_edges == 'y':
        blur_code = ' -alpha set -virtual-pixel transparent -channel A  -morphology Distance Euclidean:20,50\! +channel '

    for img in images:
        # First let's check if it exists in Upscaled
        imgPath = os.path.join(temp_images, img)
        print(imgPath)
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

        command = 'magick "' + imgPath + '" -interpolative-resize ' + str(round(width,0)) + blur_code + '"' + destination_temp + 'main_temp.png"'
        print('Image dimensions are ' + str(width) + ' x ' + str(height))
        print(command)
        os.system(command)

        #-blur 0x10
        width = width_original * max(factor_w, factor_h)
        height = height_original * max(factor_h, factor_w)

        final_width = width_4k + 2 * padding_all_sides
        final_height = height_4k + 2 * padding_all_sides

        command = 'magick "' + imgPath + '" -interpolative-resize ' + str(round(width + 2 * padding_all_sides,0)) + ' -blur 0x60 ' + ' -crop ' + str(round(final_width,0)) + 'x' + str(round(final_height,0)) + '+0+0 "' + destination_temp + 'bg_temp.png"'
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
        command = 'magick composite -geometry +' + str(main_x_offset) + '+' + str(main_y_offset) + ' \'' + destination_temp + 'main_temp.png\' \'' + destination_temp + 'bg_temp.png\' \'' + destination_folder + img +'\''

        print(command)
        os.system(command)

    print('Completed :' + searchTerm)

print("ALL DONE!")
