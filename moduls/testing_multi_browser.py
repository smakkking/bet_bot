import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool, cpu_count
import os
 
 
lst = [
    ('http://www.google.com', r'Profile 3'),
    ('http://www.mail.ru', r'Profile 1')]
 
# РЕШЕНИЕ ДЛЯ ЗАПУСКА МНОЖЕСТВА БРАУЗЕРОВ С АВТОРИЗОВАННЫМИ ПРОФИЛЯМИ
def selen(data):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1024x768")
    chrome_options.add_argument('--profile-directory=' + data[1])
    chrome_options.add_argument(r"--user-data-dir=C:\Users\user1\AppData\Local\Google\Chrome" + r'\\' + data[1])
    driver = webdriver.Chrome(executable_path=os.getcwd() + r'\chromedriver.exe', chrome_options=chrome_options)
    driver.get(data[0])
    time.sleep(5)
    driver.quit()

 
if __name__ == '__main__':
    import manage_file
    browser = manage_file.create_webdriver()
    browser.get('https://new.parimatch.ru')
    time.sleep(40)
    
    browser.close()
    browser.quit()
    


