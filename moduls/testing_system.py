from selenium import webdriver
from datetime import datetime
import sys
import time
from datetime import datetime
import os

import manage_file

opt = webdriver.ChromeOptions()
opt.add_argument(r'user-data-dir=C:\Users\user1\AppData\Local\Google\Chrome\User Data')
opt.add_argument('--profile-directory=Profile 1') # возможно заменить на другой профиль с названием Profile 1
arg = {'chrome.page.settings.userAgent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
BROWSER = webdriver.Chrome(executable_path=os.getcwd() + '\\chromedriver.exe', options=opt, desired_capabilities=arg)



BROWSER.close()
sys.exit()
