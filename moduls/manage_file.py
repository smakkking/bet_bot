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


class Stavka :
    def __init__(self, bet_dict) :
        for key in bet_dict :
            exec('self.' + str(key) + '=bet_dict[key]')
            
class Coupon() :
    def __init__(self, type_x='ordn') :
        self.type = type_x
        self.bets = []
    def add_bet(self, bet) :
        self.bets.append(Stavka(bet))
    def change_type(self, new_type) :
        self.type = new_type

class GroupPost() :
    def __init__(self, text='', photo_list=[]) :
        self.text = text
        self.photo_list = photo_list

    def add_photo(self, photo) :
        self.photo_list.append(photo)

    def __str__(self) :
        return str(dict([('text', self.text), ('photo_list', self.photo_list)]))
        
    def get_last_post(self, BROWSER, WALL_GET_url) :
        get_html_with_browser(BROWSER, WALL_GET_url, 4)
        # первый пост
        first_post = BROWSER.find_element_by_id('page_wall_posts').find_element_by_tag_name('div').find_element_by_class_name('wall_text')
        # получаем текст
        self.text = first_post.find_elements_by_tag_name('div')[1].text
        # получаем список фото
        photos_click_dom = first_post.find_elements_by_tag_name('div')[2].find_elements_by_tag_name('a')
        # тест
        try :
            for item in photos_click_dom :
                item.click()
                time.sleep(0.5)
                self.add_photo(BROWSER.find_element_by_xpath('//*[@id="pv_photo"]/img').get_attribute('src'))
                BROWSER.find_element_by_class_name('pv_close_btn').click() # нужно закрыть фото
                time.sleep(0.5)  
        except common.exceptions.NoSuchElementException:
            pass

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
    soup = BeautifulSoup(get_html_with_browser(BROWSER, url, 4), 'html.parser')
    items2 = soup.find_all('div', class_='CbirOcr-TextBlock CbirOcr-TextBlock_level_text')
    text = []
    for item in items2 :
       text.append(item.text)
    return text

def create_webdriver() :
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36")
    opts.add_argument(r'user-data-dir=C:\Users\user1\AppData\Local\Google\Chrome\bet_data')
    opts.add_argument('--profile-directory=Profile 1') # возможно заменить на другой профиль с названием Default
    obj = webdriver.Chrome(executable_path=os.getcwd() + '\\chromedriver.exe', options=opts)
    return obj
    


if __name__ == "__main__":
    browser = create_webdriver()
    try :
        pass
    finally :
        browser.close()
        browser.quit()