#!/usr/bin/python
# 9/22/2018 - Skeetzo
# 10/10/2018: args overhaul
# 10/20/2018: usability overhaul
# 1/21/2019: upload fix & hashtagging
# 2/3/2019: upload ext fix & tweeting

###### Process ################################
# download mp4 from Google Drive folder @ id  #
# login to OnlyFans                           #
# upload video to OnlyFans                    #
# publish                                     #
#   move mp4 to Google Drive folder @ id      #
# or                                          #
#   trash Google Drive mp4                    #
###############################################

########################################################################################################
##### Dependencies #####################################################################################
# pip install selenium 
########################################################################################################
import random
import os
import shutil
import datetime
import json
import sys
import pathlib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pprint import pprint
########################################################################################################
##### Globals ##########################################################################################
########################################################################################################
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json')
GOOGLE_CREDS = os.path.join(os.path.dirname(os.path.realpath(__file__)),'google_creds.txt')
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
DEBUG = False
DEBUG_SKIP_DOWNLOAD = True
IMAGE_UPLOAD_LIMIT = 6
REMOVE_LOCAL = True
# selenium web browser
BROWSER = None
# backup uploaded content
BACKING_UP = True
# delete uploaded content
DELETING = False
# -v -> video
VIDEO_FILE = False
# -g -> gallery
GALLERY_FOLDER = False
# -i -> image
IMAGE_FILE = False
# Twitter hashtags
HASHTAGGING = False
# -f -> force / ignore upload max wait
FORCE_UPLOAD = False
# -show -> shows window
SHOW_WINDOW = False
# -t -> text
TEXT = None
# -q -> quiet / no tweet
TWEETING = True
def updateDefaults(args):
    for arg in args:
        if arg[0] == "Debug":
            DEBUG = arg[1]
        if arg[0] == "DEBUG_SKIP_DOWNLOAD":
            DEBUG_SKIP_DOWNLOAD = arg[1]
        if arg[0] == "IMAGE_UPLOAD_LIMIT":
            IMAGE_UPLOAD_LIMIT = arg[1]
        if arg[0] == "BACKING_UP":
            BACKING_UP = arg[1]
        if arg[0] == "DELETING":
            DELETING = arg[1]
        if arg[0] == "VIDEO_FILE":
            VIDEO_FILE = arg[1]
        if arg[0] == "GALLERY_FOLDER":
            GALLERY_FOLDER = arg[1]
        if arg[0] == "IMAGE_FILE":
            IMAGE_FILE = arg[1]
        if arg[0] == "HASHTAGGING":
            HASHTAGGING = arg[1]
        if arg[0] == "FORCE_UPLOAD":
            FORCE_UPLOAD = arg[1]
        if arg[0] == "SHOW_WINDOW":
            SHOW_WINDOW = arg[1]
        if arg[0] == "TEXT":
            TEXT = arg[1]
        if arg[0] == "TWEETING":        
            TWEETING = arg[1]
########################################################################################################
##### Args #############################################################################################
########################################################################################################
i = 0
while i < len(sys.argv):
    if '-v' in str(sys.argv[i]):
        VIDEO_FILE = True
    if '-g' in str(sys.argv[i]):
        GALLERY_FOLDER = True
    if '-i' in str(sys.argv[i]):
        IMAGE_FILE = True
    if '-t' in str(sys.argv[i]):
        TEXT = str(sys.argv[i+1])
    if '-d' in str(sys.argv[i]):
        DEBUG = True
    if '-h' in str(sys.argv[i]):
        HASHTAGGING = True
    if '-f' in str(sys.argv[i]):
        FORCE_UPLOAD = True
    if '-show' in str(sys.argv[i]):
        SHOW_WINDOW = True
    if '-q' in str(sys.argv[i]):
        TWEETING = False
    if '-delete' in str(sys.argv[i]):
        DELETING = False
    i += 1

# debugging
def maybePrint(text):
    if DEBUG:
        print(text);
########################################################################################################
##### Config ###########################################################################################
########################################################################################################
with open(CONFIG_FILE) as config_file:    
    config = json.load(config_file)
