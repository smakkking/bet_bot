# общие модули
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium import common
import sys
import time
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# конкретные модули

WAIT_TIME = 4 # время ожидания прогрузки страницы в секундах

def Error(code) :
    if code == 0x1 :
        # не обработан правильно: может попасться текст не ставки, но в нем будет 6 строк 
        print('text is not bet')
    elif code == 0x2 :
        print('no match found')
    elif code == 0x3 :
        print('no outcome found')
    elif code == 0x4 :
        print('no working case')

def get_html(url, params=None):
    return requests.get(url, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}, params=params).text

def get_html_with_browser(BROWSER, url, sec=0, scrolls=0) :
    if url != 'none' :
        BROWSER.get(url)
    time.sleep(sec // 2)
    if scrolls > 1 :
        for i in range(scrolls) :
            BROWSER.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(1)
    time.sleep(sec // 2)
    return BROWSER.page_source

def get_text_from_image(BROWSER, url):
    url = url.replace('/', '%2F')
    url = url.replace(':', '%3A')
    url = 'https://yandex.ru/images/search?url=' + url + '&rpt=imageview&from=tabbar' # создание рабочей ссылки
    soup = BeautifulSoup(get_html_with_browser(BROWSER, url, WAIT_TIME), 'html.parser')
    items2 = soup.find_all('div', class_='CbirOcr-TextBlock CbirOcr-TextBlock_level_text')
    text = []
    for item in items2 :
       text.append(item.text)
    return text

def renew(BROWSER, url) :
    BROWSER.get(url)

def create_webdriver() :
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36")
    opts.add_argument(r'user-data-dir=C:\Users\user1\AppData\Local\Google\Chrome\bet_data')
    opts.add_argument('--profile-directory=Profile 1') # возможно заменить на другой профиль с названием Default
    obj = webdriver.Chrome(executable_path=os.getcwd() + '\\chromedriver.exe', options=opts)
    return obj
    
def get_last_post(BROWSER, WALL_GET_url) :
    get_html_with_browser(BROWSER, WALL_GET_url, WAIT_TIME)
    result = {
        'text' : '',
        'list_of_photo' : [],
    }
    # первый пост
    first_post = BROWSER.find_element_by_id('page_wall_posts').find_element_by_tag_name('div').find_element_by_class_name('wall_text')
    # получаем текст
    result['text'] = first_post.find_elements_by_tag_name('div')[1].text
    # получаем список фото
    photos_click_dom = first_post.find_elements_by_tag_name('div')[2].find_elements_by_tag_name('a')
    # тест
    try :
        for item in photos_click_dom :
            item.click()
            time.sleep(0.5)
            result['list_of_photo'].append(BROWSER.find_element_by_xpath('//*[@id="pv_photo"]/img').get_attribute('src'))
            BROWSER.find_element_by_class_name('pv_close_btn').click() # нужно закрыть фото
            time.sleep(0.5)  
    except common.exceptions.NoSuchElementException:
        pass
    return result

if __name__ == "__main__":
    browser = create_webdriver()
    try :
        print(get_last_post(browser, 'https://vk.com/rushbet.tips'))
        time.sleep(10)
    finally :
        browser.close()
        browser.quit()