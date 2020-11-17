from moduls.bet_manage import create_webdriver, get_html_with_browser
from manage import ALL_POSTS_JSON_PATH

def do_stuff(url):
    browser = create_webdriver(user_id=url[1])
    get_html_with_browser(browser, url[0])
    browser.close()
    browser.quit()
    
from multiprocessing import Pool

if __name__ == "__main__" :
    urls = [
        ['https://vk.com/akademiya_stavki_csgo', '0'],
        ['https://vk.com/akademiya_stavki_csgo', '1'],
    ]

    with Pool(processes=len(urls)) as pool:
        pool.map(do_stuff, urls)