# maybePrint('Loaded: Config')
########################################################################################################
##### Authenticate Google ##############################################################################
########################################################################################################
# print('Uploading Google Drive content to OnlyFans')
# print('Authenticating Google...')
try:
    # Google Drive folder ids and OnlyFans login
    OnlyFans_USERNAME = config['username']        
    OnlyFans_PASSWORD = config['password']   
    OnlyFans_VIDEOS_FOLDER = config['videos_folder']
    OnlyFans_IMAGES_FOLDER = config['images_folder']
    OnlyFans_GALLERIES_FOLDER = config['galleries_folder']
    OnlyFans_POSTED_FOLDER = config['posted_folder']
    # Google Auth
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile(os.path.join(GOOGLE_CREDS))
    # maybePrint('Loaded: Google Credentials')
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(os.path.join(GOOGLE_CREDS))
    drive = GoogleDrive(gauth)
except:
    print('...Authentication Failure!')
    print('exiting...')
    sys.stdout.flush()
    sys.exit()
# print('...Authentication Success!') 
sys.stdout.flush()
########################################################################################################
##### MENU FUNCTIONS ###################################################################################
########################################################################################################
FOLDER_NAME = None

def all(fileChoice, args):
    updateDefaults(args)
    global GALLERY_FOLDER
    GALLERY_FOLDER = False
    global IMAGE_FILE
    IMAGE_FILE = False
    global VIDEO_FILE
    VIDEO_FILE = False
    if fileChoice == 'image':
        IMAGE_FILE = True
    elif fileChoice == 'gallery':
        GALLERY_FOLDER = True
    elif fileChoice == 'video':
        VIDEO_FILE = True
    main()

def download(fileChoice, args):
    updateDefaults(args)
    if fileChoice == 'image':
        return download_image_()
    elif fileChoice == 'gallery':
        return download_gallery_()
    elif fileChoice == 'video':
        return download_video_()

def download_image_():
    if DEBUG:
        print('Deleting Locals')
        remove_local()
    print('Fetching Content')
    random_file = get_random_image()
    if random_file == None:
        print('Missing Random Image')
        return
    file_name = random_file['title']
    file_path = download_file(random_file)
    if random_file == None:
        print('Missing Random Image')
        return
    if file_path == None:
        print('Missing Random Image: Empty Download')
        return
    return [file_name, file_path]

def download_gallery_():
    if DEBUG:
        print('Deleting Locals')
        remove_local()
    print('Fetching Content')
    random_file = get_random_gallery()
    file_name = random_file['title']
    file_path = download_gallery(random_file)
    if random_file == None:
        print('Missing Random Gallery')
        return
    if file_path == None:
        print('Missing Random Gallery: Empty Download')
        return
    return [file_name, file_path]

def download_video_():
    if DEBUG:
        print('Deleting Locals')
        remove_local()
    print('Fetching Content')
    random_file = get_random_video()
    file_name = random_file['title']
    file_path = download_file(random_file)
    if random_file == None:
        print('Missing Random Video')
        return
    if file_path == None:
        print('Missing Random Video: Empty Download')
        return
    return [file_name, file_path]

def upload(fileChoice, args):
    updateDefaults(args)
    file_name = None
    file_path = None
    for arg in args:
        if arg[0] == "file_name":
            file_name = arg[1]
        if arg[0] == "file_path":
            file_path = arg[1]
    print('file name: '+str(file_name))
    print('file path: '+str(file_path))
    if fileChoice == 'image':
        return upload_image_(file_name, file_path)
    elif fileChoice == 'gallery':
        return upload_gallery_(file_name, file_path)
    elif fileChoice == 'video':
        return upload_video_(file_name, file_path)
    print('Upload Complete')
    sys.stdout.flush()
    #################################################
    if REMOVE_LOCAL:
        print('Cleaning Up Files')
        remove_local()
    if BACKING_UP:
        print('Backing Up')
        move_file(random_file)
    if DELETING:
        print('Deleting')
        delete_file(random_file)
    sys.stdout.flush()

def upload_image_(file_name, file_path):
    print('Accessing OnlyFans')
    log_into_OnlyFans()
    upload_file_to_OnlyFans(file_name, file_path)
    print('Upload Complete')
    return

def upload_gallery_(file_name, file_path):
    print('Accessing OnlyFans')
    log_into_OnlyFans()
    upload_directory_to_OnlyFans(file_name, file_path)
    print('Upload Complete')
    return

def upload_video_(file_name, file_path):
    print('Accessing OnlyFans')
    log_into_OnlyFans()
    upload_file_to_OnlyFans(file_name, file_path)
    print('Upload Complete')
    return

def backup(fileChoice, args):
    updateDefaults(args)
    print("Missing Feature: Backup")
    return


########################################################################################################
##### FUNCTIONS ########################################################################################
########################################################################################################
# Downloads random video from Google Drive
def get_random_video():
    print('Downloading Random Video')
    random_folders = drive.ListFile({'q': "'"+OnlyFans_VIDEOS_FOLDER+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
    video_list = [];
    random_video = None;
    # print('random folders: '+str(random_folders))
    print('randomizing folder...')
    for folder in random_folders:
        random_folder_folder = random.choice(random_folders)
        video_list_tmp = drive.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and mimeType contains 'video/mp4'"}).GetList()
        if len(video_list_tmp)==0:
           maybePrint('skipping empty folder: '+folder['title'])
        else:
            maybePrint('folder found: '+folder['title'])
            video_list.append(folder)
    if len(video_list)==0:
        print('No video file found!')
        return
    # print('video list: '+str(video_list))
    random_video = random.choice(video_list)
    global FOLDER_NAME
    FOLDER_NAME = random_video['title'];
    print('Random Folder: '+random_video['title'])
    random_video = drive.ListFile({'q': "'"+random_video['id']+"' in parents and trashed=false and mimeType contains 'video/mp4'"}).GetList()
    random_video = random.choice(random_video)
    print('Random Video: '+random_video['title'])
    return random_video

# Downloads random image from Google Drive
def get_random_image():
    print('Downloading Random Image')
    random_folders = drive.ListFile({'q': "'"+OnlyFans_IMAGES_FOLDER+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
    images_list = [];
    random_image = None;
    for folder in random_folders:
        random_folder_folder = random.choice(random_folders)
        images_list = drive.ListFile({'q': "'"+random_folder_folder['id']+"' in parents and trashed=false and mimeType contains 'image/jpeg'"}).GetList()      
        if len(images_list)==0:
            maybePrint('skipping empty folder: '+random_folder_folder['title'])
        elif len(images_list)>0:
            # print('- folder found: '+images_list['title'])
            global FOLDER_NAME
            FOLDER_NAME = random_folder_folder['title']
            maybePrint('folder name: '+FOLDER_NAME)
            random_image = random.choice(images_list)
            maybePrint('random image: '+random_image['title'])
            return random_image
    if len(images_list)==0:
        print('No image file found!')
        return
    random_image = random.choice(images_list)
    print('Random Image: '+random_image['title'])
    return random_image

# Downloads random gallery from Google Drive
def get_random_gallery():
    print('Downloading Random Gallery')
    random_folders = drive.ListFile({'q': "'"+OnlyFans_GALLERIES_FOLDER+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
    gallery_list = [];
    random_gallery = None;
    for folder in random_folders:
        random_folder_folder = random.choice(random_folders)
        gallery_list = drive.ListFile({'q': "'"+random_folder_folder['id']+"' in parents and trashed=false and mimeType contains 'application/vnd.google-apps.folder'"}).GetList()
        if len(gallery_list)==0:
            maybePrint('- skipping empty folder: '+random_folder_folder['title'])
        elif len(gallery_list)>0:
            global FOLDER_NAME
            FOLDER_NAME = random_folder_folder['title']
            maybePrint('folder name: '+FOLDER_NAME)
            random_gallery = random.choice(gallery_list)
            maybePrint('random gallery: '+random_gallery['title'])
            return random_gallery
    if len(gallery_list)==0:
        print('No gallery folders found!')
        return
    random_gallery = random.choice(gallery_list)
    print('Random Gallery: '+random_gallery['title'])
    return random_gallery

# Download File
def download_file(file):
    print('Downloading Video...')
    # mkdir /tmp
    path = os.getcwd()
    path += '/tmp'
    tmp = path
    if not os.path.exists(path):
        os.mkdir(path)
    # download file
    ext = os.path.splitext(file['title'])[1]
    if not ext:
        ext = '.mp4'
        maybePrint('ext (default): '+ext)
    else:
        maybePrint('ext: '+ext)
    path += "/uploadMe"+ext
    maybePrint('path: '+path)
    file.GetContentFile(path)
    if os.path.getsize(path) == 0:
        maybePrint('size: '+str(os.path.getsize(path)))
        print('Download Failure')
        return None
    print('Download Complete')
    return path

# Download Gallery
def download_gallery(folder):
    print('Downloading Gallery...')
    # mkdir /tmp
    path = os.getcwd()
    path += '/tmp'+"/"+str(folder['title'])
    maybePrint('path: '+path)
    if not os.path.exists(path):
        os.makedirs(path)
    # download folder
    file_list = drive.ListFile({'q': "'"+folder['id']+"' in parents and trashed=false and mimeType contains 'image/jpeg'"}).GetList()
    folder_size = len(file_list)
    maybePrint('Folder size: '+str(folder_size))
    maybePrint('Upload limit: '+str(IMAGE_UPLOAD_LIMIT))
    file_list_random = []
    for x in range(IMAGE_UPLOAD_LIMIT):
        random_file = random.choice(file_list)
        file_list.remove(random_file)
        file_list_random.append(random_file)
    i = 1
    for file in sorted(file_list_random, key = lambda x: x['title']):
        print('Downloading {} from GDrive ({}/{})'.format(file['title'], i, folder_size))
        maybePrint('filePath: '+path+"/"+str(file['title']))
        file.GetContentFile(path+"/"+str(file['title']))
        i+=1
    print('Download Complete')
    return path

# Upload to OnlyFans
def log_into_OnlyFans():
    print('Logging into OnlyFans...')
    options = webdriver.ChromeOptions()
    if not SHOW_WINDOW:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.setExperimentalOption('useAutomationExtension', false);
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    global BROWSER
    BROWSER = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)
    BROWSER.implicitly_wait(10) # seconds
    BROWSER.set_page_load_timeout(1200)
    BROWSER.get(('https://onlyfans.com'))
    # login via Twitter
    twitter = BROWSER.find_element_by_xpath('//a[@class="btn btn-default btn-block btn-lg btn-twitter"]').click()
    # fill in username
    username = BROWSER.find_element_by_xpath('//input[@id="username_or_email"]').send_keys(OnlyFans_USERNAME)
    # fill in password and hit the login button 
    password = BROWSER.find_element_by_xpath('//input[@id="password"]')
    password.send_keys(OnlyFans_PASSWORD)
    password.send_keys(Keys.ENTER)
    print('Login Success')
    return

# Uploads a file to OnlyFans
def upload_file_to_OnlyFans(fileName, path):
    fileName = os.path.splitext(fileName)[0]
    print('Uploading: '+fileName)
    # maybePrint('path: '+path)
    global FOLDER_NAME
    if HASHTAGGING:
        postText = str(fileName)+" #"+" #".join(FOLDER_NAME.split(' '))
    else:
        postText = FOLDER_NAME+" "+fileName
    maybePrint('text: '+postText)
    global BROWSER
    BROWSER.find_element_by_id("new_post_text_input").send_keys(postText)
    BROWSER.find_element_by_id("fileupload_photo").send_keys(path)
    if not TWEETING:
        WebDriverWait(BROWSER, 600, poll_frequency=10).until(EC.element_to_be_clickable((By.XPATH, '//label[@for="new_post_tweet_send"]'))).click()
    maxUploadCount = 12 # 2 hours max attempt time
    i = 0
    while True:
        try:
            WebDriverWait(BROWSER, 600, poll_frequency=10).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and @class="btn btn-xs btn-default send_post_button"]')))
            if DEBUG:
                print('skipping OnlyFans upload')
                return
            send = WebDriverWait(BROWSER, 600, poll_frequency=10).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and @class="btn btn-xs btn-default send_post_button"]'))).click()
            break
        except Exception as e:
            print('uploading...')
            i+=1
            if i == maxUploadCount and FORCE_UPLOAD is not True:
                print('max upload wait reached, breaking..')
                break
    print('File Uploaded Successfully')
    return

# Uploads a folder to OnlyFans
def upload_directory_to_OnlyFans(dirName, path):
    global FOLDER_NAME
    if HASHTAGGING:
        postText = str(dirName)+" #"+" #".join(FOLDER_NAME.split(' '))
    else:    
        postText = str(FOLDER_NAME)+" "+str(dirName)
    print('Uploading: '+postText)
    # maybePrint('path: '+path)
    files_path = []
    for file in pathlib.Path(path).iterdir():  
        files_path.append(str(file))
    maybePrint('files: '+str(files_path))
    global BROWSER
    BROWSER.find_element_by_id("new_post_text_input").send_keys(postText)
    if not TWEETING:
        WebDriverWait(BROWSER, 600, poll_frequency=10).until(EC.element_to_be_clickable((By.XPATH, '//label[@for="new_post_tweet_send"]'))).click()
    for file in files_path:
        maybePrint('uploading: '+str(file))
        BROWSER.find_element_by_id("fileupload_photo").send_keys(file)
        WebDriverWait(BROWSER, 600).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and @class="btn btn-xs btn-default send_post_button"]')))
    if DEBUG:
        print('skipping OnlyFans upload')
        return
    send = WebDriverWait(BROWSER, 600).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and @class="btn btn-xs btn-default send_post_button"]'))).click()
    print('Directory Uploaded Successfully')
    return

# Deletes local file
def remove_local():
    print('Deleting Local File(s)')
    # delete /tmp
    tmp = os.getcwd()
    tmp += '/tmp'
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
        print('Local File(s) Removed')
        return
    else:
        print('Local Files Not Found')
        return

# Deletes online file
def delete_file(file):
    print('Trashing Google Video')
    if DEBUG:
        print('skipping Google delete')
        return
    file.Trash()
    print('Google Video Trashed')
    return

# Archives posted file
def move_file(file):
    print('Archiving Google Video')
    if DEBUG:
        print('skipping Google archive')
        return
    file['parents'] = [{"kind": "drive#fileLink", "id": OnlyFans_POSTED_FOLDER}]
    file.Upload()
    print('Google Video Archived')
    return
########################################################################################################
###### START ###########################################################################################
########################################################################################################
# if DEBUG_SKIP_DOWNLOAD:
    # return print('- Skipping Download -')
########################################################################################################
def main():
    if DEBUG:
        print('0/3 : Deleting Locals')
        remove_local()
    print('1/3 : Fetching Content')
    RANDOM_FILE = None
    if GALLERY_FOLDER:
        RANDOM_FILE = get_random_gallery()
        FILE_NAME = RANDOM_FILE['title']
        FILE_PATH = download_gallery(RANDOM_FILE)
    elif VIDEO_FILE:
        RANDOM_FILE = get_random_video()
        FILE_NAME = RANDOM_FILE['title']
        FILE_PATH = download_file(RANDOM_FILE)
    elif IMAGE_FILE:
        RANDOM_FILE = get_random_image()
        FILE_NAME = RANDOM_FILE['title']
        FILE_PATH = download_file(RANDOM_FILE)
    else:
        print('Missing Args!')
        sys.stdout.flush()
        sys.exit()
    if RANDOM_FILE == None:
        print('Missing Random File / Directory!')
        sys.stdout.flush()
        sys.exit()
    if FILE_PATH == None:
        print('Missing Random Video: Empty Download')
        sys.stdout.flush()
        sys.exit()
    sys.stdout.flush()
    #################################################
    print('2/3 : Accessing OnlyFans')
    log_into_OnlyFans()
    sys.stdout.flush()
    if GALLERY_FOLDER:
        upload_directory_to_OnlyFans(FILE_NAME, FILE_PATH)
    elif VIDEO_FILE or IMAGE_FILE:
        upload_file_to_OnlyFans(FILE_NAME, FILE_PATH)
    else:
        print('Missing OnlyFans Instructions!')
        sys.stdout.flush()
        sys.exit()
    print('Upload Complete')
    sys.stdout.flush()
    #################################################
    print('3/3 : Cleaning Up Files')
    remove_local()
    if BACKING_UP:
        move_file(RANDOM_FILE)
    else:
        delete_file(RANDOM_FILE)
    print('Files Cleaned ')
    sys.stdout.flush()
    #################################################
    print('Google Drive to OnlyFans Upload Complete!')
    sys.stdout.flush()
    return

if __name__ == "__main__":
    os.system('clear')
    print('OnlySnarf Settings:')
    print(' - DEBUG = '+str(DEBUG))
    print(' - BACKING_UP = '+str(BACKING_UP))
    print(' - HASHTAGGING = '+str(HASHTAGGING))
    print(' - TWEETING = '+str(TWEETING))
    print(' - FORCE_UPLOAD = '+str(FORCE_UPLOAD))
    main()